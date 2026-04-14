from typing import Dict
import random

CUIL_EMITIDOS: Dict[str, str] = {}

def emitir_constancia_cuil(dni: str, sexo: str) -> dict:
    if not dni or not sexo:
        return {"status": "error", "message": "DNI y sexo son requeridos."}

    if sexo.upper() not in ["M", "F"]:
        return {"status": "error", "message": "Sexo debe ser M o F."}

    if dni in CUIL_EMITIDOS:
        return {
            "status": "success",
            "message": "Constancia de CUIL emitida.",
            "data": {"cuil": CUIL_EMITIDOS[dni], "dni": dni},
        }

    prefix = "20" if sexo.upper() == "M" else "27"
    suffix = str(random.randint(0, 9))

    cuil = f"{prefix}-{dni}-{suffix}"
    CUIL_EMITIDOS[dni] = cuil

    return {
        "status": "success",
        "message": "Constancia de CUIL emitida.",
        "data": {"cuil": cuil, "dni": dni},
    }
