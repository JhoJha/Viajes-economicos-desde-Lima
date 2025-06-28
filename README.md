# 🚌 Chaskiway

**Chaskiway** es una aplicación web que recomienda pasajes interprovinciales económicos desde Lima hacia distintos destinos del Perú, integrando información real de precios, clima y atractivos turísticos para ayudar a planificar viajes de forma inteligente.

---

## 🎯 Motivación y Propósito

Buscar pasajes económicos en Perú suele requerir revisar varias plataformas manualmente. Esto consume tiempo y puede llevar a pagar precios elevados por falta de información.

**Chaskiway** nace para:
- Facilitar la búsqueda de pasajes desde Lima optimizando el presupuesto de estudiantes, trabajadores y turistas.
- Cruzar datos de precios, clima y preferencias del usuario.
- Promover el turismo interno y accesible.
- Analizar los datos recolectados para descubrir patrones y generar recomendaciones útiles.

---

## ⚙️ Objetivo General

Desarrollar una aplicación web interactiva que recomiende viajes económicos desde Lima a diferentes regiones del Perú, en función del presupuesto, clima preferido y fecha de viaje, integrando técnicas de scraping, visualización analítica y una interfaz accesible.

---

## 🎯 Objetivos Específicos

- 🧭 Implementar técnicas de scraping para recolectar pasajes desde el portal **RedBus**.
- ⚖️ Incorporar algoritmos simples (sistemas de puntuación o heurísticas) para mejorar la precisión de las recomendaciones.
- 📊 Crear un **dashboard visual** que explore métricas como precios promedio, duración del viaje y distribución por clima.
- 🖥️ Simular una experiencia de usuario realista utilizando **Streamlit** con un diseño claro y responsivo.

---

## 📚 Fuentes de Información

- 🔗 **RedBus** – Scraping de pasajes interprovinciales (destinos, precios, horarios, empresas).
- 🌤️ **Visual Crossing Weather API** – Clima histórico (ej. temperaturas promedio de julio 2024).
- 🖼️ **Pixabay API** – Imágenes representativas de destinos turísticos.

---

## 🧱 Estructura del Proyecto

```

chaskiway/
├── backend/
│   ├── scraping/             # Scraper de RedBus y descarga de clima/imágenes
│   ├── apis/                 # Consultas API para clima e imágenes
│   ├── core/                 # Recomendador y configuración global
│   └── database/             # SQLite y gestor de datos
│
├── frontend/
│   ├── app.py                # App en Streamlit
│   ├── components/           # Inputs, resultados y dashboard
│   └── assets/               # Logos e íconos
│
├── data/
│   ├── raw/                  # Datos como clima\_julio\_2024.csv
│   └── images/               # Imágenes descargadas de destinos
│
├── docs/                     # Presentación, informe técnico
├── tests/                    # Pruebas unitarias
├── README.md
├── requirements.txt
└── main.py

```

---

## 🚀 Tecnologías Usadas

- Python 3
- Streamlit
- SQLite
- APIs públicas (Visual Crossing, Pixabay)
- Git y GitHub

---

## 👨‍💻 Equipo de Desarrollo

- **Jhon Jhayro Villegas Verde** – Backend, lógica del recomendador.
- **David Ojeda Valdiviezo** – Scraping ,Frontend con Streamlit y visualizaciones. .
- **Jonnathan Jesús Pedraza Laboriano** – Scraping, Frontend con Streamlit y visualizaciones.

---

## 📌 Estado del Proyecto

🚧 *En desarrollo* – Actualmente se encuentra en la fase de integración de módulos.  
✅ Scraper validado, API de clima en proceso, frontend inicial funcionando.

---

## 📞 Contacto

Para más información o colaboración, escribe a:  
**jjvillegasv@lamolina.edu.pe**  