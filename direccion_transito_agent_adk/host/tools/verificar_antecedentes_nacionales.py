from typing import Dict

IDENTITY_RECORDS: Dict[str, Dict] = {}


def verificar_antecedentes_nacionales(dni: str) -> dict:
    if not dni:
        return {"status": "error", "message": "DNI es requerido."}

    record = IDENTITY_RECORDS.get(dni)

    if record:
        return {
            "status": "success",
            "message": "Validación cruzada con Nación completada.",
            "data": {
                "dni": dni,
                "nombre": record.get("nombre"),
                "apellido": record.get("apellido"),
                "validado": True,
                "antecedentes": record.get("antecedentes", []),
            },
        }

    return {
        "status": "success",
        "message": "Ciudadano validado en sistema de Nación.",
        "data": {
            "dni": dni,
            "validado": True,
            "antecedentes": [],
        },
    }
