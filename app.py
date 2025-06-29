# Contenido 100% COMPLETO y FINAL para: app.py (con Diseño Compacto y Eficiente)

import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import sys
from pathlib import Path
import time

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

# --- FUNCIONES DE AYUDA ---
def get_price_indicator(price, avg_price):
    if avg_price is None or pd.isna(avg_price) or avg_price == 0: return ""
    diff_percent = ((price - avg_price) / avg_price) * 100
    if diff_percent < -10: return f"<span class='price-indicator price-good'>¡Oferta! {diff_percent:.0f}%</span>"
    elif diff_percent > 10: return f"<span class='price-indicator price-high'>+{diff_percent:.0f}%</span>"
    else: return f"<span class='price-indicator price-normal'>Normal</span>"

def format_time_am_pm(time_str_24h):
    if not time_str_24h or not isinstance(time_str_24h, str): return "N/A"
    try:
        return datetime.strptime(time_str_24h, '%H:%M:%S').strftime('%I:%M %p')
    except ValueError:
        return time_str_24h

def find_round_trips(df_ida, df_vuelta):
    combinaciones = []
    empresas_comunes = set(df_ida['empresa']).intersection(set(df_vuelta['empresa']))
    for empresa in empresas_comunes:
        viajes_ida_empresa = df_ida[df_ida['empresa'] == empresa]
        viajes_vuelta_empresa = df_vuelta[df_vuelta['empresa'] == empresa]
        for _, ida_row in viajes_ida_empresa.iterrows():
            for _, vuelta_row in viajes_vuelta_empresa.iterrows():
                combinaciones.append({'empresa_ida': empresa, 'empresa_vuelta': empresa, 'precio_total': ida_row['precio_min'] + vuelta_row['precio_min'], 'score_combinado': (ida_row['score'] + vuelta_row['score']) / 2, 'ida': ida_row, 'vuelta': vuelta_row})
    top_ida = df_ida.nsmallest(3, 'precio_min')
    top_vuelta = df_vuelta.nsmallest(3, 'precio_min')
    for _, ida_row in top_ida.iterrows():
        for _, vuelta_row in top_vuelta.iterrows():
            if not any(c['ida']['viaje_id'] == ida_row['viaje_id'] and c['vuelta']['viaje_id'] == vuelta_row['viaje_id'] for c in combinaciones):
                combinaciones.append({'empresa_ida': ida_row['empresa'], 'empresa_vuelta': vuelta_row['empresa'], 'precio_total': ida_row['precio_min'] + vuelta_row['precio_min'], 'score_combinado': (ida_row['score'] + vuelta_row['score']) / 2, 'ida': ida_row, 'vuelta': vuelta_row})
    if not combinaciones: return pd.DataFrame()
    return pd.DataFrame(combinaciones).sort_values('score_combinado', ascending=False)

