# Contenido de ALTO RENDIMIENTO para: backend/scraping/redbus/runners/runner_batch.py

import logging
from pathlib import Path
from datetime import datetime, timedelta
import sys
import calendar
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed # <-- 1. Importamos las herramientas de concurrencia

# Importar las herramientas necesarias
from ..extractor import scrape_redbus

# ========== CONFIGURACIÓN DEL LOTE ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- ¡EL ACELERADOR! ---
# Número de trabajadores (peticiones simultáneas).
# Un buen punto de partida es entre 8 y 16. No lo subas demasiado al principio.
MAX_WORKERS = 16

TARGET_YEAR = 2025
TARGET_MONTH = 7

try:
    city_ids_path = Path(__file__).parent.parent / "config" / "city_ids.json"
    with open(city_ids_path, "r", encoding="utf-8") as f:
        city_ids = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error(f"❌ No se pudo cargar 'city_ids.json': {e}")
    sys.exit()

# ========== LÓGICA DE EJECUCIÓN AUTOMÁTICA Y CONCURRENTE ==========

def run_batch_scraping():
    """
    Ejecuta el scraping de forma concurrente para ser mucho más rápido.
    """
    meses_es = {7: "julio"}
    nombre_mes_str = meses_es.get(TARGET_MONTH, f"mes_{TARGET_MONTH}")

    logging.info(f"🚀 INICIANDO SCRAPING CONCURRENTE (hasta {MAX_WORKERS} trabajadores) PARA: {nombre_mes_str.capitalize()} {TARGET_YEAR}")

    all_cities = list(city_ids.keys())
    
    _, num_days = calendar.monthrange(TARGET_YEAR, TARGET_MONTH)
    fechas_mes = [
        (datetime(TARGET_YEAR, TARGET_MONTH, day)).strftime("%d-%b-%Y")
        for day in range(1, num_days + 1)
    ]

    # --- 2. PREPARAMOS TODAS LAS TAREAS ANTES DE EMPEZAR ---
    tasks_to_run = []
    for from_name in all_cities:
        for to_name in all_cities:
            if from_name == to_name:
                continue

            from_name_clean = from_name.split('(')[0].strip()
            to_name_clean = to_name.split('(')[0].strip()

            for date_str in fechas_mes:
                output_dir = Path(f"data/raw/redbus/{from_name_clean}/{to_name_clean}/{nombre_mes_str}")
                fecha_archivo = datetime.strptime(date_str, "%d-%b-%Y").strftime("%Y%m%d")
                archivo_json = output_dir / f"api_response_{fecha_archivo}.json"

                # Si el archivo ya existe, no lo añadimos a la lista de tareas
                if archivo_json.exists():
                    continue
                
                # Añadimos una tupla con todos los argumentos que necesita scrape_redbus
                tasks_to_run.append((
                    city_ids[from_name], city_ids[to_name], from_name, to_name, date_str, output_dir
                ))

    if not tasks_to_run:
        logging.info("✅ No hay tareas nuevas que ejecutar. ¡Todo está al día!")
        return

    logging.info(f"📰 Tareas pendientes encontradas: {len(tasks_to_run)}")

    # --- 3. EJECUTAMOS LAS TAREAS CON EL EQUIPO DE TRABAJADORES ---
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Creamos un diccionario para mapear futuros a sus argumentos
        future_to_task = {
            executor.submit(scrape_redbus, *task): task for task in tasks_to_run
        }

        # Usamos tqdm para crear la barra de progreso sobre los futuros completados
        progress_bar = tqdm(as_completed(future_to_task), total=len(tasks_to_run), desc="Procesando rutas")
        
        for future in progress_bar:
            task_args = future_to_task[future]
            try:
                # Obtenemos el resultado (aunque scrape_redbus no devuelve nada,
                # esto es importante para que se lancen las excepciones si las hubo)
                future.result()
            except Exception as exc:
                # Si una tarea falló, lo mostramos en el log
                logging.error(f'❌ Tarea {task_args[2]}->{task_args[3]} en {task_args[4]} generó una excepción: {exc}')

    logging.info("\n✅✅✅ PROCESO CONCURRENTE COMPLETADO ✅✅✅")

if __name__ == "__main__":
    run_batch_scraping()