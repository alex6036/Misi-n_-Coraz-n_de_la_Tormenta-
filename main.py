import subprocess
import sys
import os

if __name__ == "__main__":
    # Aseguramos que la carpeta actual es la del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("🚀 Iniciando War Room Dashboard (Streamlit)...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
