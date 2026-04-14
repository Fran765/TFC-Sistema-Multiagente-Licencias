from datetime import datetime
import random
from typing import Dict

BOLETAS: Dict[str, Dict] = {}


def generar_boleta_pago(dni: str) -> dict:
    if not dni:
        return {"status": "error", "message": "DNI es requerido."}

    nro_boleta = f"MED{random.randint(10000, 99999)}"

    boleta = {
        "nro_boleta": nro_boleta,
        "dni": dni,
        "monto": 1500.0,
        "fecha_emision": datetime.now().strftime("%Y-%m-%d"),
        "estado": "pendiente",
    }

    BOLETAS[nro_boleta] = boleta

    return {
        "status": "success",
        "message": "Boleta de pago generada.",
        "data": {
            "nro_boleta": nro_boleta,
            "monto": boleta["monto"],
            "dni": dni,
            "estado": "pendiente",
        },
    }
