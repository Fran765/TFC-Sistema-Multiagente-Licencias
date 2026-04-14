from typing import Dict

RESULTADOS: Dict[str, str] = {}


def obtener_resultado_medico(dni: str) -> dict:
    if not dni:
        return {"status": "error", "message": "DNI es requerido."}

    resultado = RESULTADOS.get(dni, "apto")

    return {
        "status": "success",
        "data": {
            "dni": dni,
            "resultado": resultado,
        },
    }
