import logging
import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent import CentroSaludAgent
from agent_executor import CentroSaludAgentExecutor
from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    pass


def main():
    host = "localhost"
    port = 10002
    try:
        if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE":
            if not os.getenv("GOOGLE_API_KEY"):
                raise MissingAPIKeyError(
                    "GOOGLE_API_KEY environment variable not set and GOOGLE_GENAI_USE_VERTEXAI is not TRUE."
                )

        capabilities = AgentCapabilities(streaming=True)

        skill_disponibilidad = AgentSkill(
            id="disponibilidad",
            name="Consultar Disponibilidad",
            description="Consulta la disponibilidad de turnos médicos en un rango de fechas.",
            tags=["turnos", "disponibilidad"],
            examples=[
                "Qué fechas disponibles hay para la próxima semana?",
            ],
        )

        skill_boleta = AgentSkill(
            id="generar_boleta_pago",
            name="Generar Boleta de Pago",
            description="Genera una boleta de pago para el examen médico.",
            tags=["pago", "boleta"],
            examples=[
                "Generar boleta de pago para DNI 12345678",
            ],
        )

        skill_validar = AgentSkill(
            id="validar_pago_reservar_turno",
            name="Validar Pago y Reservar Turno",
            description="Valida el pago de la boleta y reserva el turno médico.",
            tags=["pago", "reserva", "turno"],
            examples=[
                "Validar pago y reservar turno para DNI 12345678 con boleta MED12345 el 2024-01-15 a las 09:00",
            ],
        )

        skill_resultado = AgentSkill(
            id="obtener_resultado_medico",
            name="Obtener Resultado Médico",
            description="Obtiene el resultado del examen médico del ciudadano.",
            tags=["resultado", "aptitud"],
            examples=[
                "Cuál es el resultado del examen médico de DNI 12345678?",
            ],
        )

        agent_card = AgentCard(
            name="CentroSalud Agent",
            description="Agente del centro médico autorizado para gestionar turnos y emitir certificados de aptitud física.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=["text/plain"],
            defaultOutputModes=["text/plain"],
            capabilities=capabilities,
            skills=[skill_disponibilidad, skill_boleta, skill_validar, skill_resultado],
        )

        centro_salud = CentroSaludAgent()
        runner = Runner(
            app_name=centro_salud._agent.name,
            agent=centro_salud._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        agent_executor = CentroSaludAgentExecutor(runner)

        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        uvicorn.run(server.build(), host=host, port=port)
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
