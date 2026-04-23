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
from agent import ANSESAgent
from agent_executor import ANSESAgentExecutor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


def main():
    """Entry point for ANSES Agent."""
    host = "localhost"
    port = 10003
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=False)

        skill = AgentSkill(
            id="emitir_constancia_cuil",
            name="Emisión de Constancia CUIL",
            description="Emite constancias de CUIL (Clave Única de Identificación Laboral) para ciudadanos argentinos. REQUISITO ESTRICTO: Para invocar esta habilidad es obligatorio proporcionar el DNI (solo números) y el Sexo (M o F) del ciudadano. No invocar si faltan estos datos.",
            
            tags=["anses", "cuil", "identidad"],
            examples=[
                "Obtener la constancia de CUIL para Juan Pérez, DNI 12345678, sexo masculino",
                "Generar comprobante de CUIL de María García, DNI 20334455, sexo femenino",
                "Emitir CUIL: documento 12345678, sexo M",
                "Necesito la constancia de CUIL de un ciudadano con DNI 95123456 y sexo F"
            ],
        )

        agent_card = AgentCard(
            name="ANSES Agent",
            description="Agente del sistema ANSES encargado de emitir constancias de CUIL de los ciudadanos argentinos.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=ANSESAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=ANSESAgent.SUPPORTED_OUTPUT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=ANSESAgentExecutor(),
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
