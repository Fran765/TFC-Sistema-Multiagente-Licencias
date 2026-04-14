from typing import Dict
import random

EXAMENES: Dict[str, str] = {}


def validar_examen_practico(dni: str) -> dict:
    if not dni:
        return {"status": "error", "message": "DNI es requerido."}

    if dni not in EXAMENES:
        # resultado = "aprobado" if random.random() > 0.2 else "reprobado"
        resultado = "aprobado"
        EXAMENES[dni] = resultado
    else:
        resultado = EXAMENES[dni]

    return {
        "status": "success",
        "message": "Resultado del examen práctico consultado.",
        "data": {
            "dni": dni,
            "resultado": resultado,
        },
    }
