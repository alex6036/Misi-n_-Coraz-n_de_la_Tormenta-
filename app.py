import streamlit as st
import pandas as pd
import numpy as np
import time
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from utils.precog import VARIABLES, predecir_riesgo
from utils.storage import read_json, write_json, path_asset, DATA_DIR
from utils.simulator import simulate_and_record, _label_from_score
from PIL import Image, ImageDraw, ImageFont


def mostrar_mapa_espana(datos=None):
    """
    Muestra un mapa interactivo de España con puntos de riesgo.
    Si no se pasa 'datos', se generan valores aleatorios.
    """
    if datos is None:
        datos = pd.DataFrame({
            "ciudad": ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Zaragoza"],
            "lat": [40.4168, 41.3874, 39.4699, 37.3891, 43.2630, 41.6488],
            "lon": [-3.7038, 2.1686, -0.3763, -5.9845, -2.9350, -0.8891],
            "riesgo": np.random.randint(40, 100, size=6)  # valores aleatorios entre 40 y 100
        })

    fig = px.scatter_mapbox(
        datos,
        lat="lat",
        lon="lon",
        size="riesgo",
        color="riesgo",
        color_continuous_scale="RdYlGn_r",  # Rojo = más riesgo
        size_max=40,
        zoom=4.5,
        mapbox_style="carto-darkmatter",  # Fondo oscuro estilo dashboard
        hover_name="ciudad",
        title="Mapa de Calor de Riesgo en España"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Inicialización y recursos
# ---------------------------
st.set_page_config(page_title="War Room — ChronoLogistics", layout="wide")
st.title("ChronoLogistics — War Room Dashboard")
st.markdown("**Misión:** Dashboard operativo en vivo — Precog, Chronos y K-Lang. (Demo)")

# Crear assets placeholder si no existen
assets_dir = Path(__file__).resolve().parents[1] / "data" / "assets"
assets_dir.mkdir(parents=True, exist_ok=True)

def _create_placeholder(path: Path, text: str, size=(800, 450)):
    if path.exists():
        return
    img = Image.new("RGB", size, color=(18, 22, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except:
        font = None
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        w, h = draw.textsize(text, font=font)
    draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill=(220, 220, 220), font=font)
    img.save(path)

map_path = assets_dir / "map_clusters.png"
chronos_fortaleza = assets_dir / "chronos_fortaleza.png"
chronos_bunker = assets_dir / "chronos_bunker.png"

_create_placeholder(map_path, "MAPA DE CLÚSTERES (placeholder)")
_create_placeholder(chronos_fortaleza, "FORTALEZA VERDE (placeholder)")
_create_placeholder(chronos_bunker, "BÚNKER TECNOLÓGICO (placeholder)")

protocols = read_json("protocols.json", {})
incidents = read_json("incidents.json", [])

if "events" not in st.session_state:
    st.session_state["events"] = incidents.copy()

# ---------------------------
# Barra lateral: navegación
# ---------------------------
st.sidebar.title("Navegación")
section = st.sidebar.radio("Sección", ["Precog: Monitor de Riesgo", "Chronos: Visión 2040", "K-Lang: Manual de Batalla", "Registro y Auditoría"])

# ---------------------------
# Helpers visuales
# ---------------------------
def label_and_color(score):
    if score <= 0.59:
        return "BAJO", "green"
    if score <= 0.74:
        return "MEDIO", "yellow"
    if score <= 0.89:
        return "ALTO", "orange"
    return "CRÍTICO", "red"

def mostrar_mapa_calor():
    data = np.random.rand(10, 10)
    fig = go.Figure(data=go.Heatmap(z=data, colorscale="RdBu"))
    fig.update_layout(
        title="Mapa de Calor de Riesgo",
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

def mostrar_contribuciones(contribs):
    df = pd.DataFrame([
        {"variable": k, "pct_contrib": v["pct_contrib"]}
        for k, v in contribs.items()
    ]).sort_values("pct_contrib", ascending=True)

    fig = px.bar(
        df,
        x="pct_contrib",
        y="variable",
        orientation="h",
        text=df["pct_contrib"].apply(lambda x: f"{x:.0%}"),
        title="Contribución de cada variable al riesgo"
    )
    fig.update_layout(template="plotly_dark", yaxis_title="", xaxis_title="Porcentaje de contribución")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Sección: PRECOG
# ---------------------------
if section == "Precog: Monitor de Riesgo":
    st.header("Precog — Monitor de Riesgo Táctico")
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Mapa de Calor de Riesgo")
        mostrar_mapa_espana()
        st.caption("Mapa interactivo de clústeres de riesgo en España (datos simulados).")


    with col2:
        st.subheader("Simulador Interactivo")
        inputs = {}
        for var, meta in VARIABLES.items():
            lo, hi = meta["min"], meta["max"]
            if isinstance(lo, int) and isinstance(hi, int):
                val = st.slider(var.replace("_"," "), int(lo), int(hi), int((lo+hi)/4))
            else:
                val = st.slider(var.replace("_"," "), float(lo), float(hi), float((lo+hi)/4))
            inputs[var] = val

        if st.button("Aplicar y Simular"):
            result = predecir_riesgo(inputs)
            res_record = simulate_and_record(inputs)
            st.session_state["events"].insert(0, res_record["incident"])
            st.success(f"Riesgo: {result['pct']}% — {label_and_color(result['score'])[0]}")
            mostrar_contribuciones(result["contribuciones"])

            mostrar_mapa_espana()

    st.subheader("Feed de eventos recientes")
    for ev in st.session_state["events"][:20]:
        st.markdown(f"- **{ev['ts']}** — {ev['label']} — `{ev['id']}` — {ev['vars']}")

# (El resto de secciones se queda igual que en tu código original)

# ---------------------------
# Sección: CHRONOS
# ---------------------------
elif section == "Chronos: Visión 2040":
    st.header("Chronos — Visión Estratégica 2040")
    st.write("Selector de Estrategia y visualización de futuros (imágenes generadas por GAN - placeholders).")
    choice = st.radio("Estrategia", ["Fortaleza Verde", "Búnker Tecnológico"])
    if choice == "Fortaleza Verde":
        st.image(str(chronos_fortaleza), use_column_width=True)
        st.subheader("Defensa estratégica — Fortaleza Verde")
        st.write(
            "Fortaleza Verde apuesta por infraestructuras resilientes y sostenibilidad. "
            "Inversión en movilidad limpia, drenaje urbano y centro de control climático para minimizar impactos. "
            "Beneficios: reducir exposición a eventos climáticos extremos, mejorar imagen corporativa y resiliencia logística en Madrid."
        )
    else:
        st.image(str(chronos_bunker), use_column_width=True)
        st.subheader("Defensa estratégica — Búnker Tecnológico")
        st.write(
            "Búnker Tecnológico prioriza redundancia tecnológica, automatización y robustez en centros de datos. "
            "Inversión en Réplica multi-región, sistemas autónomos de reruteo y control algorítmico de operaciones. "
            "Beneficios: máxima continuidad operativa frente a fallos sistémicos y ciber-incidentes."
        )

# ---------------------------
# Sección: K-LANG
# ---------------------------
elif section == "K-Lang: Manual de Batalla":
    st.header("K-Lang — Manual de Batalla Interactivo")
    st.subheader("Selector de Protocolos")
    proto_choice = st.selectbox("Protocolo", list(protocols.keys()))
    proto = protocols.get(proto_choice, {})
    st.markdown(f"**{proto_choice}** — {proto.get('descripcion','(sin descripción)')}")
    st.write("**Ficha técnica:**")
    st.write(f"- Trigger: {proto.get('trigger')}")
    st.write(f"- Responsables: {', '.join(proto.get('responsables',[]))}")
    st.write("**Secuencia de acciones:**")
    for i, step in enumerate(proto.get("steps", []), 1):
        st.write(f"{i}. {step}")

    st.subheader("Simulador de condiciones reales")
    # Simulador: sliders típicos
    v_wind = st.slider("Velocidad del viento (km/h)", 0, 150, 30)
    v_inund = st.slider("Nivel de inundación (cm)", 0, 500, 5)
    v_temp = st.slider("Temperatura (°C)", -20, 50, 15)
    v_traf = st.slider("Densidad tráfico (%)", 0, 100, 40)

    # Evaluar reglas simples (las mismas que en protocols.json)
    # Regla sencilla: comprobar umbrales básicos
    active = None
    variant = None
    if v_wind >= 110 and v_inund >= 150:
        active = "CÓDIGO ROJO"
        variant = "TITÁN"
    elif v_wind >= 90 or v_inund >= 80:
        active = "CÓDIGO ROJO"
    elif v_wind >= 60 or v_inund >= 20:
        active = "VÍSPERA"
    else:
        # Si score bajo
        # calculamos score de precog
        score = predecir_riesgo({
            "velocidad_media": v_wind,
            "intensidad_lluvia": 0,
            "nivel_inundacion_cm": v_inund,
            "densidad_trafico": v_traf,
            "temperatura": v_temp
        })["score"]
        if score <= 0.4:
            active = "RENACIMIENTO"

    st.subheader("Estado de protocolo actual")
    if active:
        if variant:
            st.error(f"PROTOCOLO ACTIVO: {active}: {variant}")
        else:
            st.error(f"PROTOCOLO ACTIVO: {active}")
    else:
        st.success("Ningún protocolo activo")

    # Acciones rápidas que registran auditoría
    st.write("Acciones rápidas:")
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("Notificar"):
        log_action = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "action": "Notificar", "detail": f"Estado: {active}"}
        aud = read_json("audit_logs.json", [])
        aud.insert(0, log_action)
        write_json("audit_logs.json", aud)
        st.info("Notificado.")
    if col_b.button("Asignar Responsable"):
        st.info("Responsable asignado (demo).")
    if col_c.button("Marcar paso ejecutado"):
        st.success("Paso marcado.")

# ---------------------------
# Sección: Registro y Auditoría
# ---------------------------
elif section == "Registro y Auditoría":
    st.header("Registro y Auditoría")
    incidents = read_json("incidents.json", [])
    st.subheader("Incidentes recientes")
    if incidents:
        df = pd.DataFrame([{
            "id": i["id"],
            "ts": i["ts"],
            "pct": i.get("pct"),
            "label": i.get("label")
        } for i in incidents[:50]])
        st.table(df)
    else:
        st.write("No hay incidentes registrados.")

    st.subheader("Audit logs")
    audit = read_json("audit_logs.json", [])
    if audit:
        for a in audit[:100]:
            st.write(f"- {a.get('ts')} — {a.get('action')} — {a.get('detail','')}")
    else:
        st.write("No hay logs de auditoría todavía.")
