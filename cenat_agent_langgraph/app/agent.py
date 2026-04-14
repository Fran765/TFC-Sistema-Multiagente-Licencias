from collections.abc import AsyncIterable
from datetime import date
from pathlib import Path
from typing import Any, Literal
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from .tools.boletas_service import BoletaService
import logging

logger = logging.getLogger(__name__)

memory = MemorySaver()

INSTRUCTION_PATH = Path(__file__).parent / "instruction.md"
SYSTEM_INSTRUCTION = INSTRUCTION_PATH.read_text(encoding="utf-8")

boleta_service = BoletaService()


class GenerarBoletaInput(BaseModel):
    dni: str = Field(..., description="Número de documento de identidad.")
    nombre: str = Field(..., description="Nombre completo.")
    apellido: str = Field(..., description="Apellido.")

@tool(args_schema=GenerarBoletaInput)
def generar_boleta_cenat(dni: str, nombre: str, apellido: str) -> str:
    """Genera una boleta del Certificado Nacional de Antecedentes de Tránsito (CeNAT)."""
    if not dni or not nombre or not apellido:
        return "Error: DNI, nombre y apellido son requeridos."

    boleta = boleta_service.generar(dni, nombre, apellido)
    return (
        f"Boleta generada exitosamente.\n"
        f"Código de pago: {boleta['codigo_pago']}\n"
        f"Monto: ${boleta['monto']}\n"
        f"Estado: {boleta['estado']}"
    )


class CertificarPagoInput(BaseModel):
    codigo_pago: str = Field(..., description="Código de pago de la boleta.")

@tool(args_schema=CertificarPagoInput)
def certificar_pago(codigo_pago: str) -> str:
    """Certifica si el pago de la boleta CeNAT fue acreditado."""
    if not codigo_pago:
        return "Error: Código de pago es requerido."

    resultado = boleta_service.certificar_pago(codigo_pago)
    if resultado is None:
        return "Error: Boleta no encontrada. Debe generar la boleta primero."

    return f"Pago acreditado.\nCódigo: {codigo_pago}\nEstado: pagado"


class ResponseFormat(BaseModel):
    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str


class CenatAgent:
    """Agente del CeNAT para gestionar certificados de antecedentes de tránsito."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.tools = [generar_boleta_cenat, certificar_pago]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=ResponseFormat,
        )

    def invoke(self, query: str, context_id: str) -> dict[str, Any]:
        """Synchronously invokes the agent with the given query."""
        config: RunnableConfig = {"configurable": {"thread_id": context_id}}
        today_str = f"Fecha actual: {date.today().strftime('%Y-%m-%d')}."
        augmented_query = f"{today_str}\n\nConsulta del ciudadano: {query}"
        self.graph.invoke({"messages": [("user", augmented_query)]}, config)
        return self.get_agent_response(config)

    @property
    def SYSTEM_INSTRUCTION(self) -> str:
        return SYSTEM_INSTRUCTION

    async def stream(
        self, query: str, context_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        """Streams the agent's response to the given query."""
        today_str = f"Fecha actual: {date.today().strftime('%Y-%m-%d')}."
        augmented_query = f"{today_str}\n\nConsulta del ciudadano: {query}"
        inputs = {"messages": [("user", augmented_query)]}
        config: RunnableConfig = {"configurable": {"thread_id": context_id}}

        async for item in self.graph.astream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]

            if isinstance(message, AIMessage) and message.tool_calls:
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Procesando solicitud...",
                }
            elif isinstance(message, ToolMessage):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Verificando información...",
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config: RunnableConfig) -> dict[str, Any]:
        """Extracts the structured response from the agent's state."""
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get("structured_response")
        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status == "input_required":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            if structured_response.status == "error":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            if structured_response.status == "completed":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": structured_response.message,
                }

        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "No podemos procesar su solicitud en este momento. Intente nuevamente.",
        }
