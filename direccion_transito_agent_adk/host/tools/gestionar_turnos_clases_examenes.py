from typing import Dict, Optional
from datetime import date, timedelta
import random

TURNOS: Dict[str, Dict] = {}


def gestionar_turnos_clases_examenes(tipo: str, fecha_minima: Optional[str] = None ) -> dict:
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

    days_ahead = random.randint(2, 5)
    fecha_1 = base_date + timedelta(days=days_ahead)

    if tipo == "teorico":
        days_examen = days_ahead + random.randint(2, 4)
        fecha_2 = base_date + timedelta(days=days_examen)

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
        return {
            "status": "success",
            "message": "Turno asignado para examen práctico.",
            "data": {
                "tipo": "practico",
                "fecha_examen": fecha_1.strftime("%Y-%m-%d"),
                "hora_examen": f"{random.randint(7, 13)}:00",
            },
        }
