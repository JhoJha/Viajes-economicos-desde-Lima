# Contenido para: run_db_loader.py (en la raíz del proyecto)
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from backend.database.redbus_loader.schema import crear_tablas
from backend.database.redbus_loader.loader import cargar_datos_desde_carpeta

DB_PATH = Path("data/processed/viajes.db")
JSON_ROOT_PATH = Path("data/raw/redbus")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"1. Creando/verificando esquema de la base de datos en: {DB_PATH}")
    crear_tablas(str(DB_PATH))
    logging.info("   Esquema listo.")

    logging.info(f"2. Iniciando la carga de datos desde: {JSON_ROOT_PATH}")
    cargar_datos_desde_carpeta(str(JSON_ROOT_PATH), str(DB_PATH))

    logging.info("\n✅ ¡Proceso de carga a la base de datos completado!")

if __name__ == "__main__":
    main()