# --- 2. ESTILOS COMPACTOS Y PROFESIONALES ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {
    --primary-color: #d9534f; --accent-color: #f7931e; --text-primary: #1a1a1a;
    --text-secondary: #4a5568; --background: #f9fafb; --surface: #ffffff;
    --border: #e5e7eb; --success: #10b981; --danger: #ef4444; --text-muted: #718096;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05); --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --radius-md: 10px; --radius-lg: 12px; --transition: all 0.2s ease-in-out;
}
* { font-family: 'Inter', sans-serif; }
.main .block-container { padding-top: 1rem; padding-bottom: 2rem; }
.main-header { text-align: center; padding: 1.5rem 1rem; margin-bottom: 1rem; background: linear-gradient(135deg, var(--primary-color) 0%, #e8554a 100%); border-radius: var(--radius-lg); color: white; box-shadow: var(--shadow-md); }
.main-header h1 { font-weight: 700; font-size: 1.8rem; line-height: 1.2; margin: 0; }
.main-header h3 { font-weight: 400; font-size: 0.95rem; opacity: 0.9; margin-top: 0.25rem; }
.filter-container { background: var(--surface); border-radius: var(--radius-lg); padding: 1.2rem 1.5rem; margin: 1rem 0; border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
.results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
.destination-card { background: var(--surface); border-radius: var(--radius-md); padding: 1rem; border: 1px solid var(--border); border-left: 4px solid var(--primary-color); box-shadow: var(--shadow-sm); transition: var(--transition); display: flex; flex-direction: column; justify-content: space-between; }
.destination-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); border-left-color: var(--accent-color); }
.company-name { font-weight: 600; font-size: 1.1rem; color: var(--text-primary); }
.price-primary { font-weight: 700; font-size: 1.5rem; color: var(--primary-color); }
.trip-details { font-weight: 500; font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.75rem; }
.price-indicator { font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 12px; }
.price-good { background: rgba(16, 185, 129, 0.1); color: var(--success); }
.price-high { background: rgba(239, 68, 68, 0.1); color: var(--danger); }
.price-normal { background: rgba(107, 114, 128, 0.1); color: var(--text-muted); }
.rating-badge { background: var(--accent-color); color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }
.stButton > button { padding: 0.6rem 1.5rem !important; font-size: 0.95rem !important; }
.visual-separator { height: 1px; background: var(--border); margin: 1rem 0; }
.skeleton-card { border-radius: var(--radius-lg); padding: 1rem; background: var(--surface); border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
.skeleton { background: #e2e8f0; border-radius: 8px; }
.skeleton.title { height: 20px; width: 60%; margin-bottom: 0.75rem; }
.skeleton.price { height: 28px; width: 40%; margin-bottom: 1rem; }
.skeleton.text { height: 14px; width: 80%; }
.skeleton-card .skeleton { animation: shimmer 1.5s infinite linear; background-image: linear-gradient(90deg, #e2e8f0 0px, #f8fafc 40px, #e2e8f0 80px); background-size: 600px; }
@keyframes shimmer { 0% { background-position: -300px 0; } 100% { background-position: 300px 0; } }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""<div class="main-header"><h1>🚌 Chaskiway</h1><h3>Encuentra tu viaje ideal por el Perú</h3></div>""", unsafe_allow_html=True)

# --- ESTRUCTURA DE PESTAÑAS ---
tabs = st.tabs(["🧭 Buscar Viajes", "📊 Analytics"])

# --- PESTAÑA RECOMENDADOR ---
with tabs[0]:
    if df_viajes.empty:
        st.error("No hay datos de viajes disponibles. Por favor, ejecuta el pipeline de datos.")
    else:
        with st.container():
            st.markdown('<div class="filter-container">', unsafe_allow_html=True)
            
            modo_viaje = st.radio("Tipo de viaje:", ["✈️ Solo Ida", "🔄 Viaje Redondo"], horizontal=True, label_visibility="collapsed")
            
            col1, col2, col3 = st.columns(3, gap="medium")
            with col1:
                origenes = sorted(df_viajes['origen'].unique())
                origen_seleccionado = st.selectbox("📍 Origen", origenes, index=origenes.index("Lima") if "Lima" in origenes else 0)
            with col2:
                destinos_posibles = sorted(df_viajes[df_viajes['origen'] == origen_seleccionado]['destino'].unique())
                if modo_viaje == "✈️ Solo Ida":
                    opciones_destino = ["Cualquier destino"] + destinos_posibles
                else:
                    opciones_destino = destinos_posibles
                destino_seleccionado = st.selectbox("🎯 Destino", opciones_destino)
            with col3:
                precio_max_disponible = int(df_viajes['precio_min'].max())
                presupuesto = st.slider("💰 Presupuesto (S/.)", 0, precio_max_disponible, 150, 10)

            col_fecha1, col_fecha2, col_clima_placeholder = st.columns(3, gap="medium")
            with col_fecha1:
                fecha_ida = st.date_input("🗓️ Fecha de ida", value=date(2025, 7, 15), min_value=date.today())
            if modo_viaje == "🔄 Viaje Redondo":
                with col_fecha2:
                    fecha_vuelta = st.date_input("🗓️ Fecha de vuelta", value=fecha_ida + timedelta(days=7), min_value=fecha_ida)
            
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🔍 Buscar Viajes", type="primary", use_container_width=True):
            placeholder = st.empty()
            with placeholder.container():
                st.markdown('<div class="results-grid">', unsafe_allow_html=True)
                for _ in range(3):
                    st.markdown("""<div class="skeleton-card"><div class="skeleton title"></div><div class="skeleton price"></div><div class="skeleton text"></div></div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            time.sleep(0.5)

            # --- LÓGICA PARA MODO SOLO IDA ---
            if modo_viaje == "✈️ Solo Ida":
                fecha_ida_ts = pd.to_datetime(fecha_ida)
                resultados = df_viajes[(df_viajes['origen'] == origen_seleccionado) & (df_viajes['precio_min'] <= presupuesto) & (df_viajes['fecha_salida'] == fecha_ida_ts)].copy()
                if not resultados.empty:
                    resultados['score'] = ((resultados['rating'].fillna(3.0) * 15) - (resultados['precio_min'] * 0.6) + (resultados['tiene_oferta'].fillna(0) * 25))
                    resultados = resultados.sort_values('score', ascending=False)
                
                placeholder.empty()
                st.markdown('<div class="visual-separator"></div>', unsafe_allow_html=True)

                if not resultados.empty:
                    if destino_seleccionado != "Cualquier destino":
                        resultados_filtrados = resultados[resultados['destino'] == destino_seleccionado]
                        if not resultados_filtrados.empty:
                            st.success(f"🎉 {len(resultados_filtrados)} opciones encontradas para {origen_seleccionado} → {destino_seleccionado}")
                            st.markdown('<div class="results-grid">', unsafe_allow_html=True)
                            for _, row in resultados_filtrados.iterrows():
                                st.markdown(f"""
                                <div class="destination-card">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start;"><div class="company-name">{row['empresa']}</div><div class="rating-badge">{row['rating']:.1f} ⭐</div></div>
                                    <div style="margin-top: 0.75rem;"><div class="price-primary">S/ {row['precio_min']:.0f}</div>{get_price_indicator(row['precio_min'], row['precio_promedio_ruta'])}</div>
                                    <div class="trip-details"><span>🚌 {row['tipo_bus']}</span><span>⏰ {format_time_am_pm(row['hora_salida_programada'])} → {format_time_am_pm(row['hora_llegada_programada'])}</span></div>
                                </div>""", unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.warning(f"No se encontraron viajes a {destino_seleccionado} con tus criterios.")
                    else:
                        destinos_encontrados = resultados['destino'].unique()
                        st.success(f"🎉 ¡Encontramos {len(destinos_encontrados)} destinos desde {origen_seleccionado}!")
                        for destino in destinos_encontrados:
                            viajes_a_destino = resultados[resultados['destino'] == destino]
                            precio_mas_bajo = viajes_a_destino['precio_min'].min()
                            with st.expander(f"📍 **{destino}** • Desde S/ {precio_mas_bajo:.0f} • {len(viajes_a_destino)} opciones"):
                                st.markdown('<div class="results-grid">', unsafe_allow_html=True)
                                for _, row in viajes_a_destino.iterrows():
                                    st.markdown(f"""
                                    <div class="destination-card">
                                        <div style="display: flex; justify-content: space-between; align-items: flex-start;"><div class="company-name">{row['empresa']}</div><div class="rating-badge">{row['rating']:.1f} ⭐</div></div>
                                        <div style="margin-top: 0.75rem;"><div class="price-primary">S/ {row['precio_min']:.0f}</div>{get_price_indicator(row['precio_min'], row['precio_promedio_ruta'])}</div>
                                        <div class="trip-details"><span>🚌 {row['tipo_bus']}</span><span>⏰ {format_time_am_pm(row['hora_salida_programada'])} → {format_time_am_pm(row['hora_llegada_programada'])}</span></div>
                                    </div>""", unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("😔 No encontramos viajes con tus criterios. Intenta ser más flexible.")
            
            # --- LÓGICA PARA MODO VIAJE REDONDO ---
            elif modo_viaje == "🔄 Viaje Redondo":
                fecha_ida_ts = pd.to_datetime(fecha_ida)
                df_ida = df_viajes[(df_viajes['origen'] == origen_seleccionado) & (df_viajes['destino'] == destino_seleccionado) & (df_viajes['precio_min'] <= presupuesto) & (df_viajes['fecha_salida'] == fecha_ida_ts)].copy()
                fecha_vuelta_ts = pd.to_datetime(fecha_vuelta)
                df_vuelta = df_viajes[(df_viajes['origen'] == destino_seleccionado) & (df_viajes['destino'] == origen_seleccionado) & (df_viajes['precio_min'] <= presupuesto) & (df_viajes['fecha_salida'] == fecha_vuelta_ts)].copy()

                placeholder.empty()
                st.markdown('<div class="visual-separator"></div>', unsafe_allow_html=True)

                if df_ida.empty or df_vuelta.empty:
                    st.warning("No se encontraron viajes de ida o de vuelta para las fechas y filtros seleccionados.")
                else:
                    df_ida['score'] = ((df_ida['rating'].fillna(3.0) * 15) - (df_ida['precio_min'] * 0.6) + (df_ida['tiene_oferta'].fillna(0) * 25))
                    df_vuelta['score'] = ((df_vuelta['rating'].fillna(3.0) * 15) - (df_vuelta['precio_min'] * 0.6) + (df_vuelta['tiene_oferta'].fillna(0) * 25))
                    df_resultados_redondos = find_round_trips(df_ida, df_vuelta)

                    if df_resultados_redondos.empty:
                        st.warning("No se pudieron encontrar combinaciones de viaje redondo con los criterios actuales.")
                    else:
                        st.success(f"🎉 ¡Encontramos {len(df_resultados_redondos)} excelentes opciones de viaje redondo!")
                        st.markdown('<div class="results-grid">', unsafe_allow_html=True)
                        for _, combo in df_resultados_redondos.head(10).iterrows():
                            ida = combo['ida']
                            vuelta = combo['vuelta']
                            st.markdown(f"""
                            <div class="destination-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 1rem;">
                                    <div>
                                        <div class="company-name">{ida['empresa'] if ida['empresa'] == vuelta['empresa'] else f"{ida['empresa']} / {vuelta['empresa']}"}</div>
                                        <div class="rating-badge">{(ida['rating'] + vuelta['rating'])/2:.1f} ⭐ (Promedio)</div>
                                    </div>
                                    <div style="text-align: right;"><span style="font-size: 0.8rem; color: var(--text-secondary);">Total</span><div class="price-primary">S/ {combo['precio_total']:.0f}</div></div>
                                </div>
                                <div class="trip-details" style="margin-top: 0; flex-direction: column; gap: 0.5rem;">
                                    <div><b>✈️ Ida:</b> {format_time_am_pm(ida['hora_salida_programada'])} → {format_time_am_pm(ida['hora_llegada_programada'])}<span style="float: right; font-weight: 600;">S/ {ida['precio_min']:.0f}</span></div>
                                    <div><b>🔄 Vuelta:</b> {format_time_am_pm(vuelta['hora_salida_programada'])} → {format_time_am_pm(vuelta['hora_llegada_programada'])}<span style="float: right; font-weight: 600;">S/ {vuelta['precio_min']:.0f}</span></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. PESTAÑA DE ANALYTICS ---
with tabs[1]:
    st.header("📊 Dashboard de Analytics")
    st.info("📈 Esta sección será desarrollada por el equipo de analytics")