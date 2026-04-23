import os
import json
import logging
from pathlib import Path
from typing import Type

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from tools.emitir_constancia_cuil import emitir_constancia_cuil

load_dotenv()

INSTRUCTION_PATH = Path(__file__).parent / "instruction.md"
BACKSTORY = INSTRUCTION_PATH.read_text(encoding="utf-8")


class EmitirConstanciaCuilInput(BaseModel):
    dni: str = Field(..., description="Número de documento de identidad.")
    sexo: str = Field(
        ..., description="Sexo: M (masculino) o F (femenino).", pattern="^[MF]$"
    )


class EmitirConstanciaCuilTool(BaseTool):
    name: str = "Emitir Constancia CUIL"
    description: str = "Emite una constancia de CUIL para un ciudadano argentino."
    args_schema: Type[BaseModel] = EmitirConstanciaCuilInput

    def _run(self, dni: str, sexo: str) -> str:
        result = emitir_constancia_cuil(dni=dni, sexo=sexo)
        return str(result)

class ANSESAgent:
    SUPPORTED_CONTENT_TYPES = ["text/plain"]
    SUPPORTED_OUTPUT_TYPES = ["application/json"]

    def __init__(self):
        if os.getenv("GOOGLE_API_KEY"):
            self.llm = LLM(
                model="gemini/gemini-3.1-flash-lite-preview", api_key=os.getenv("GOOGLE_API_KEY")
            )
        else:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        self.anses_assistant = Agent(
            role="Emisor de Constancias de CUIL",
            goal="Emitir constancias de CUIL para ciudadanos argentinos.",
            backstory=BACKSTORY,
            verbose=True,
            allow_delegation=False,
            tools=[EmitirConstanciaCuilTool()],
            llm=self.llm,
        )

    def invoke(self, question: str) -> str:
        task_description = (
            f"Solicitud del Orquestador: '{question}'.\n\n"
            "Procesa la solicitud siguiendo estrictamente tu Contrato de Salida."
        )
        process_task = Task(
            description=task_description,
            expected_output= "UNICAMENTE un objeto JSON crudo en texto plano. NO uses bloques de codigo markdown. NO uses la palabra 'json' al inicio. Comienza directamente con { y termina con }.",
            agent=self.anses_assistant,
        )
        crew = Crew(
            agents=[self.anses_assistant],
            tasks=[process_task],
            process=Process.sequential,
            verbose=True,
        )
        try:
            result = crew.kickoff()
            return str(result)
        
        except Exception as e:
            logging.error(f"Fallo crítico en la ejecución del LLM en CrewAI (ANSES): {e}")
            return json.dumps({
                "status": "error",
                "message": "ANSES se encuentra temporalmente fuera de servicio. Por favor, intente nuevamente en unos minutos.",
                "data": {}
            })