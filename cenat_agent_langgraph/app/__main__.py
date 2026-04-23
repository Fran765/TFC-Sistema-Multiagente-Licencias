import logging
import os
import sys

import httpx
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from app.agent import CenatAgent
from app.agent_executor import CenatAgentExecutor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    pass


def main():
    host = "localhost"
    port = 10004
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)

        skill_boleta = AgentSkill(
            id="generar_boleta_cenat",
            name="Generar Boleta CeNAT",
            description="Genera una boleta del Certificado Nacional de Antecedentes de Tránsito (CeNAT). REQUISITO ESTRICTO: Para generar una boleta, es OBLIGATORIO proporcionar DNI, Nombre y Apellido.",
            tags=["cenat", "boleta", "antecedentes"],
            examples=[
                "Necesito la boleta del CeNAT para Juan Pérez",
            ],
        )

        skill_pago = AgentSkill(
            id="certificar_pago",
            name="Certificar Pago CeNAT",
            description="Certifica si el pago de la boleta CeNAT fue acreditado. REQUISITO ESTRICTO: Para certificar el pago, es OBLIGATORIO proporcionar el código de pago de la boleta previamente generada.",
            tags=["cenat", "pago", "certificacion"],
            examples=[
                "Verificar si el pago con código CENAT123456 fue acreditado",
            ],
        )

        agent_card = AgentCard(
            name="CeNAT Agent",
            description="Agente especialista del sistema de Certificado Nacional de Antecedentes de Tránsito (CeNAT). Encargado de la validación de antecedentes de tránsito mediante la emisión y certificación de boletas de pago.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=CenatAgent.SUPPORTED_INPUT_TYPES,
            defaultOutputModes=CenatAgent.SUPPORTED_OUTPUT_TYPES,
            capabilities=capabilities,
            skills=[skill_boleta, skill_pago],
        )

        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=CenatAgentExecutor(),
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        uvicorn.run(server.build(), host=host, port=port)

    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
