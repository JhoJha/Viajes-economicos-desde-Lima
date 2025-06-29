# Contenido COMPLETO y FINAL para: app.py (con Estética Optimizada)

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys
from pathlib import Path

# --- 1. CONFIGURACIÓN INICIAL Y CARGA DE DATOS ---
sys.path.append(str(Path(__file__).resolve().parent))
from backend.database.data_provider import load_all_data_for_frontend

st.set_page_config(
    page_title="Chaskiway | Descubre tu Próximo Viaje",
    page_icon="🚌",
    layout="wide"
)

@st.cache_data
def get_data():
    """Función wrapper para cachear la carga de datos."""
    df = load_all_data_for_frontend()
    if not df.empty and 'fecha_salida' in df.columns:
        df['fecha_salida'] = pd.to_datetime(df['fecha_salida'])
    return df

df_viajes = get_data()

# --- FUNCIÓN DEL TERMÓMETRO DE PRECIOS ---
def get_price_indicator(price, avg_price):
    if avg_price is None or pd.isna(avg_price) or avg_price == 0:
        return ""
    
    diff_percent = ((price - avg_price) / avg_price) * 100
    
    if diff_percent < -10:
        return f"<span class='price-indicator price-good'>¡Oferta! {diff_percent:.0f}%</span>"
    elif diff_percent > 10:
        return f"<span class='price-indicator price-high'>+{diff_percent:.0f}%</span>"
    else:
        return f"<span class='price-indicator price-normal'>Precio normal</span>"

