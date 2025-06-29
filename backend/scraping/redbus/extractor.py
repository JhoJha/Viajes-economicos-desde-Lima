# Contenido CORREGIDO para: backend/scraping/redbus/extractor.py

import os
import json
import time
import random
import logging
from datetime import datetime
import requests

from .config.config import HEADERS, COOKIES, BODY

def scrape_redbus(from_city_id, to_city_id, from_name, to_name, date_str, output_dir):
    """
    Realiza scraping a la API de RedBus y guarda el JSON crudo aunque no haya viajes,
    para poder inspeccionar la estructura de la respuesta.
    """
    try:
        date_obj = datetime.strptime(date_str, "%d-%b-%Y")
    except ValueError:
        logging.error(f"❌ Fecha inválida: '{date_str}'. Usa formato 'DD-MMM-YYYY' (ej. 15-Jun-2025)")
        return

    os.makedirs(output_dir, exist_ok=True)

    # --- INICIO DE LA MODIFICACIÓN ---

    # 1. Definimos la URL base sin parámetros
    base_url = "https://www.redbus.pe/search/SearchV4Results"

    # 2. Creamos un diccionario con todos los parámetros de la URL
    params = {
        "fromCity": from_city_id,
        "toCity": to_city_id,
        "src": from_name,
        "dst": to_name,
        "DOJ": date_str,
        "sectionId": 0,
        "groupId": 0,
        "limit": 20,
        "offset": 0,
        "sort": 0,
        "sortOrder": 0,
        "meta": "true",
        "returnSearch": 0,
    }

    logging.info(f"🔍 Buscando: {from_name} → {to_name} | Fecha: {date_str}")

    try:
        # 3. Pasamos la URL base y el diccionario de 'params' a requests.
        # La librería se encargará de construir la URL final correctamente.
        response = requests.post(base_url, params=params, headers=HEADERS, cookies=COOKIES, json=BODY, timeout=15)

    # --- FIN DE LA MODIFICACIÓN ---

        if response.status_code == 429:
            logging.warning("⚠️ Código 429: Rate limiting. Aumentando delay.")
            time.sleep(random.uniform(10, 20))
            return

        if response.status_code == 403:
            logging.error("⛔ Código 403: IP posiblemente bloqueada.")
            return

        logging.info(f"📡 Código de estado: {response.status_code}")
        response.raise_for_status() # Esto es lo que lanza el error con el código 500

        data = response.json()

        # Guardamos SIEMPRE el JSON completo para inspección
        fecha_formato = date_obj.strftime("%Y%m%d")
        output_path = os.path.join(output_dir, f"api_response_{fecha_formato}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logging.info(f"📁 Archivo (debug) guardado: {output_path}")

        # Intentamos acceder al campo "inventories"
        results = data.get("inventories", [])
        if not results:
            logging.warning("⚠️ No se encontraron viajes o estructura de API inesperada.")
            # No retornamos, para que el bucle continúe con la siguiente fecha
        else:
            logging.info(f"✅ {len(results)} resultados encontrados")

    except requests.exceptions.Timeout:
        logging.error("⏱️ Timeout: El servidor no respondió a tiempo.")
    except requests.RequestException as e:
        # El error 500 se captura aquí
        logging.error(f"❌ Error de red: {e}")
    except Exception as e:
        logging.error(f"❌ Error inesperado: {e}")

    # El sleep se ejecuta incluso si hay un error, para no martillar el servidor
    time.sleep(random.uniform(5, 10))