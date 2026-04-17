from typing import Dict, Optional
from datetime import date, timedelta
import random

TURNOS: Dict[str, Dict] = {}

def gestionar_turnos_clases_examenes(dni: str, tipo: str, fecha_minima: Optional[str] = None ) -> dict:
    if not dni:
        return {"status": "error", "message": "DNI es requerido."}

    if not tipo:
        return {"status": "error", "message": "Tipo es requerido."}

    if tipo not in ["teorico", "practico"]:
        return {"status": "error", "message": "Tipo debe ser 'teorico' o 'practico'."}

    if fecha_minima:
        try:
            base_date = date.fromisoformat(fecha_minima)
        except ValueError:
            return {"status": "error", "message": "Formato de fecha mínima inválido. Use YYYY-MM-DD."}
    else:
        base_date = date.today()

    if dni not in TURNOS:
        TURNOS[dni] = {}

    days_ahead = random.randint(1, 2)
    fecha_1 = base_date + timedelta(days=days_ahead)

    if tipo == "teorico":
        days_examen = days_ahead + random.randint(1, 2)
        fecha_2 = base_date + timedelta(days=days_examen)

        TURNOS[dni]["teorico"] = {
            "fecha_clase": fecha_1.strftime("%Y-%m-%d"),
            "asistencia_clase": False,
            "fecha_examen": fecha_2.strftime("%Y-%m-%d"),
            "asistencia_examen": False,
            "estado": "pendiente"
        }

        return {
            "status": "success",
            "message": "Turnos asignados para clase y examen teórico.",
            "data": {
                "tipo": "teorico",
                "fecha_clase": fecha_1.strftime("%Y-%m-%d"),
                "hora_clase": f"{random.randint(9, 14)}:00",
                "fecha_examen": fecha_2.strftime("%Y-%m-%d"),
                "hora_examen": f"{random.randint(9, 12)}:00",
            },
        }

    else:
        TURNOS[dni]["practico"] = {
            "fecha_examen": fecha_1.strftime("%Y-%m-%d"),
            "estado": "pendiente"
        }
        return {
            "status": "success",
            "message": "Turno asignado para examen práctico.",
            "data": {
                "tipo": "practico",
                "fecha_examen": fecha_1.strftime("%Y-%m-%d"),
                "hora_examen": f"{random.randint(7, 13)}:00",
            },
        }
