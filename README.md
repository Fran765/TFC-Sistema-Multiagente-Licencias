# Sistema Multiagente - Obtención de Licencia de Conducir

Este proyecto es un sistema multiagente que orquesta el proceso completo de obtención o renovacion de la licencia de conducir, utilizando el protocolo A2A (Agent-to-Agent) para la comunicación entre agentes.

## Arquitectura

El sistema está compuesto por 4 agentes, cada uno construido con un framework diferente:

| Agente | Framework | Rol | Puerto |
|--------|-----------|-----|--------|
| Dirección de Tránsito | ADK | Orquestador central | 10001 |
| ANSES | CrewAI | Emisión de CUIL | 10003 |
| Centro de Salud | ADK | Exámenes médicos y aptitud | 10002 |
| CeNAT | LangGraph | Certificado de antecedentes de tránsito | 10004 |

## Flujo del Proceso

1. **Identificación y Requisitos Previos**
   - El ciudadano solicita su trámite
   - Se obtiene el CUIL (ANSES)
   - Se genera y paga la boleta CeNAT
   - Validación de identidad y antecedentes

2. **Aptitud Psicofísica (Centro de Salud)**
   - Consulta y reserva de turno médico
   - Verificación de pago
   - Emisión del certificado de aptitud

3. **Capacitación y Examen (Dirección de Tránsito)**
   - Asignación de fecha para clase teórica
   - Asignación de fecha para examen teórico
   - Asignacion de fecha para examen practico

4. **Finalización**
   - Carga en sistema nacional
   - Emisión de la licencia

## Requisitos Previos

1. **uv:** Gestor de paquetes de Python.
2. **Python 3.13** requerido para a2a-sdk
3. **Archivo .env** en la raíz del proyecto:
```
GOOGLE_API_KEY="tu_api_key_aqui"
```

## Ejecución de los Agentes

Cada agente debe ejecutarse en una terminal separada:


### Terminal 1: ANSES
```bash
cd anses_agent_crewai
uv venv
source .venv/bin/activate
uv run --active .
```

### Terminal 2: CeNAT
```bash
cd cenat_agent_langgraph
uv venv
source .venv/bin/activate
uv run --active app/__main__.py
```

### Terminal 3: Centro de Salud
```bash
cd centro_salud_agent_adk
uv venv
source .venv/bin/activate
uv run --active .
```

### Terminal 4: Dirección de Tránsito (Orquestador)
```bash
cd direccion_transito_agent_adk
uv venv
source .venv/bin/activate
uv run --active adk web
```

## Uso

Una vez iniciados todos los agentes, el ciudadano interactúa únicamente con el agente de Dirección de Tránsito (puerto 10001). El orquestador gestiona automáticamente la comunicación con los demás agentes.

## Referencias

- https://github.com/google/a2a-python
- https://codelabs.developers.google.com/intro-a2a-purchasing-concierge#1
