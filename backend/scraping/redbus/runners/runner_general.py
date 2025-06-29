# Contenido FINAL y MEJORADO para: backend/scraping/redbus/runners/runner_general.py

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import sys
import calendar # Módulo necesario para calcular los días del mes

# ... (el resto de los imports y la configuración de logging no cambian) ...
from ..extractor import scrape_redbus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

city_ids_path = Path(__file__).parent.parent / "config" / "city_ids.json"
if not city_ids_path.exists():
    logging.error(f"❌ No se encontró el archivo city_ids.json en {city_ids_path}")
    sys.exit()
with open(city_ids_path, "r", encoding="utf-8") as f:
    city_ids = json.load(f)

# ========== INPUT INTERACTIVO ==========
print("\n🗺️  Ciudades disponibles:")
for ciudad in city_ids:
    print("   -", ciudad)

from_name = input("\n🔹 Ingresa ciudad de origen EXACTA (copiar/pegar de arriba): ").strip()
if from_name not in city_ids:
    logging.error("⛔ Error: nombre de ciudad de origen inválido.")
    sys.exit()

# --- NUEVA LÓGICA 1: DESTINO AUTOMÁTICO A LIMA ---
LIMA_CANONICAL_NAME = "Lima (Todos)"
if from_name != LIMA_CANONICAL_NAME:
    to_name = LIMA_CANONICAL_NAME
    print(f"   Destino fijado automáticamente a: {to_name}")
else:
    to_name = input("🔹 Ingresa ciudad de destino EXACTA: ").strip()
    if to_name not in city_ids:
        logging.error("⛔ Error: nombre de ciudad de destino inválido.")
        sys.exit()

from_city_id = city_ids[from_name]
to_city_id = city_ids[to_name]

# --- NUEVA LÓGICA 2: SELECCIÓN DE FECHAS (RANGO VS. MES) ---
print("\n📅 ¿Cómo deseas ingresar las fechas?")
print("   1. Por rango de fechas exactas (YYYY-MM-DD)")
print("   2. Por mes completo (ej. 7 para Julio)")
date_choice = input("   Elige una opción (1 o 2): ").strip()

fecha_inicio = None
fecha_fin = None

if date_choice == '1':
    fecha_inicio_str = input("   Fecha inicio (YYYY-MM-DD): ").strip()
    fecha_fin_str = input("   Fecha fin (YYYY-MM-DD): ").strip()
    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
    except ValueError:
        logging.error("❌ Las fechas deben tener formato YYYY-MM-DD")
        sys.exit()
elif date_choice == '2':
    try:
        year_str = input("   Ingresa el año (ej. 2025): ").strip()
        month_str = input(f"   Ingresa el número del mes (1-12): ").strip()
        year = int(year_str)
        month = int(month_str)
        if not (1 <= month <= 12):
            raise ValueError("Mes debe estar entre 1 y 12.")
        
        _, num_days = calendar.monthrange(year, month)
        fecha_inicio = datetime(year, month, 1)
        fecha_fin = datetime(year, month, num_days)
        print(f"   Fechas calculadas: {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}")
    except (ValueError, TypeError) as e:
        logging.error(f"❌ Entrada inválida. Asegúrate de ingresar números correctos. Error: {e}")
        sys.exit()
else:
    logging.error("❌ Opción no válida. Debes elegir 1 o 2.")
    sys.exit()

# ========== VALIDACIÓN DE FECHAS (ahora usa los objetos fecha_inicio/fin) ==========
if fecha_inicio > fecha_fin:
    logging.error("❌ Fecha de inicio no puede ser mayor que la final.")
    sys.exit()

# ... (el resto del código, desde la validación de MAX_DIAS hasta el final, es idéntico) ...
hoy = datetime.now()
if fecha_inicio < hoy.replace(hour=0, minute=0, second=0, microsecond=0):
    logging.warning("⚠️ Atención: estás incluyendo fechas pasadas. Puede que no haya resultados.")

MAX_DIAS = 45
if (fecha_fin - fecha_inicio).days + 1 > MAX_DIAS:
    logging.error(f"⚠️ Rango muy amplio. Máximo permitido: {MAX_DIAS} días.")
    sys.exit()

meses_es = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

fechas = [(fecha_inicio + timedelta(days=i)).strftime("%d-%b-%Y")
          for i in range((fecha_fin - fecha_inicio).days + 1)]

total = len(fechas)
exitos = 0
fallos = 0

logging.info(f"🚀 Iniciando scraping: {from_name} → {to_name} | Total: {total} fechas")

from_name_clean = from_name.split('(')[0].strip()
to_name_clean = to_name.split('(')[0].strip()

for i, fecha_str in enumerate(fechas, start=1):
    try:
        fecha_obj = datetime.strptime(fecha_str, "%d-%b-%Y")
        nombre_mes = meses_es[fecha_obj.month]
        fecha_archivo = fecha_obj.strftime("%Y%m%d")

        output_dir = Path(f"data/raw/redbus/{from_name_clean}/{to_name_clean}/{nombre_mes}")
        output_dir.mkdir(parents=True, exist_ok=True)

        archivo_json = output_dir / f"api_response_{fecha_archivo}.json"
        if archivo_json.exists():
            logging.info(f"📁 Ya existe: {archivo_json}, saltando...")
            continue

        logging.info(f"📆 Procesando fecha {i}/{total}: {fecha_str}")
        scrape_redbus(
            from_city_id=from_city_id,
            to_city_id=to_city_id,
            from_name=from_name,
            to_name=to_name,
            date_str=fecha_str,
            output_dir=output_dir
        )
        exitos += 1

    except Exception as e:
        logging.error(f"❌ Fallo al procesar {fecha_str}: {e}")
        fallos += 1

logging.info(f"✅ Scraping terminado | Éxitos: {exitos} | Fallos: {fallos}")