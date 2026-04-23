from typing import Dict

RESULTADOS: Dict[str, str] = {}


def obtener_resultado_medico(dni: str) -> dict:
    if not dni:
        return "El DNI es requerido."

    return RESULTADOS.get(dni, "apto")