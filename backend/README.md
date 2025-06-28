# 🧠 Backend – Chaskiway

Este módulo contiene la lógica principal del sistema: recolección de datos (scraping), procesamiento, consulta de APIs externas, y filtrado inteligente de resultados para recomendación.

---

## 📁 Estructura del Backend

- **scraping/**: Obtiene pasajes desde RedBus, clima histórico y descarga imágenes.
- **apis/**: Maneja llamadas a APIs externas (clima, imágenes).
- **core/**: Contiene el 
ecommender.py y configuración global.
- **database/**: Lógica de conexión y manipulación de datos en SQLite.

---

## 🚀 Módulos Clave

| Archivo                | Funcionalidad                                             |
|------------------------|-----------------------------------------------------------|
| 
edbus_scraper.py    | Extrae pasajes desde la API interna de RedBus.            |
| weather_downloader.py| Descarga clima de todo julio 2024 para múltiples destinos.|
| image_downloader.py  | Descarga imágenes desde Pixabay o Unsplash.               |
| 
ecommender.py       | Aplica filtros por clima y precio.                        |
| db_manager.py        | Inserta y consulta datos desde SQLite.                    |
| config.py            | Variables globales, rutas y claves API.                   |

---

## ⚙️ Requisitos

Instala las dependencias desde la raíz del proyecto:

`
pip install -r requirements.txt
`

---

## 📌 Uso

Ejemplo para ejecutar el scraper:

`
python backend/scraping/redbus_scraper.py
`

Ejemplo para correr la lógica del recomendador:

`
python backend/core/recommender.py
`

---

