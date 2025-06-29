# Contenido para: backend/database/redbus_loader/schema.py
import sqlite3
import logging

def crear_tablas(db_path):
    """
    Crea/verifica el esquema completo de la base de datos, incluyendo las nuevas
    columnas para ofertas y características del bus.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- TABLAS DE CATÁLOGO ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rutas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origen TEXT NOT NULL,
            destino TEXT NOT NULL,
            UNIQUE(origen, destino)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            operator_id INTEGER UNIQUE,
            rating REAL,
            logo_url TEXT,
            total_ratings INTEGER,
            number_of_reviews INTEGER,
            bus_score REAL,
            UNIQUE(nombre, operator_id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS amenidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo INTEGER UNIQUE NOT NULL,
            descripcion TEXT NOT NULL
        );
        """)

        # --- TABLA DE VIAJES (Catálogo estático MEJORADO) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS viajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            ruta_id INTEGER NOT NULL,
            fecha_salida DATE NOT NULL,
            hora_salida_programada TEXT NOT NULL,
            hora_llegada_programada TEXT NOT NULL,
            duracion_programada_min INTEGER,
            tipo_bus TEXT,
            es_ac BOOLEAN,
            es_seater BOOLEAN,
            es_sleeper BOOLEAN,
            asientos_totales INTEGER,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE CASCADE,
            UNIQUE(empresa_id, ruta_id, fecha_salida, hora_salida_programada, tipo_bus)
        );
        """)

        # --- TABLA DE HISTORIAL (Dinámica y MEJORADA) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_viajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viaje_id INTEGER NOT NULL,
            fecha_snapshot DATETIME NOT NULL,
            precio_min REAL,
            precio_max REAL,
            asientos_disponibles INTEGER,
            tiene_oferta BOOLEAN DEFAULT FALSE,
            oferta_descripcion TEXT,
            precio_original_min REAL,
            precio_descuento_min REAL,
            url_scrapeada TEXT,
            FOREIGN KEY (viaje_id) REFERENCES viajes(id) ON DELETE CASCADE,
            UNIQUE(viaje_id, fecha_snapshot)
        );
        """)

        # --- TABLAS DE RELACIÓN ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS puntos_parada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viaje_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            direccion TEXT,
            fecha_hora DATETIME,
            tipo TEXT CHECK(tipo IN ('embarque', 'desembarque')) NOT NULL,
            FOREIGN KEY (viaje_id) REFERENCES viajes(id) ON DELETE CASCADE,
            UNIQUE(viaje_id, nombre, fecha_hora, tipo)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS viaje_amenidades (
            viaje_id INTEGER NOT NULL,
            amenidad_id INTEGER NOT NULL,
            PRIMARY KEY (viaje_id, amenidad_id),
            FOREIGN KEY (viaje_id) REFERENCES viajes(id) ON DELETE CASCADE,
            FOREIGN KEY (amenidad_id) REFERENCES amenidades(id) ON DELETE CASCADE
        );
        """)

        # --- TABLA DE ERRORES ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS errores_procesamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT,
            mensaje TEXT,
            detalle_excepcion TEXT,
            fecha_error DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # --- ÍNDICES ---
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_historial_viajes_viaje_id ON historial_viajes(viaje_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_viajes_ruta_fecha ON viajes(ruta_id, fecha_salida);")

        conn.commit()
        logging.info("Esquema de base de datos verificado/creado exitosamente.")
    except sqlite3.Error as e:
        logging.error(f"Error al crear/verificar el esquema de la base de datos: {e}")
    finally:
        if conn:
            conn.close()