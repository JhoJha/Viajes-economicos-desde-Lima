# Contenido CORREGIDO para: backend/database/redbus_loader/loader.py
import os
import sqlite3
import logging
from datetime import datetime
from tqdm import tqdm

from .utils import (
    cargar_json_desde_archivo, obtener_origen_destino, limpiar_precios, limpiar_tipo_bus,
    extraer_puntos_parada, extraer_codigos_amenidades, generar_url_logo,
    validar_entero_o_none, validar_flotante_o_none, validar_formato_datetime,
    AMENIDADES_MAP, cache_empresas_por_nombre, cache_empresas_por_operator_id,
    cache_rutas, cache_amenidades_por_codigo
)

LOTE_TAMANO = 200

def registrar_error(cursor, archivo, mensaje, excepcion_detalle=None):
    try:
        cursor.execute("INSERT INTO errores_procesamiento (archivo, mensaje, detalle_excepcion, fecha_error) VALUES (?, ?, ?, ?)",
                       (archivo, mensaje, str(excepcion_detalle), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    except sqlite3.Error as e:
        logging.error(f"Error al registrar error en BD: {e}")

def procesar_lote_archivos(cursor, lote_archivos):
    for ruta_archivo in lote_archivos:
        json_data = cargar_json_desde_archivo(ruta_archivo)
        if not json_data or not isinstance(json_data.get("inventories"), list):
            registrar_error(cursor, ruta_archivo, "JSON inválido o sin inventario.")
            continue

        origen_ciudad, destino_ciudad = obtener_origen_destino(json_data)
        fecha_snapshot = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url_scrapeada = ruta_archivo.replace("\\", "/")
        bus_logo_base_url = json_data.get("metaData", {}).get("busLogoBaseUrl", "")

        ruta_tupla = (origen_ciudad, destino_ciudad)
        if ruta_tupla not in cache_rutas:
            cursor.execute("INSERT OR IGNORE INTO rutas (origen, destino) VALUES (?, ?)", ruta_tupla)
            cursor.execute("SELECT id FROM rutas WHERE origen = ? AND destino = ?", ruta_tupla)
            cache_rutas[ruta_tupla] = cursor.fetchone()[0]
        ruta_id = cache_rutas[ruta_tupla]

        for inv_item in json_data["inventories"]:
            try:
                # --- LÓGICA DE EMPRESAS (UPSERT) ---
                nombre_empresa = str(inv_item.get("travelsName", "")).strip()
                operator_id = validar_entero_o_none(inv_item.get("operatorId"))
                if not nombre_empresa and operator_id is None: continue

                empresa_id = cache_empresas_por_operator_id.get(operator_id) or cache_empresas_por_nombre.get((nombre_empresa, operator_id))
                if empresa_id is None:
                    empresa_data = (
                        nombre_empresa, operator_id, validar_flotante_o_none(inv_item.get("totalRatings")),
                        generar_url_logo(bus_logo_base_url, inv_item.get("operatorLogoPath")),
                        validar_entero_o_none(inv_item.get("totalRatings")),
                        validar_entero_o_none(inv_item.get("numberOfReviews")),
                        validar_flotante_o_none(inv_item.get("busScore"))
                    )
                    cursor.execute("INSERT OR IGNORE INTO empresas (nombre, operator_id, rating, logo_url, total_ratings, number_of_reviews, bus_score) VALUES (?, ?, ?, ?, ?, ?, ?)", empresa_data)
                    if operator_id:
                        cursor.execute("SELECT id FROM empresas WHERE operator_id = ?", (operator_id,))
                    else:
                        cursor.execute("SELECT id FROM empresas WHERE nombre = ?", (nombre_empresa,))
                    empresa_id = cursor.fetchone()[0]
                    if operator_id: cache_empresas_por_operator_id[operator_id] = empresa_id
                    cache_empresas_por_nombre[(nombre_empresa, operator_id)] = empresa_id

                # --- LÓGICA DE VIAJES Y HISTORIAL ---
                hora_salida_str = validar_formato_datetime(inv_item.get("departureTime"))
                hora_llegada_str = validar_formato_datetime(inv_item.get("arrivalTime"))
                if not hora_salida_str or not hora_llegada_str: continue

                dt_salida = datetime.strptime(hora_salida_str, "%Y-%m-%d %H:%M:%S")
                
                # 1. OBTENER O CREAR EL VIAJE EN EL CATÁLOGO
                viaje_estatico_data = (
                    empresa_id, ruta_id, dt_salida.strftime("%Y-%m-%d"),
                    dt_salida.strftime("%H:%M:%S"),
                    datetime.strptime(hora_llegada_str, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S"),
                    validar_entero_o_none(inv_item.get("journeyDurationMin")),
                    limpiar_tipo_bus(inv_item.get("serviceName"), inv_item.get("busType")),
                    inv_item.get("isAc"), inv_item.get("isSeater"), inv_item.get("isSleeper"),
                    validar_entero_o_none(inv_item.get("totalSeats"))
                )
                cursor.execute("INSERT OR IGNORE INTO viajes (empresa_id, ruta_id, fecha_salida, hora_salida_programada, hora_llegada_programada, duracion_programada_min, tipo_bus, es_ac, es_seater, es_sleeper, asientos_totales) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", viaje_estatico_data)
                
                viaje_fue_creado = cursor.lastrowid is not None

                cursor.execute("SELECT id FROM viajes WHERE empresa_id=? AND ruta_id=? AND fecha_salida=? AND hora_salida_programada=? AND tipo_bus=?",
                               (viaje_estatico_data[0], viaje_estatico_data[1], viaje_estatico_data[2], viaje_estatico_data[3], viaje_estatico_data[6]))
                viaje_id = cursor.fetchone()[0]

                # 2. REGISTRAR EL SNAPSHOT EN EL HISTORIAL
                precio_min, precio_max = limpiar_precios(inv_item.get("fareList", []))
                asientos_disp = validar_entero_o_none(inv_item.get("availableSeats"))
                
                # --- ESTA ES LA LÍNEA CORREGIDA ---
                oferta_info = (inv_item.get("operatorOfferCampaign") or {}).get("CmpgList", [{}])[0]
                
                tiene_oferta = bool(oferta_info)
                oferta_desc = oferta_info.get("CampaignDesc")
                precios_orig = oferta_info.get("OriginalPrices", [])
                precios_desc = oferta_info.get("DiscountedPrices", [])
                precio_orig_min = min(precios_orig) if precios_orig else None
                precio_desc_min = min(precios_desc) if precios_desc else None

                snapshot_data = (viaje_id, fecha_snapshot, precio_min, precio_max, asientos_disp, tiene_oferta, oferta_desc, precio_orig_min, precio_desc_min, url_scrapeada)
                cursor.execute("INSERT OR IGNORE INTO historial_viajes (viaje_id, fecha_snapshot, precio_min, precio_max, asientos_disponibles, tiene_oferta, oferta_descripcion, precio_original_min, precio_descuento_min, url_scrapeada) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", snapshot_data)

                # 3. PROCESAR DATOS RELACIONADOS SOLO SI EL VIAJE ES NUEVO
                if viaje_fue_creado:
                    # Puntos de parada
                    puntos = extraer_puntos_parada(inv_item, "embarque") + extraer_puntos_parada(inv_item, "desembarque")
                    if puntos:
                        cursor.executemany("INSERT OR IGNORE INTO puntos_parada (viaje_id, nombre, direccion, fecha_hora, tipo) VALUES (?, ?, ?, ?, ?)",
                                           [(viaje_id, *p) for p in puntos])
                    # Amenidades
                    codigos_amenidades = extraer_codigos_amenidades(inv_item.get("amenities", []))
                    for codigo in codigos_amenidades:
                        if codigo not in cache_amenidades_por_codigo:
                            desc = AMENIDADES_MAP.get(codigo, f"Amenidad Desconocida {codigo}")
                            cursor.execute("INSERT OR IGNORE INTO amenidades (codigo, descripcion) VALUES (?, ?)", (codigo, desc))
                            cursor.execute("SELECT id FROM amenidades WHERE codigo = ?", (codigo,))
                            cache_amenidades_por_codigo[codigo] = cursor.fetchone()[0]
                        amenidad_id = cache_amenidades_por_codigo[codigo]
                        cursor.execute("INSERT OR IGNORE INTO viaje_amenidades (viaje_id, amenidad_id) VALUES (?, ?)", (viaje_id, amenidad_id))

            except (TypeError, IndexError, sqlite3.Error, ValueError) as e:
                registrar_error(cursor, ruta_archivo, "Error procesando un item de inventario.", e)

def cargar_datos_desde_carpeta(carpeta_raiz_json, db_path):
    if not os.path.isdir(carpeta_raiz_json):
        logging.error(f"La carpeta raíz no existe: {carpeta_raiz_json}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    archivos_json = [os.path.join(root, file) for root, _, files in os.walk(carpeta_raiz_json) for file in files if file.lower().endswith(".json")]
    if not archivos_json:
        logging.info("No se encontraron archivos JSON para procesar.")
        conn.close()
        return

    num_lotes = (len(archivos_json) + LOTE_TAMANO - 1) // LOTE_TAMANO
    logging.info(f"Iniciando carga de {len(archivos_json)} archivos en {num_lotes} lotes.")

    for i in tqdm(range(0, len(archivos_json), LOTE_TAMANO), desc="Procesando lotes de JSONs"):
        lote_actual = archivos_json[i:i + LOTE_TAMANO]
        try:
            cursor.execute("BEGIN TRANSACTION")
            procesar_lote_archivos(cursor, lote_actual)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logging.error(f"Error de SQLite en un lote, revirtiendo: {e}")

    logging.info("--- Carga de datos finalizada ---")
    conn.close()