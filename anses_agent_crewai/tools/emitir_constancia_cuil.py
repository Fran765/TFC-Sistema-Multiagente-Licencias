from typing import Dict

CUIL_EMITIDOS: Dict[str, str] = {}
MULTIPLICADORES_AFIP = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

def emitir_constancia_cuil(dni: str, sexo: str) -> str:
    if not dni or not sexo:
        return  "ERROR: DNI y sexo son requeridos."

    if sexo.upper() not in ["M", "F"]:
        return "ERROR: Sexo debe ser M o F."

    if dni in CUIL_EMITIDOS:
        return CUIL_EMITIDOS[dni]
        
    prefix = "20" if sexo.upper() == "M" else "27"

    if len(dni) < 8:
        dni = dni.zfill(8)
    
    base_calculo = prefix + dni
    suma = sum(int(digito) * mult for digito, mult in zip(base_calculo, MULTIPLICADORES_AFIP))

    resto = suma % 11 

    if resto == 0:
        suffix = "0"
    elif resto == 1: # Caso overflow: Se cambia el prefijo a 23 y se asigna un Z específico
        prefix = "23"
        suffix = "9" if sexo.upper() == "M" else "4"
    else:
        suffix = str(11 - resto)


    cuil = f"{prefix}-{dni}-{suffix}"
    CUIL_EMITIDOS[dni] = cuil

    return cuil
