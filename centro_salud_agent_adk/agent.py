from datetime import date
from pathlib import Path
from typing import Any, AsyncIterable

from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from tools import (
    disponibilidad,
    generar_boleta_pago,
    validar_pago_reservar_turno,
    obtener_resultado_medico,
)

INSTRUCTION_PATH = Path(__file__).parent / "instruction.md"
ROOT_INSTRUCTION = INSTRUCTION_PATH.read_text(encoding="utf-8")


class CentroSaludAgent:
    SUPPORTED_CONTENT_TYPES = ["text/plain"]

    def __init__(self):
        self._agent = self.create_agent()
        self._user_id = "centro_salud_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def create_agent(self) -> Agent:
        return Agent(
            model="gemini-2.5-flash-lite",
            name="CentroSalud_Agent",
            instruction=self.root_instruction,
            description="Agente del centro médico autorizado para emitir certificados de aptitud física.",
            tools=[
                disponibilidad,
                generar_boleta_pago,
                validar_pago_reservar_turno,
                obtener_resultado_medico,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        return ROOT_INSTRUCTION

    async def stream(
        self, query: str, session_id: str
    ) -> AsyncIterable[dict[str, Any]]:
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
                yield {"is_task_complete": True, "content": response}
            else:
                yield {"is_task_complete": False, "updates": "Procesando..."}


def create_agent():
    return CentroSaludAgent()
