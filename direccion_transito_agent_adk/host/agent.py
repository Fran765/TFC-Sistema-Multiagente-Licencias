import asyncio
import json
import logging
import os
import uuid
import httpx
import nest_asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterable, List
from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from .tools import (
    verificar_antecedentes_nacionales,
    gestionar_turnos_clases_examenes,
    validar_asistencia,
    validar_examen_practico,
    carga_nacional,
)
from .remote_agent_connection import RemoteAgentConnections

logger = logging.getLogger(__name__)

load_dotenv()
nest_asyncio.apply()

INSTRUCTION_PATH = Path(__file__).parent / "instruction.md"
ROOT_INSTRUCTION = INSTRUCTION_PATH.read_text(encoding="utf-8")


class DireccionTransitoAgent:
    """The Direccion Transito agent."""

    def __init__(
        self,
    ):
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ""
        self._agent = self.create_agent()
        self._user_id = "host_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def _async_init_components(self, remote_agent_addresses: List[str]):
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(client, address)
                try:
                    card = await card_resolver.get_agent_card()
                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                except httpx.ConnectError as e:
                    logger.error(f"Failed to get agent card from {address}: {e}")
                except Exception as e:
                    logger.error(f"Failed to initialize connection for {address}: {e}")

        agents_list = []
        for card in self.cards.values():
            skills_info = [
                f"- Skill: {skill.name}, Description: {skill.description}"
                for skill in card.skills
            ]
            agent_str = f"AGENTE: {card.name}\nDESCRIPCION: {card.description}\nHABILIDADES:\n" + "\n".join(skills_info)
            
            agents_list.append(agent_str)
        
        logger.info("Connected agents: %s", len(agents_list))
        self.agents = "\n".join(agents_list) if agents_list else "No friends found"

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: List[str],
    ):
        instance = cls()
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        return Agent(
            model="gemini-2.5-pro",
            name="DireccionTransito_Orquestador",
            instruction=self.root_instruction,
            description="Agente orquestador de la Dirección de Tránsito que coordina "
            "el proceso completo de obtención de licencias de conducir.",
            tools=[
                self.send_message,
                verificar_antecedentes_nacionales,
                gestionar_turnos_clases_examenes,
                validar_asistencia,
                validar_examen_practico,
                carga_nacional,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        return f"{ROOT_INSTRUCTION}\n\n**Fecha Actual:** {fecha_actual} \n\n**AGENTES DISPONIBLES EN LA RED:**\n{self.agents}"

    async def stream(
        self, query: str, session_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        """
        Streams the agent's response to a given query.
        """
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response():
                response = ""
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    response = "\n".join(
                        [p.text for p in event.content.parts if p.text]
                    )
                yield {
                    "is_task_complete": True,
                    "content": response,
                }
            else:
                yield {
                    "is_task_complete": False,
                    "updates": "The host agent is thinking...",
                }

    async def send_message(self, agent_name: str, task: str, tool_context: ToolContext):
        """Sends a task to a remote friend agent."""
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f"Agent {agent_name} not found")
        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(f"Client not available for {agent_name}")

        state = tool_context.state
        task_id = state.get("task_id", str(uuid.uuid4()))
        context_id = state.get("context_id", str(uuid.uuid4()))
        message_id = str(uuid.uuid4())

        payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": task}],
                "messageId": message_id,
                "taskId": task_id,
                "contextId": context_id,
            },
        }

        message_request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )
        send_response: SendMessageResponse = await client.send_message(message_request)
        logger.debug("Send response: %s", send_response)

        if not isinstance(
            send_response.root, SendMessageSuccessResponse
        ) or not isinstance(send_response.root.result, Task):
            logger.warning(
                "Received a non-success or non-task response. Cannot proceed."
            )
            return

        response_content = send_response.root.model_dump_json(exclude_none=True)
        json_content = json.loads(response_content)

        resp_text = ""
        if json_content.get("result", {}).get("artifacts"):
            for artifact in json_content["result"]["artifacts"]:
                for part in artifact.get("parts", []):
                    if "text" in part:
                        resp_text += part.get("text", "")

        if not resp_text:
            logger.error("El agente remoto no devolvió contenido de texto.")
            return "ERROR: El agente no devolvió ninguna respuesta."
        
        try:
            clean_text = resp_text.strip("` \n")
            if clean_text.startswith("json"):
                 clean_text = clean_text[4:].strip()

            agent_response = json.loads(clean_text)

            status = agent_response.get("status", "unknown")
            message = agent_response.get("message", "Sin mensaje especificado.")

            extra_data = agent_response.get("data")

            data_context = ""
            if extra_data:
                data_context = f" | Datos del agente: {json.dumps(extra_data, ensure_ascii=False)}"

            if status == "input_required":
                return f"🛑 EL AGENTE REQUIERE MÁS DATOS: {message}"
            
            elif status == "completed":
                return f"✅ TAREA COMPLETADA. Mensaje: {message}{data_context}"
            
            elif status == "error":
                return f"❌ ERROR EN EL AGENTE REMOTO: {message}{data_context}"
            
            else:
                # Si el agente devolvió un JSON pero no siguió el contrato (no tiene status)
                return f"✅ RESPUESTA DEL AGENTE: {message}{data_context}"
            
        except json.JSONDecodeError:
            logger.debug("La respuesta no es JSON. Tratándola como texto plano.")
            return f"RESPUESTA DEL AGENTE: {resp_text}"


def _get_initialized_host_agent_sync():
    """Synchronously creates and initializes the HostAgent."""

    async def _async_main():
        # Hardcoded URLs for the colaboration agents
        colaboration_agents_urls = [
            "http://localhost:10002",  # Centro Salud Agent
            "http://localhost:10003",  # ANSES Agent
            "http://localhost:10004",  # CeNAT Agent
        ]

        logger.info("Initializing host agent")
        hosting_agent_instance = await DireccionTransitoAgent.create(
            remote_agent_addresses=colaboration_agents_urls
        )
        logger.info("DireccionTransitoAgent initialized")
        return hosting_agent_instance.create_agent()

    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            logger.warning(
                "Could not initialize DireccionTransitoAgent with asyncio.run(): %s. "
                "Consider initializing DireccionTransitoAgent within an async function.",
                e,
            )
        else:
            raise


root_agent = _get_initialized_host_agent_sync()
