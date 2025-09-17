
# Misión: Corazón de la Tormenta

Dashboard de simulación y monitoreo de riesgos para situaciones de emergencia climática en España. Utiliza Streamlit para visualización, simulación de incidentes y activación de protocolos.

## Características principales
- Visualización de riesgos en mapa interactivo
- Simulación de incidentes y predicción de riesgo (precog)
- Registro y consulta de incidentes
- Activación de protocolos y registro de auditoría

## Estructura del proyecto

```
├── app.py                # Interfaz principal Streamlit
├── main.py               # Lanzador del dashboard
├── requirements.txt      # Dependencias
├── data/                 # Datos simulados y registros
│   ├── audit_logs.json
│   ├── incidents.json
│   ├── protocols.json
│   └── assets/
├── imagen/               # Imágenes para la interfaz
│   ├── bunker.jpg
│   └── verde.png
├── utils/                # Módulos auxiliares
│   ├── precog.py         # Predicción de riesgo
│   ├── simulator.py      # Simulación de incidentes
│   ├── storage.py        # Manejo de datos
│   └── __init__.py
```

## Instalación
1. Clona el repositorio:
	```bash
	git clone https://github.com/alex6036/Misi-n_-Coraz-n_de_la_Tormenta-.git
	cd Misi-n_-Coraz-n_de_la_Tormenta-
	```
2. Instala las dependencias:
	```bash
	pip install -r requirements.txt
	```

## Uso
Ejecuta el dashboard con:
```bash
python main.py
```
Esto abrirá la interfaz Streamlit en tu navegador.

## Dependencias principales
- streamlit
- pandas
- numpy
- Pillow
- plotly

## Créditos
Desarrollado por alex6036. Inspirado en simulaciones de gestión de crisis y dashboards de monitoreo.

---
¡Contribuciones y sugerencias son bienvenidas!