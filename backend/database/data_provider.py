# Contenido MEJORADO para: backend/database/data_provider.py

import sqlite3
import pandas as pd
from pathlib import Path
import logging

try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    DB_PATH = PROJECT_ROOT / "data" / "processed" / "viajes.db"
except NameError:
    DB_PATH = Path("data/processed/viajes.db")

def load_all_data_for_frontend():
    if not DB_PATH.exists():
        logging.warning(f"La base de datos no se encontró en la ruta: {DB_PATH}")
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        
        # --- LA NUEVA CONSULTA SQL CON CÁLCULO DE PROMEDIO ---
        query = """
        WITH 
        LatestSnapshot AS (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY viaje_id ORDER BY fecha_snapshot DESC) as rn
            FROM historial_viajes
        ),
        RoutePriceAvg AS (
            SELECT v.ruta_id, AVG(h.precio_min) as precio_promedio_ruta
            FROM historial_viajes h
            JOIN viajes v ON h.viaje_id = v.id
            GROUP BY v.ruta_id
        )
        SELECT
            v.id as viaje_id, e.nombre as empresa, e.rating, r.origen, r.destino,
            v.fecha_salida, v.hora_salida_programada, v.hora_llegada_programada,
            v.duracion_programada_min, v.tipo_bus, v.es_ac, v.es_seater, v.es_sleeper,
            v.asientos_totales, ls.fecha_snapshot, ls.precio_min, ls.precio_max,
            ls.asientos_disponibles, ls.tiene_oferta, ls.oferta_descripcion,
            ls.precio_original_min, ls.precio_descuento_min,
            rpa.precio_promedio_ruta -- <-- La nueva columna que necesitamos
        FROM LatestSnapshot ls
        JOIN viajes v ON ls.viaje_id = v.id
        JOIN empresas e ON v.empresa_id = e.id
        JOIN rutas r ON v.ruta_id = r.id
        LEFT JOIN RoutePriceAvg rpa ON v.ruta_id = rpa.ruta_id
        WHERE ls.rn = 1;
        """
        
        df = pd.read_sql_query(query, conn)
        logging.info(f"Datos cargados exitosamente. {len(df)} viajes actuales encontrados.")
        return df

    except sqlite3.Error as e:
        logging.error(f"Error al consultar la base de datos: {e}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals() and conn:
            conn.close()