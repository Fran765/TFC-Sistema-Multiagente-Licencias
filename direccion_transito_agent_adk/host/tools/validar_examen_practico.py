from .gestionar_turnos_clases_examenes import TURNOS

def validar_examen_practico(dni: str) -> dict:
    if not dni:
        return {
            "status": "error", 
            "message": "DNI es requerido."
        }
    
    if dni not in TURNOS or "practico" not in TURNOS[dni]:
        return {
            "status": "error", 
            "message": "No se encontraron turnos prácticos para este DNI."
        }
    
    resultado = "aprobado"
    TURNOS[dni]["practico"]["estado"] = resultado

    return {
        "status": "success",
        "message": "Resultado del examen práctico consultado.",
        "data": {
            "dni": dni,
            "resultado": resultado,
        },
    }
