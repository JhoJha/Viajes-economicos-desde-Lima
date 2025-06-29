# Contenido para: backend/database/redbus_loader/utils.py
# (El código de este archivo no necesita cambios, puedes mantener el que ya tienes)
import os
import json
from datetime import datetime, date
import re
import logging

AMENIDADES_MAP = {
    1: "Snacks", 3: "Manta", 4: "Almohada", 5: "Agua embotellada", 6: "Audífonos",
    7: "TV Central", 8: "Música", 9: "Películas", 12: "Baño", 13: "Extintor",
    21: "Luz de lectura", 24: "Cargador", 25: "Descansa piernas", 26: "GPS",
    27: "Cinturón de seguridad", 29: "Aire acondicionado", 30: "Calefacción",
    31: "Asiento reclinable", 33: "Pantalla individual", 34: "Toma de corriente",
    41: "WiFi", 51: "Puerto USB", 52: "Seguimiento en vivo", 71: "CCTV",
    88: "Primeros Auxilios",
}

cache_empresas_por_nombre = {}
cache_empresas_por_operator_id = {}
cache_rutas = {}
cache_amenidades_por_codigo = {}

def obtener_origen_destino(json_data):
    origen = json_data.get("parentSrcCityName", "Desconocido").strip()
    destino = json_data.get("parentDstCityName", "Desconocido").strip()
    return origen, destino

def extraer_fecha_desde_nombre_archivo(nombre_archivo):
    base = os.path.basename(nombre_archivo)
    match = re.search(r"(\d{4})(\d{2})(\d{2})", base)
    if match:
        year, month, day = map(int, match.groups())
        try: return date(year, month, day).isoformat()
        except ValueError: return None
    return None

def limpiar_precios(fare_list):
    if not fare_list: return 0.0, 0.0
    precios_validos = [float(p) for p in fare_list if isinstance(p, (int, float)) or (isinstance(p, str) and p.replace('.', '', 1).isdigit())]
    if not precios_validos: return 0.0, 0.0
    return min(precios_validos), max(precios_validos)

def limpiar_tipo_bus(service_name, bus_type):
    s_name = str(service_name).strip() if service_name else ""
    b_type = str(bus_type).strip() if bus_type else ""
    if s_name and b_type and s_name.lower() != b_type.lower(): return f"{s_name} ({b_type})"
    return s_name or b_type or "No especificado"

def extraer_puntos_parada(inventario_viaje, tipo_punto):
    puntos = []
    json_key = "bpData" if tipo_punto == "embarque" else "dpData"
    for punto_data in inventario_viaje.get(json_key, []):
        if isinstance(punto_data, dict):
            nombre = str(punto_data.get("Name", "")).strip()
            direccion = str(punto_data.get("Address", "")).strip()
            fecha_hora_str = str(punto_data.get("BpFullTime", "")).strip()
            fecha_hora_dt = validar_formato_datetime(fecha_hora_str)
            if nombre and fecha_hora_dt:
                puntos.append((nombre, direccion or None, fecha_hora_dt, tipo_punto))
    return puntos

def extraer_codigos_amenidades(lista_codigos_json):
    if not isinstance(lista_codigos_json, list): return []
    return [int(codigo) for codigo in lista_codigos_json if isinstance(codigo, (int, str)) and str(codigo).isdigit()]

def cargar_json_desde_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        logging.error(f"Error cargando {ruta_archivo}: {e}")
        return None

def generar_url_logo(base_url, path_logo):
    if base_url and path_logo: return base_url.rstrip('/') + "/" + path_logo.lstrip('/')
    return None

def validar_entero_o_none(valor):
    try: return int(valor)
    except (ValueError, TypeError): return None

def validar_flotante_o_none(valor):
    try: return float(valor)
    except (ValueError, TypeError): return None

def validar_formato_datetime(datetime_str, formato_entrada="%Y-%m-%d %H:%M:%S"):
    if not datetime_str or not isinstance(datetime_str, str): return None
    try:
        dt_obj = datetime.strptime(datetime_str, formato_entrada)
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            dt_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None