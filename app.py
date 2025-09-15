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
import plotly.io as pio
pio.templates.default = "plotly_dark"  # Asegura modo oscuro global



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
            "riesgo": np.random.randint(40, 100, size=6)
        })

    fig = px.scatter_mapbox(
        datos,
        lat="lat",
        lon="lon",
        size="riesgo",
        color="riesgo",
        color_continuous_scale="RdYlGn_r",
        size_max=30,
        zoom=4.5,
        mapbox_style="carto-darkmatter",
        hover_name="ciudad",
    )
    fig.update_layout(title="Mapa de Calor de Riesgo en España", margin={"r":0,"t":30,"l":0,"b":0})
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
    st.write("Selector de Estrategia y visualización de futuros (mapa dinámico con zonas estratégicas).")
    choice = st.radio("Estrategia", ["Fortaleza Verde", "Búnker Tecnológico"])

    # Lista de ciudades y coordenadas
    todas_ciudades = pd.DataFrame({
        "ciudad": ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Zaragoza"],
        "lat": [40.4168, 41.3874, 39.4699, 37.3891, 43.2630, 41.6488],
        "lon": [-3.7038, 2.1686, -0.3763, -5.9845, -2.9350, -0.8891],
    })

    # Elegimos aleatoriamente 3 ciudades
    datos = todas_ciudades.sample(n=3, random_state=None).copy()

    # Coloreamos según la estrategia
    if choice == "Fortaleza Verde":
        datos["tipo"] = "Fortaleza Verde"
        datos["color"] = "green"
    else:
        datos["tipo"] = "Búnker Tecnológico"
        datos["color"] = "red"

    # Creamos el mapa interactivo
    fig = px.scatter_mapbox(
        datos,
        lat="lat",
        lon="lon",
        text="ciudad",
        color="color",
        size=[15] * len(datos),  # tamaño fijo de los puntos
        zoom=4.5,
        mapbox_style="carto-darkmatter",
    )
    fig.update_layout(
        title=f"Mapa Estratégico — {choice}",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Descripción de estrategia
    if choice == "Fortaleza Verde":
        st.subheader("Defensa estratégica — Fortaleza Verde")

        # Dividimos en dos columnas
        col1, col2 = st.columns([2, 1])  # col1 más ancha para el texto, col2 para la imagen
        with col1:
            st.write(
                "Fortaleza Verde apuesta por infraestructuras resilientes y sostenibilidad. "
                "Inversión en movilidad limpia, drenaje urbano y centro de control climático para minimizar impactos. "
                "Beneficios: reducir exposición a eventos climáticos extremos, mejorar imagen corporativa y resiliencia logística en Madrid."
            )
        with col2:
            st.image("imagen/verde.png", use_container_width=True)  # usa la ruta de tu imagen

    else:
        st.subheader("Defensa estratégica — Búnker Tecnológico")
        col1, col2 = st.columns([2, 1])  # col1 más ancha para el texto, col2 para la imagen
        with col1:
            st.write(
                "Búnker Tecnológico prioriza redundancia tecnológica, automatización y robustez en centros de datos. "
                "Inversión en Réplica multi-región, sistemas autónomos de reruteo y control algorítmico de operaciones. "
                "Beneficios: máxima continuidad operativa frente a fallos sistémicos y ciber-incidentes."
            )
        with col2:
            st.image("imagen/bunker.jpg", use_container_width=True)  # usa la ruta de tu imagen



# ---------------------------
# Sección: K-LANG
# ---------------------------
elif section == "K-Lang: Manual de Batalla":
    st.header("K-Lang — Manual de Batalla Interactivo")

    # --- Componente 1: Selector de Protocolos ---
    st.subheader("Selector de Protocolos")
    protocolos_disponibles = ["VÍSPERA", "CÓDIGO ROJO", "RENACIMIENTO"]
    protocolo_sel = st.radio("Selecciona un protocolo", protocolos_disponibles)

    # Cargamos información de protocols.json (si existe)
    protocolos_data = read_json("protocols.json", {})
    info = protocolos_data.get(protocolo_sel, {})

    st.markdown(f"### **{protocolo_sel}**")
    st.markdown(f"**Descripción:** {info.get('descripcion', '(Sin descripción)')}")
    st.markdown(f"**Trigger:** {info.get('trigger', '(No especificado)')}")

    st.markdown("**Secuencia de acciones:**")
    for i, step in enumerate(info.get("steps", []), 1):
        st.markdown(f"{i}. {step}")

    # --- Componente 2: Simulador de Protocolos ---
    st.subheader("Simulador de condiciones en tiempo real")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        v_wind = st.slider("Velocidad del viento (km/h)", 0, 150, 30)
    with col2:
        v_inund = st.slider("Nivel de inundación (cm)", 0, 500, 10)
    with col3:
        v_temp = st.slider("Temperatura (°C)", -20, 50, 15)
    with col4:
        v_traf = st.slider("Tráfico (%)", 0, 100, 30)

    # --- Evaluación de protocolos ---
    active = None
    variant = None

    if v_wind >= 110 or v_inund >= 150:
        active = "RENACIMIENTO"
        variant = "THANOS"
    elif v_wind >= 95:
        active = "CÓDIGO ROJO"
        variant = "TITÁN"
    elif v_wind >= 0 or v_inund >= 20:
        active = "VÍSPERA"
        variant = "CELESTIALES"
    else:
        # Si no hay protocolo por condiciones extremas, calculamos con Precog
        score = predecir_riesgo({
            "velocidad_media": v_wind,
            "intensidad_lluvia": 0,
            "nivel_inundacion_cm": v_inund,
            "densidad_trafico": v_traf,
            "temperatura": v_temp
        })["score"]
        if score <= 0.4:
            active = "RENACIMIENTO"

    # --- Indicador de protocolo activo ---
    st.subheader("Estado del Protocolo")
    if active:
        st.markdown(
            f"<h2 style='color:red; text-align:center;'>PROTOCOLO ACTIVO: {active}{' — '+variant if variant else ''}</h2>",
            unsafe_allow_html=True
        )
    else:
        st.markdown("<h3 style='color:green; text-align:center;'>No hay protocolos activos</h3>", unsafe_allow_html=True)
    
    st.subheader("Acciones rápidas")
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
