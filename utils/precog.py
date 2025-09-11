"""
Funcionalidad 'precog' - predecir riesgo.

Implementación explicable simple:
 - Normalizamos inputs por sus rangos
 - Aplicamos pesos (viento y lluvia dominantes)
 - score = sigmoid(sum(weights * normalized_values))
 - Devolvemos dict con score (0..1) y contribuciones por variable
"""

from math import exp
from typing import Dict

# Definición de variables y rangos (usados para normalizar)
VARIABLES = {
    "velocidad_media": {"min": 0, "max": 150},
    "intensidad_lluvia": {"min": 0, "max": 200},
    "nivel_inundacion_cm": {"min": 0, "max": 500},
    "densidad_trafico": {"min": 0, "max": 100},
    "temperatura": {"min": -20, "max": 50},
}

# Pesos por variable (ajustables)
WEIGHTS = {
    "velocidad_media": 1.0,
    "intensidad_lluvia": 0.9,
    "nivel_inundacion_cm": 1.1,
    "densidad_trafico": 0.4,
    "temperatura": 0.1,
}

def _sigmoid(x: float) -> float:
    return 1 / (1 + exp(-x))

def _normalize(name: str, value: float) -> float:
    rng = VARIABLES[name]
    lo, hi = rng["min"], rng["max"]
    if hi == lo:
        return 0.0
    # Clip and normalize to [0,1]
    v = max(min(value, hi), lo)
    return (v - lo) / (hi - lo)

def predecir_riesgo(inputs: Dict[str, float]) -> Dict:
    # Ensure all variables present (missing -> 0 normalized)
    contribs = {}
    s = 0.0
    for var, w in WEIGHTS.items():
        val = float(inputs.get(var, 0.0))
        norm = _normalize(var, val)
        contrib = w * norm
        contribs[var] = {"valor": val, "normalizado": round(norm, 4), "peso": w, "contrib": round(contrib, 4)}
        s += contrib
    # map s to sigmoid to keep 0..1
    score = _sigmoid(s - 1.5)  # shift so typical values not too close to 1
    # Normalizamos las contribuciones percentuales sobre s (evitar div por 0)
    total_contrib = s if s > 0 else 1.0
    for var in contribs:
        contribs[var]["pct_contrib"] = round(100 * (contribs[var]["contrib"] / total_contrib), 1)
    return {"score": round(score, 4), "pct": int(round(score * 100)), "contribuciones": contribs}
