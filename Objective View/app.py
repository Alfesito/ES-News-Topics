# app.py
import streamlit as st
import json
from datetime import datetime
from utils_gemini import (
    cargar_noticias,
    extraer_tags_unicos,
    filtrar_noticias,
    analizar_con_gemini,
    generar_estadisticas,
    guardar_analisis,
    cargar_analisis_historico,
    buscar_analisis_por_titulo,
    eliminar_analisis,
    exportar_analisis_individual
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Noticias - El Panorama",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<p class="main-header">🔍 Análisis Objetivo de Noticias Multi-Medio</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Selecciona tags y define el tema para generar un análisis con IA</p>', unsafe_allow_html=True)

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información")
    st.markdown("""
    **El Panorama** - Análisis de Noticias
    
    Esta herramienta utiliza **Gemini 2.5** (Google AI) para:
    - Analizar objetivamente noticias de múltiples medios españoles
    - Detectar sesgos y divergencias editoriales
    - Generar estadísticas de cobertura por medio
    
    ---
    
    **Modelos disponibles:**
    - **Flash (2.5)**: Más rápido (recomendado)
    - **Pro (2.5)**: Mejor calidad
    
    **Método:** Análisis en 2 fases optimizado
    
    ---
    
    **Datos**: El Panorama News DB
    """)
    
    st.divider()
    
    # Selector de modelo
    usar_pro = st.checkbox(
        "🚀 Usar Gemini 2.5 Pro",
        help="Mejor calidad pero más lento. Desmarca para usar Flash (recomendado)"
    )
    
    modelo_activo = "Gemini 2.5 Pro" if usar_pro else "Gemini 2.5 Flash"
    st.info(f"Modelo activo: **{modelo_activo}**")

# Inicializar estado de sesión
if 'noticias' not in st.session_state:
    st.session_state.noticias = None
if 'tags_disponibles' not in st.session_state:
    st.session_state.tags_disponibles = []
if 'analisis_resultado' not in st.session_state:
    st.session_state.analisis_resultado = None
if 'analisis_historico' not in st.session_state:
    st.session_state.analisis_historico = cargar_analisis_historico()

# Cargar datos
if st.session_state.noticias is None:
    with st.spinner("📡 Cargando noticias desde GitHub..."):
        try:
            st.session_state.noticias = cargar_noticias()
            st.session_state.tags_disponibles = extraer_tags_unicos(st.session_state.noticias)
            st.success(f"✅ **{len(st.session_state.noticias)}** noticias cargadas con **{len(st.session_state.tags_disponibles)}** tags únicos")
        except Exception as e:
            st.error(f"❌ Error al cargar noticias: {str(e)}")
            st.stop()

# Formulario de configuración
with st.container():
    st.subheader("1️⃣ Configuración del Análisis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Selector de tags
        tags_seleccionados = st.multiselect(
            "🏷️ Selecciona los tags del tema a analizar:",
            options=st.session_state.tags_disponibles,
            help="Puedes seleccionar múltiples tags. Se analizarán todas las noticias que contengan al menos uno.",
            max_selections=10
        )
    
    with col2:
        # Contador de noticias
        if tags_seleccionados:
            # Filtrar sin límite para contar total
            noticias_temp_todas = []
            for noticia in st.session_state.noticias:
                if any(tag in noticia.get('tags', []) for tag in tags_seleccionados):
                    noticias_temp_todas.append(noticia)
            
            total_encontradas = len(noticias_temp_todas)
            noticias_a_analizar = min(total_encontradas, 20)
            
            # Obtener medios de las 20 más recientes
            noticias_temp = filtrar_noticias(st.session_state.noticias, tags_seleccionados, limite=20)
            medios_diferentes = len(set([n['newspaper'] for n in noticias_temp]))
            
            st.metric("📰 Noticias encontradas", total_encontradas)
            
            if total_encontradas > 20:
                st.metric("🔍 Se analizarán", "20 (más recientes)", delta=f"-{total_encontradas - 20}")
                st.info(f"ℹ️ Se usarán las 20 noticias más recientes")
            else:
                st.metric("🔍 Se analizarán", noticias_a_analizar)
            
            st.metric("📺 Medios diferentes", medios_diferentes)
    
    # Input de título
    titulo_tema = st.text_input(
        "📝 Define el título del tema:",
        placeholder="Ej: Caso Ábalos y relación con Pedro Sánchez",
        help="Este será el título del análisis generado",
        max_chars=200
    )

# Verificar si existe análisis previo
if titulo_tema:
    analisis_existente = buscar_analisis_por_titulo(titulo_tema)
    if analisis_existente:
        st.info(f"ℹ️ Ya existe un análisis con este título (versión {analisis_existente.get('metadata', {}).get('version', 1)}). Si generas uno nuevo, se sobrescribirá.")

# Botón de análisis
st.divider()

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    analizar_btn = st.button(
        "🚀 Generar Análisis con IA",
        type="primary",
        disabled=not (tags_seleccionados and titulo_tema),
        use_container_width=True
    )

if analizar_btn:
    # Filtrar noticias (automáticamente limita a 20 más recientes)
    noticias_filtradas = filtrar_noticias(st.session_state.noticias, tags_seleccionados, limite=20)
    
    if len(noticias_filtradas) == 0:
        st.error("❌ No se encontraron noticias con los tags seleccionados")
        st.stop()
    
    # Contar total antes del límite
    total_sin_limite = sum(
        1 for n in st.session_state.noticias 
        if any(tag in n.get('tags', []) for tag in tags_seleccionados)
    )
    
    medios_unicos = len(set([n['newspaper'] for n in noticias_filtradas]))
    
    if total_sin_limite > 20:
        st.info(f"📊 Analizando las **20 noticias más recientes** de {total_sin_limite} encontradas, de **{medios_unicos}** medios diferentes...")
    else:
        st.info(f"📊 Analizando **{len(noticias_filtradas)}** noticias de **{medios_unicos}** medios diferentes...")
    
    # Generar estadísticas cuantitativas
    with st.spinner("📈 Generando estadísticas..."):
        try:
            estadisticas = generar_estadisticas(noticias_filtradas)
        except Exception as e:
            st.error(f"Error al generar estadísticas: {str(e)}")
            estadisticas = {}
    
    # Análisis con Gemini (2 fases)
    with st.spinner("🤖 Analizando con Gemini AI en 2 fases (puede tardar 60-90 segundos)..."):
        try:
            analisis = analizar_con_gemini(
                noticias_filtradas,
                titulo_tema,
                tags_seleccionados,
                usar_pro=usar_pro
            )
            
            # Agregar estadísticas al resultado
            analisis["estadisticas"] = estadisticas
            
            # Guardar en sesión
            st.session_state.analisis_resultado = analisis
            
            # Guardar en archivo con persistencia
            try:
                accion, total = guardar_analisis(analisis)
                
                if accion == "actualizado":
                    st.success(f"✅ Análisis completado y **actualizado** en el histórico (Total: {total} análisis guardados)")
                else:
                    st.success(f"✅ Análisis completado y **añadido** al histórico (Total: {total} análisis guardados)")
                
                # Actualizar histórico en sesión
                st.session_state.analisis_historico = cargar_analisis_historico()
                
            except Exception as e:
                st.warning(f"⚠️ Análisis completado pero no se pudo guardar en archivo: {str(e)}")
            
        except Exception as e:
            st.error(f"❌ Error en el análisis: {str(e)}")
            st.stop()

# Mostrar resultados si existen
if st.session_state.analisis_resultado:
    analisis = st.session_state.analisis_resultado
    
    st.divider()
    st.header("📋 Resultados del Análisis")
    
    # Mostrar metadata del análisis
    if 'metodo' in analisis:
        st.caption(f"Método: {analisis['metodo']} | Modelo: {analisis.get('modelo_usado', 'N/A')} | Noticias: {analisis.get('noticias_analizadas', 0)}")
    
    # Tabs para organizar resultados
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Resumen",
        "📊 Estadísticas",
        "🎯 Sesgos Detectados",
        "🔄 Divergencias",
        "💾 JSON Completo"
    ])
    
    with tab1:
        st.subheader(f"📰 {analisis['tema']}")
        st.write(analisis['resumen_objetivo'])
        
        st.markdown("#### ✅ Puntos en Común")
        for punto in analisis.get('puntos_comunes', []):
            st.markdown(f"- {punto}")
        
        st.markdown("#### 📚 Fuentes Citadas")
        fuentes = analisis.get('fuentes_citadas', [])
        if fuentes:
            for fuente in fuentes:
                st.markdown(f"- {fuente}")
        else:
            st.info("No se identificaron fuentes citadas explícitamente")
        
        st.markdown("#### 🎭 Análisis de Sentimiento")
        sent = analisis.get('analisis_sentimiento', {})
        col1, col2 = st.columns(2)
        col1.metric("Tono General", sent.get('tono_general', 'N/A').title())
        col2.metric("Nivel Sensacionalismo", f"{sent.get('nivel_sensacionalismo_promedio', 0):.2f}")
        if 'descripcion' in sent:
            st.info(sent['descripcion'])
    
    with tab2:
        st.subheader("📊 Estadísticas de Cobertura por Medio")
        
        stats = analisis.get('estadisticas', {})
        if stats:
            st.metric("Total de Artículos Analizados", stats.get('total_articulos_analizados', 0))
            
            st.markdown("---")
            
            for medio, datos in stats.get('distribucion_por_medio', {}).items():
                with st.expander(f"📺 {medio}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Artículos", datos['num_articulos'])
                    col2.metric("% Cobertura", f"{datos['porcentaje_cobertura']}%")
                    
                    primera = datos.get('primera_publicacion')
                    if primera:
                        col3.metric("Primera Publicación", primera[:10])
                    
                    st.markdown("**URLs de los artículos:**")
                    for url in datos.get('urls', []):
                        st.markdown(f"- [{url}]({url})")
        else:
            st.warning("No hay estadísticas disponibles")
    
    with tab3:
        st.subheader("🎯 Sesgos Detectados por Medio")
        
        sesgos = analisis.get('sesgo_detectado', {})
        if sesgos:
            for medio, datos in sesgos.items():
                with st.expander(f"📺 {medio}", expanded=True):
                    st.markdown(f"**Orientación Detectada:** {datos.get('orientacion_detectada', 'N/A')}")
                    
                    nivel = datos.get('nivel_bias', 0)
                    st.progress(nivel, text=f"Nivel de Sesgo: {nivel:.2f}")
                    
                    indicadores = datos.get('indicadores', [])
                    if indicadores:
                        st.markdown("**Indicadores de Sesgo:**")
                        for ind in indicadores:
                            st.markdown(f"- {ind}")
                    else:
                        st.info("No se detectaron indicadores significativos de sesgo")
        else:
            st.info("No se detectaron sesgos significativos")
        
        # Omisiones relevantes
        st.markdown("---")
        st.markdown("#### 🚫 Omisiones Relevantes")
        omisiones = analisis.get('omisiones_relevantes', [])
        if omisiones:
            for om in omisiones:
                st.warning(f"**{om['medio']}**: {om['informacion_omitida']}")
        else:
            st.success("No se detectaron omisiones relevantes entre medios")
    
    with tab4:
        st.subheader("🔄 Divergencias en la Cobertura")
        
        divergencias = analisis.get('divergencias', [])
        if divergencias:
            for div in divergencias:
                st.markdown(f"### 📌 {div['aspecto']}")
                
                for persp in div.get('perspectivas', []):
                    with st.container():
                        st.markdown(f"**{persp['medio']}**")
                        st.write(persp['enfoque'])
                        st.markdown("---")
        else:
            st.success("No se detectaron divergencias significativas entre medios")
    
    with tab5:
        st.subheader("💾 JSON Completo del Análisis")
        
        # Botón de descarga
        json_str = json.dumps(analisis, indent=2, ensure_ascii=False)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        titulo_safe = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in titulo_tema)[:50]
        filename = f"analisis_{titulo_safe}_{timestamp}.json"
        
        st.download_button(
            label="⬇️ Descargar JSON",
            data=json_str,
            file_name=filename,
            mime="application/json",
            use_container_width=True
        )
        
        # Mostrar JSON
        st.json(analisis)

