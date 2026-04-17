from .gestionar_turnos_clases_examenes import TURNOS

def validar_asistencia(dni: str, actividad: str) -> dict:
    if not dni or not actividad:
        return {
            "status": "error", 
            "message": "DNI y actividad son requeridos."
        }

    if actividad not in ["clase_teorica", "examen_teorico"]:
        return {
            "status": "error",
            "message": "Actividad debe ser 'clase_teorica' o 'examen_teorico'.",
        }
    
    if dni not in TURNOS or "teorico" not in TURNOS[dni]:
        return {
            "status": "error", 
            "message": "No se encontraron turnos para este DNI."
        }

    if actividad == "clase_teorica":
        TURNOS[dni]["teorico"]["asistencia_clase"] = True

    elif actividad == "examen_teorico":
        TURNOS[dni]["teorico"]["asistencia_examen"] = True

    if TURNOS[dni]["teorico"].get("asistencia_clase") and TURNOS[dni]["teorico"].get("asistencia_examen"):
        TURNOS[dni]["teorico"]["estado"] = "aprobado"

    return {
        "status": "success",
        "message": f"Asistencia validada para {actividad}.",
        "data": {
            "dni": dni,
            "actividad": actividad,
            "asistio": True,
        },
    }
