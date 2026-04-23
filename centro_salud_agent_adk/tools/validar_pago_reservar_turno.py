import random
from typing import Dict

from .calendario import CALENDAR
from .generar_boleta_pago import BOLETAS

TURNOS: Dict[str, Dict] = {}


def validar_pago_reservar_turno(
    dni: str, nro_boleta: str, fecha: str, hora: str
) -> dict:
    if not dni or not nro_boleta or not fecha or not hora:
        return "Todos los campos son requeridos."

    if nro_boleta not in BOLETAS:
        return "Boleta no encontrada."

    if BOLETAS[nro_boleta]["estado"] != "pendiente":
        return f"La boleta ya fue cerrada. {BOLETAS[nro_boleta]['estado']}."

    if fecha not in CALENDAR or hora not in CALENDAR[fecha]:
        return "Fecha u horario no disponible."

    BOLETAS[nro_boleta]["estado"] = "pagado"

    turn_id = f"TURNO{random.randint(1000, 9999)}"

    TURNOS[turn_id] = {
        "turn_id": turn_id,
        "dni": dni,
        "fecha": fecha,
        "hora": hora,
        "estado": "reservado",
    }

    return {
            "turn_id": turn_id,
            "fecha": fecha,
            "hora": hora,
            "estado": "confirmado"
        }
