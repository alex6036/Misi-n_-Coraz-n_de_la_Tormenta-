"""
Funciones auxiliares para simular eventos y activar reglas.
"""

import time
from .precog import predecir_riesgo
from .storage import read_json, write_json
from pathlib import Path
import uuid

def simulate_and_record(inputs: dict):
    """
    Ejecuta la predicción de riesgo con los inputs dados,
    guarda un incidente en data/incidents.json si el score supera 0.6 (o siempre graba un evento).
    Devuelve el resultado de precog y la ficha del incidente creado (si aplica).
    """
    result = predecir_riesgo(inputs)
    incidents = read_json("incidents.json", [])
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    incident = {
        "id": str(uuid.uuid4())[:8],
        "ts": ts,
        "score": result["score"],
        "pct": result["pct"],
        "label": _label_from_score(result["score"]),
        "vars": inputs,
        "protocol_activated": None,
        "actions": []
    }
    # Guardamos siempre como registro de simulación
    incidents.insert(0, incident)
    # Mantener tamaño razonable
    incidents = incidents[:500]
    write_json("incidents.json", incidents)
    return {"precog": result, "incident": incident}

def _label_from_score(score: float) -> str:
    if score <= 0.50:
        return "BAJO"
    if score <= 0.70:
        return "MEDIO"
    if score <= 0.80:
        return "ALTO"
    return "CRÍTICO"
