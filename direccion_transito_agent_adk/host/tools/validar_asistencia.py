from typing import Dict

ASISTENCIAS: Dict[str, bool] = {}


def validar_asistencia(dni: str, actividad: str) -> dict:
    if not dni or not actividad:
        return {"status": "error", "message": "DNI y actividad son requeridos."}

    if actividad not in ["clase_teorica", "examen_teorico"]:
        return {
            "status": "error",
            "message": "Actividad debe ser 'clase_teorica' o 'examen_teorico'.",
        }

    ASISTENCIAS[f"{dni}_{actividad}"] = True

    return {
        "status": "success",
        "message": f"Asistencia validada para {actividad}.",
        "data": {
            "dni": dni,
            "actividad": actividad,
            "asistio": True,
        },
    }
