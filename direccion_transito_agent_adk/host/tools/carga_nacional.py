from datetime import date
import uuid
from typing import Dict

LICENSES: Dict[str, Dict] = {}


def carga_nacional(dni: str, nombre: str, apellido: str) -> dict:
    if not dni or not nombre or not apellido:
        return {"status": "error", "message": "DNI, nombre y apellido son requeridos."}

    codigo_tramite = f"TRAM{uuid.uuid4().hex[:8].upper()}"

    licencia = {
        "codigo_tramite": codigo_tramite,
        "dni": dni,
        "nombre": nombre,
        "apellido": apellido,
        "fecha_emision": date.today().strftime("%Y-%m-%d"),
        "estado": "aprobado",
    }

    LICENSES[codigo_tramite] = licencia

    return {
        "status": "success",
        "message": "Legajo cargado en sistema nacional exitosamente.",
        "data": {
            "codigo_tramite": codigo_tramite,
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "estado": "aprobado",
        },
    }
