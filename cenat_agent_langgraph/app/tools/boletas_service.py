from datetime import date
import random

class BoletaService:
    """Service class to manage CeNAT payment receipts (boletas)."""

    def __init__(self):
        self._boletas: dict[str, dict] = {}

    def generar(self, dni: str, nombre: str, apellido: str) -> dict:
        """Generates a new payment receipt."""
        if not dni or not nombre or not apellido:
            return {"status": "error", "message": "DNI, nombre y apellido son requeridos."}
        
        codigo_pago = f"CENAT{random.randint(100000, 999999)}"
        boleta = {
            "codigo_pago": codigo_pago,
            "dni": dni,
            "nombre": nombre,
            "apellido": apellido,
            "monto": 500.0,
            "fecha_emision": date.today().strftime("%Y-%m-%d"),
            "estado": "pendiente",
        }
        self._boletas[codigo_pago] = boleta
        return boleta

    def certificar_pago(self, codigo_pago: str) -> dict | None:
        """Certifies that a payment has been made."""
        if codigo_pago not in self._boletas:
            return None
        self._boletas[codigo_pago]["estado"] = "pagado"
        return self._boletas[codigo_pago]

    def obtener(self, codigo_pago: str) -> dict | None:
        """Retrieves a boleta by payment code."""
        return self._boletas.get(codigo_pago)