# --- 2. ESTILOS MEJORADOS Y OPTIMIZADOS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary-color: #c7463c; --primary-light: #e8554a; --accent-color: #f7931e;
    --text-primary: #1a1a1a; --text-secondary: #6b7280; --text-muted: #9ca3af;
    --background: #fefefe; --surface: #ffffff; --surface-hover: #f9fafb;
    --border: #e5e7eb; --border-light: #f3f4f6; --success: #10b981;
    --warning: #f59e0b; --danger: #ef4444; --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1); --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px; --spacing-xs: 8px;
    --spacing-sm: 16px; --spacing-md: 24px; --spacing-lg: 32px; --spacing-xl: 48px;
    --transition: all 0.2s ease;
}

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
.main .block-container { background: var(--background); padding-top: var(--spacing-md); padding-bottom: var(--spacing-lg); max-width: 1200px; }
.main-header { text-align: center; padding: var(--spacing-md) var(--spacing-lg); margin-bottom: var(--spacing-lg); background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%); border-radius: var(--radius-lg); color: white; box-shadow: var(--shadow-md); }
.main-header h1 { color: white; font-weight: 700; font-size: 2.25rem; margin-bottom: var(--spacing-xs); text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.main-header h3 { color: rgba(255,255,255,0.9); font-weight: 400; font-size: 1.1rem; margin: 0; }
.filter-container { background: var(--surface); border-radius: var(--radius-lg); padding: var(--spacing-lg); margin: var(--spacing-lg) 0; border: 1px solid var(--border); box-shadow: var(--shadow-sm); transition: var(--transition); }
.filter-container:hover { box-shadow: var(--shadow-md); }
.destination-card { background: var(--surface); border-radius: var(--radius-md); padding: var(--spacing-md); margin-bottom: var(--spacing-sm); border: 1px solid var(--border-light); border-left: 3px solid var(--primary-color); transition: var(--transition); cursor: pointer; }
.destination-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); border-left-color: var(--accent-color); background: var(--surface-hover); }
.company-name { font-weight: 600; color: var(--text-primary); font-size: 1.125rem; margin-bottom: var(--spacing-xs); line-height: 1.4; }
.price-primary { color: var(--primary-color); font-weight: 700; font-size: 1.75rem; line-height: 1; }
.trip-details { color: var(--text-secondary); margin-top: var(--spacing-sm); font-size: 0.9rem; line-height: 1.5; display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.trip-detail-item { display: flex; align-items: center; gap: 4px; }
.price-indicator { font-size: 0.75rem; font-weight: 600; padding: 4px var(--spacing-xs); border-radius: 20px; display: inline-block; margin-top: 4px; }
.price-good { background: rgba(16, 185, 129, 0.1); color: var(--success); }
.price-high { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
.price-normal { background: rgba(107, 114, 128, 0.1); color: var(--text-muted); }
.rating-badge { background: var(--accent-color); color: white; padding: 4px var(--spacing-xs); border-radius: 20px; font-size: 0.8rem; font-weight: 600; box-shadow: var(--shadow-sm); display: inline-flex; align-items: center; gap: 2px; }
.stButton > button { background: var(--primary-color) !important; color: white !important; border: none !important; border-radius: var(--radius-md) !important; padding: 0.75rem 2rem !important; font-weight: 600 !important; font-size: 1rem !important; transition: var(--transition) !important; box-shadow: var(--shadow-sm) !important; text-transform: none !important; letter-spacing: normal !important; }
.stButton > button:hover { background: var(--primary-light) !important; transform: translateY(-1px) !important; box-shadow: var(--shadow-md) !important; }
.stTabs [data-baseweb="tab-list"] { gap: var(--spacing-sm); background: var(--surface); padding: var(--spacing-xs); border-radius: var(--radius-md); box-shadow: var(--shadow-sm); border: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { background: transparent; border-radius: var(--radius-sm); padding: var(--spacing-xs) var(--spacing-sm); transition: var(--transition); font-weight: 500; color: var(--text-secondary); }
.stTabs [aria-selected="true"] { background: var(--primary-color) !important; color: white !important; }
.section-spacing { margin: var(--spacing-lg) 0; }
.content-spacing { margin: var(--spacing-md) 0; }
.success-message { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: var(--success); padding: var(--spacing-sm); border-radius: var(--radius-md); margin: var(--spacing-sm) 0; }
.warning-message { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); color: var(--warning); padding: var(--spacing-sm); border-radius: var(--radius-md); margin: var(--spacing-sm) 0; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚌 Chaskiway</h1>
    <h3>Encuentra tu viaje ideal por el Perú</h3>
</div>
""", unsafe_allow_html=True)

# --- 3. ESTRUCTURA DE PESTAÑAS ---
tabs = st.tabs(["🧭 Buscar Viajes", "📊 Analytics"])

# --- 4. PESTAÑA RECOMENDADOR ---
with tabs[0]:
    st.markdown("<h2 style='text-align: center; color: var(--text-primary); margin-bottom: var(--spacing-sm); font-weight: 600;'>Encuentra tu próxima aventura</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: var(--text-secondary); font-size: 1rem; margin-bottom: var(--spacing-lg);'>Configura tus preferencias y descubre los mejores destinos</p>", unsafe_allow_html=True)

    if df_viajes.empty:
        st.error("No hay datos de viajes disponibles. Por favor, ejecuta el pipeline de datos.")
    else:
        with st.container():
            st.markdown('<div class="filter-container">', unsafe_allow_html=True)
            
            modo_viaje = st.radio(
                "Tipo de viaje:",
                ["✈️ Solo Ida", "🔄 Viaje Redondo (Próximamente)"],
                horizontal=True
            )
            
            st.markdown('<div class="content-spacing"></div>', unsafe_allow_html=True)
            
            col_ruta1, col_ruta2 = st.columns(2, gap="large")
            with col_ruta1:
                origenes = sorted(df_viajes['origen'].unique())
                origen_seleccionado = st.selectbox("📍 Origen", origenes, index=origenes.index("Lima") if "Lima" in origenes else 0)

            with col_ruta2:
                destinos_posibles = sorted(df_viajes[df_viajes['origen'] == origen_seleccionado]['destino'].unique())
                opciones_destino = ["Cualquier destino"] + destinos_posibles
                destino_seleccionado = st.selectbox("🎯 Destino", opciones_destino)

            st.markdown('<div class="content-spacing"></div>', unsafe_allow_html=True)

            if modo_viaje == "✈️ Solo Ida":
                col_fecha, col_presupuesto, col_clima = st.columns(3, gap="large")
                with col_fecha:
                    fecha_ida = st.date_input("🗓️ Fecha de viaje", value=date(2025, 7, 15), min_value=date.today())
                with col_presupuesto:
                    precio_max_disponible = int(df_viajes['precio_min'].max())
                    presupuesto = st.slider("💰 Presupuesto máximo (S/.)", 0, precio_max_disponible, 150, 10)
                with col_clima:
                    clima = st.selectbox("☀️ Clima preferido", ["Cualquiera", "Cálido", "Templado", "Frío"])
            else:
                # Placeholder para viaje redondo
                st.info("La búsqueda de viajes redondos estará disponible pronto.")

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="content-spacing"></div>', unsafe_allow_html=True)
        
        if st.button("🔍 Buscar Viajes", type="primary", use_container_width=True):
            
            if modo_viaje == "✈️ Solo Ida":
                fecha_ida_ts = pd.to_datetime(fecha_ida)
                
                resultados = df_viajes[
                    (df_viajes['origen'] == origen_seleccionado) &
                    (df_viajes['precio_min'] <= presupuesto) &
                    (df_viajes['fecha_salida'] == fecha_ida_ts)
                ].copy()

                if not resultados.empty:
                    resultados['score'] = ((resultados['rating'].fillna(3.0) * 15) - (resultados['precio_min'] * 0.6) + (resultados['tiene_oferta'].fillna(0) * 25))
                    resultados = resultados.sort_values('score', ascending=False)

                st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)

                if not resultados.empty:
                    if destino_seleccionado != "Cualquier destino":
                        resultados_filtrados = resultados[resultados['destino'] == destino_seleccionado]
                        if not resultados_filtrados.empty:
                            st.markdown(f'<div class="success-message">🎉 Encontramos {len(resultados_filtrados)} opciones de {origen_seleccionado} a {destino_seleccionado}</div>', unsafe_allow_html=True)
                            for _, row in resultados_filtrados.iterrows():
                                price_indicator_html = get_price_indicator(row['precio_min'], row['precio_promedio_ruta'])
                                st.markdown(f"""
                                <div class="destination-card">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--spacing-sm);">
                                        <div class="company-name">{row['empresa']}</div>
                                        <div class="rating-badge">{row['rating']:.1f} ⭐</div>
                                    </div>
                                    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: var(--spacing-xs);">
                                        <div class="price-primary">S/ {row['precio_min']:.0f}</div>
                                        {price_indicator_html}
                                    </div>
                                    <div class="trip-details">
                                        <div class="trip-detail-item">🚌 {row['tipo_bus']}</div>
                                        <div class="trip-detail-item">⏰ {row['hora_salida_programada']} → {row['hora_llegada_programada']}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="warning-message">No encontramos viajes a {destino_seleccionado} con tus criterios.</div>', unsafe_allow_html=True)
                    
                    else:
                        destinos_encontrados = resultados['destino'].unique()
                        st.markdown(f'<div class="success-message">🎉 Encontramos {len(destinos_encontrados)} destinos desde {origen_seleccionado}</div>', unsafe_allow_html=True)
                        st.info("💡 Haz clic en un destino para ver todas las opciones disponibles")

                        for destino in destinos_encontrados:
                            viajes_a_destino = resultados[resultados['destino'] == destino]
                            precio_mas_bajo = viajes_a_destino['precio_min'].min()
                            mejor_rating = viajes_a_destino['rating'].max()
                            
                            with st.expander(f"📍 **{destino}** • Desde S/ {precio_mas_bajo:.0f} • Rating {mejor_rating:.1f}⭐ • {len(viajes_a_destino)} opciones"):
                                for _, row in viajes_a_destino.iterrows():
                                    price_indicator_html = get_price_indicator(row['precio_min'], row['precio_promedio_ruta'])
                                    st.markdown(f"""
                                    <div class="destination-card">
                                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--spacing-sm);">
                                            <div class="company-name">{row['empresa']}</div>
                                            <div class="rating-badge">{row['rating']:.1f} ⭐</div>
                                        </div>
                                        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: var(--spacing-xs);">
                                            <div class="price-primary">S/ {row['precio_min']:.0f}</div>
                                            {price_indicator_html}
                                        </div>
                                        <div class="trip-details">
                                            <div class="trip-detail-item">🚌 {row['tipo_bus']}</div>
                                            <div class="trip-detail-item">⏰ {row['hora_salida_programada']} → {row['hora_llegada_programada']}</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-message">😔 No encontramos viajes con tus criterios. Intenta ser más flexible.</div>', unsafe_allow_html=True)
            
            else:
                st.info("🚧 La búsqueda de viajes redondos estará disponible pronto")

# --- 5. PESTAÑA DE ANALYTICS ---
with tabs[1]:
    st.header("📊 Dashboard de Analytics")
    st.info("📈 Esta sección será desarrollada por el equipo de analytics")