# Sección de Histórico de Análisis
st.divider()
st.header("📚 Histórico de Análisis Guardados")

analisis_historico = st.session_state.analisis_historico

if not analisis_historico:
    st.info("No hay análisis guardados todavía. Genera tu primer análisis arriba.")
else:
    st.write(f"**Total de análisis guardados:** {len(analisis_historico)}")
    
    # Selector de análisis histórico
    titulos_historico = [a['tema'] for a in analisis_historico]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        analisis_seleccionado = st.selectbox(
            "Selecciona un análisis para ver:",
            options=[""] + titulos_historico,
            format_func=lambda x: "-- Selecciona --" if x == "" else x
        )
    
    if analisis_seleccionado and analisis_seleccionado != "":
        # Buscar el análisis completo
        analisis_mostrar = next((a for a in analisis_historico if a['tema'] == analisis_seleccionado), None)
        
        if analisis_mostrar:
            with col2:
                st.write("")
                st.write("")
                exportar_btn = st.button("📥 Exportar", key="export_btn")
                eliminar_btn = st.button("🗑️ Eliminar", key="delete_btn", type="secondary")
            
            # Mostrar metadata
            metadata = analisis_mostrar.get('metadata', {})
            col1, col2 = st.columns(2)
            col1.metric("Versión", metadata.get('version', 1))
            col2.metric("Guardado", metadata.get('guardado_en', 'N/A')[:19])
            
            # Mostrar resumen compacto
            with st.expander("📋 Ver Resumen", expanded=True):
                st.write(analisis_mostrar['resumen_objetivo'])
                
                col1, col2 = st.columns(2)
                col1.metric("Tags", ", ".join(analisis_mostrar.get('tags_analizados', [])))
                col2.metric("Artículos analizados", 
                           analisis_mostrar.get('estadisticas', {}).get('total_articulos_analizados', 'N/A'))
            
            # Botón para ver completo
            if st.button("👁️ Ver Análisis Completo", key="view_full_btn"):
                st.session_state.analisis_resultado = analisis_mostrar
                st.rerun()
            
            # Manejo de exportación
            if exportar_btn:
                try:
                    filename = exportar_analisis_individual(analisis_mostrar)
                    with open(filename, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    st.download_button(
                        label="⬇️ Descargar archivo exportado",
                        data=contenido,
                        file_name=filename.split('/')[-1],
                        mime="application/json",
                        key="download_export_btn"
                    )
                    st.success(f"✅ Análisis exportado correctamente")
                except Exception as e:
                    st.error(f"Error al exportar: {str(e)}")
            
            # Manejo de eliminación
            if eliminar_btn:
                eliminados = eliminar_analisis(analisis_seleccionado)
                if eliminados > 0:
                    st.success(f"🗑️ Análisis '{analisis_seleccionado}' eliminado")
                    st.session_state.analisis_historico = cargar_analisis_historico()
                    st.rerun()
                else:
                    st.error("No se pudo eliminar el análisis")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>El Panorama</strong> - Análisis de Noticias con IA</p>
    <p>Powered by Gemini 2.5 (Google AI) | Desarrollado por Alfesito</p>
    <p style='font-size: 0.8rem; margin-top: 0.5rem;'>Método: Análisis en 2 fases optimizado para reducir tokens</p>
</div>
""", unsafe_allow_html=True)
