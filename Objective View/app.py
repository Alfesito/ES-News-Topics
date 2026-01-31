# app.py
import streamlit as st
import json
from datetime import datetime
from utils_groq import (
    cargar_noticias,
    extraer_tags_unicos,
    filtrar_noticias,
    analizar_con_groq,
    generar_estadisticas,
    guardar_analisis,
    cargar_analisis_historico,
    buscar_analisis_por_titulo,
    eliminar_analisis,
    exportar_analisis_individual
)
from visualization_utils import (
    crear_matriz_comparativa,
    crear_radar_objetividad,
    generar_resumen_ejecutivo
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
    
    Esta herramienta utiliza **Groq API** para:
    - Analizar objetivamente noticias de múltiples medios españoles
    - Responder las **5W+1H** (Qué, Quién, Cuándo, Dónde, Por qué, Cómo)
    - Detectar sesgos y divergencias editoriales
    - Generar estadísticas de cobertura por medio
    
    ---
    
    **Modelos disponibles (GRATIS):**
    - **Llama 3.1 8B**: Ultra rápido (recomendado)
    - **Llama 3.3 70B**: Más potente
    
    **Ventajas de Groq:**
    - ✅ 14,400 análisis/día gratis
    - ✅ Velocidad ultra-rápida (500+ tokens/seg)
    - ✅ Sin límites de input
    - ✅ Arquitectura LPU optimizada
    
    ---
    
    **Datos**: El Panorama News DB
    
    **Registrate en:** [console.groq.com](https://console.groq.com)
    """)
    
    st.divider()
    
    # Selector de modelo
    usar_pro = st.checkbox(
        "🚀 Usar Llama 3.3 70B (más potente)",
        help="Mejor para análisis complejos. Desmarca para Llama 3.1 8B (más rápido)"
    )
    
    modelo_activo = "Llama 3.3 70B" if usar_pro else "Llama 3.1 8B (ultra-rápido)"
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
            noticias_a_analizar = min(total_encontradas, 30)
            
            # Obtener medios de las 30 más recientes
            noticias_temp = filtrar_noticias(st.session_state.noticias, tags_seleccionados, limite=30)
            medios_diferentes = len(set([n['newspaper'] for n in noticias_temp]))
            
            st.metric("📰 Noticias encontradas", total_encontradas)
            
            if total_encontradas > 30:
                st.metric("🔍 Se analizarán", "30 (más recientes)", delta=f"-{total_encontradas - 30}")
                st.info(f"ℹ️ Se usarán las 30 noticias más recientes")
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
    # Filtrar noticias (automáticamente limita a 30 más recientes)
    noticias_filtradas = filtrar_noticias(st.session_state.noticias, tags_seleccionados, limite=30)
    
    if len(noticias_filtradas) == 0:
        st.error("❌ No se encontraron noticias con los tags seleccionados")
        st.stop()
    
    # Contar total antes del límite
    total_sin_limite = sum(
        1 for n in st.session_state.noticias 
        if any(tag in n.get('tags', []) for tag in tags_seleccionados)
    )
    
    medios_unicos = len(set([n['newspaper'] for n in noticias_filtradas]))
    
    if total_sin_limite > 30:
        st.info(f"📊 Analizando las **30 noticias más recientes** de {total_sin_limite} encontradas, de **{medios_unicos}** medios diferentes...")
    else:
        st.info(f"📊 Analizando **{len(noticias_filtradas)}** noticias de **{medios_unicos}** medios diferentes...")
    
    # Generar estadísticas cuantitativas
    with st.spinner("📈 Generando estadísticas..."):
        try:
            estadisticas = generar_estadisticas(noticias_filtradas)
        except Exception as e:
            st.error(f"Error al generar estadísticas: {str(e)}")
            estadisticas = {}
    
    # Análisis con OpenRouter
    progress_placeholder = st.empty()
    
    def actualizar_progreso(mensaje):
        progress_placeholder.info(f"🤖 {mensaje}")
    
    with st.spinner("🤖 Analizando con OpenRouter (30-60 segundos)..."):
        try:
            analisis = analizar_con_groq(
                noticias_filtradas,
                titulo_tema,
                tags_seleccionados,
                usar_pro=usar_pro,
                callback_progreso=actualizar_progreso
            )
            
            # Agregar estadísticas al resultado
            analisis["estadisticas"] = estadisticas
            
            # Guardar en sesión
            st.session_state.analisis_resultado = analisis
            
            # Limpiar placeholder de progreso
            progress_placeholder.empty()
            
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
            progress_placeholder.empty()
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
        # Resumen ejecutivo mejorado
        resumen_ejecutivo = generar_resumen_ejecutivo(analisis)
        st.markdown(resumen_ejecutivo)
        
        st.markdown("---")
        st.subheader(f"📰 {analisis['tema']}")
        st.write(analisis['resumen_objetivo'])
        
        st.markdown("---")
        st.markdown("### 🔍 Análisis 5W+1H")
        
        # Análisis 5W+1H
        analisis_5w1h = analisis.get('analisis_5w1h', {})
        
        if analisis_5w1h:
            # Qué
            with st.expander("❓ **¿Qué ha ocurrido?**", expanded=True):
                st.write(analisis_5w1h.get('que', 'No disponible'))
            
            # Quién
            with st.expander("👥 **¿Quién está involucrado?**", expanded=True):
                st.write(analisis_5w1h.get('quien', 'No disponible'))
            
            # Cuándo
            col1, col2 = st.columns(2)
            with col1:
                with st.expander("📅 **¿Cuándo ocurrió?**", expanded=True):
                    st.write(analisis_5w1h.get('cuando', 'No disponible'))
            
            # Dónde
            with col2:
                with st.expander("📍 **¿Dónde sucedió?**", expanded=True):
                    st.write(analisis_5w1h.get('donde', 'No disponible'))
            
            # Por qué
            with st.expander("💡 **¿Por qué ocurrió?**", expanded=True):
                st.write(analisis_5w1h.get('por_que', 'No disponible'))
            
            # Cómo
            with st.expander("⚙️ **¿Cómo se desarrolló?**", expanded=True):
                st.write(analisis_5w1h.get('como', 'No disponible'))
        else:
            st.warning("No se pudo generar el análisis 5W+1H")
        
        st.markdown("---")
        st.markdown("### ✅ Puntos en Común entre Medios")
        for punto in analisis.get('puntos_comunes', []):
            st.markdown(f"- {punto}")
        
        st.markdown("---")
        st.markdown("### 🎭 Análisis de Sentimiento")
        sent = analisis.get('analisis_sentimiento', {})
        col1, col2 = st.columns(2)
        col1.metric("Tono General", sent.get('tono_general', 'N/A').title())
        col2.metric("Nivel Sensacionalismo", f"{sent.get('nivel_sensacionalismo_promedio', 0):.2f}")
        if 'descripcion' in sent:
            st.info(sent['descripcion'])


    with tab2:
        st.subheader("📊 Estadísticas y Visualizaciones Avanzadas")
        
        stats = analisis.get('estadisticas', {})
        if stats:
            st.metric("Total de Artículos Analizados", stats.get('total_articulos_analizados', 0))
            
            st.markdown("---")
            
            # Visualización: Matriz Comparativa
            analisis_sesgo_detallado = analisis.get('analisis_detallado_sesgo', {})
            if analisis_sesgo_detallado:
                st.markdown("### 📈 Matriz Comparativa de Objetividad")
                fig_matriz = crear_matriz_comparativa(analisis_sesgo_detallado)
                st.pyplot(fig_matriz)
                
                st.markdown("---")
                
                # Visualización: Radar
                st.markdown("### 🎯 Análisis Multidimensional (Radar)")
                fig_radar = crear_radar_objetividad(analisis_sesgo_detallado)
                st.pyplot(fig_radar)
                
                st.markdown("---")
            
            st.markdown("### 📺 Distribución por Medio")
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
        st.subheader("🎯 Análisis Detallado de Sesgos y Objetividad")
        
        # Obtener análisis detallado
        analisis_sesgo_detallado = analisis.get('analisis_detallado_sesgo', {})
        matriz = analisis.get('matriz_comparativa', {})
        
        if matriz:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🏆 Más Objetivo", matriz.get('medio_mas_objetivo', 'N/A'), 
                         f"Score: {matriz.get('score_mas_objetivo', 0):.0f}")
            with col2:
                st.metric("⚠️ Más Sesgado", matriz.get('medio_mas_sesgado', 'N/A'), 
                         f"Score: {matriz.get('score_mas_sesgado', 0):.0f}")
            with col3:
                st.metric("📊 Diferencia", "", f"{matriz.get('diferencia_maxima_score', 0):.0f} pts")
            with col4:
                st.metric("🤝 Consenso", matriz.get('consensus_nivel', 'N/A'))
            
            st.markdown("---")
        
        # Mostrar scores para cada medio
        if analisis_sesgo_detallado:
            st.markdown("### Scores de Objetividad por Medio (0-100, donde 0 = Muy Objetivo)")
            
            # Preparar datos para gráfico
            medios_nombres = []
            scores_sesgo = []
            clasificaciones = []
            
            for medio, datos in analisis_sesgo_detallado.items():
                medios_nombres.append(medio)
                score = datos.get('score_sesgo_0_100', 50)
                scores_sesgo.append(score)
                clasificaciones.append(datos.get('clasificacion', 'Desconocida'))
            
            # Gráfico de barras
            if medios_nombres:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(10, 6))
                colores = ['#2ecc71' if s < 30 else '#f39c12' if s < 50 else '#e74c3c' for s in scores_sesgo]
                ax.barh(medios_nombres, scores_sesgo, color=colores)
                ax.set_xlabel('Score de Sesgo (0=Objetivo, 100=Sesgado)', fontsize=12)
                ax.set_title('Análisis de Objetividad por Medio', fontsize=14, fontweight='bold')
                ax.set_xlim(0, 100)
                for i, v in enumerate(scores_sesgo):
                    ax.text(v + 2, i, f'{v:.0f}', va='center', fontweight='bold')
                st.pyplot(fig)
            
            st.markdown("---")
            
            # Análisis detallado por medio
            st.markdown("### 📺 Análisis Detallado por Medio")
            
            for medio, datos in analisis_sesgo_detallado.items():
                with st.expander(f"🔍 {medio} - {datos.get('clasificacion', 'N/A')}", expanded=True):
                    
                    # Scores principales
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Sesgo Total", f"{datos.get('score_sesgo_0_100', 0):.0f}/100")
                    with col2:
                        st.metric("Neutralidad", f"{datos.get('lenguaje', {}).get('nivel_emotividad_0_100', 50):.0f}/100", delta=None)
                    with col3:
                        st.metric("Fuentes", f"{datos.get('atribucion_fuentes', {}).get('score_calidad_fuentes_0_100', 50):.0f}/100")
                    with col4:
                        st.metric("Balance", f"{datos.get('balance_perspectivas', {}).get('score_balance_0_100', 50):.0f}/100")
                    
                    # Lenguaje
                    lenguaje = datos.get('lenguaje', {})
                    if lenguaje:
                        st.markdown("**🔤 Análisis de Lenguaje**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"- Emotividad: {lenguaje.get('nivel_emotividad_0_100', 0):.0f}%")
                            st.write(f"- Palabras cargadas: {len(lenguaje.get('palabras_cargadas', []))}")
                        with col2:
                            st.write(f"- Intensificadores: {len(lenguaje.get('intensificadores', []))}")
                            st.write(f"- Adjetivos tendenciosos: {len(lenguaje.get('adjetivos_tendenciosos', []))}")
                        
                        if lenguaje.get('palabras_cargadas'):
                            st.caption(f"Palabras cargadas: {', '.join(lenguaje['palabras_cargadas'][:5])}")
                    
                    # Atribución de fuentes
                    fuentes = datos.get('atribucion_fuentes', {})
                    if fuentes:
                        st.markdown("**📚 Atribución de Fuentes**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"- Citas directas: {fuentes.get('citas_directas', 0)}")
                        with col2:
                            st.write(f"- Citas indirectas: {fuentes.get('citas_indirectas', 0)}")
                        with col3:
                            st.write(f"- Sin fuente: {fuentes.get('afirmaciones_sin_fuente', 0)}")
                        
                        tipos = fuentes.get('tipos_fuentes_usadas', [])
                        if tipos:
                            st.caption(f"Tipos de fuentes: {', '.join(tipos)}")
                    
                    # Énfasis
                    enfasis = datos.get('enfasis_colocacion', {})
                    if enfasis:
                        st.markdown("**📌 Énfasis y Colocación**")
                        st.write(f"- Info. principal en título: {enfasis.get('informacion_principal_en_titulo', 'N/A')}")
                        st.write(f"- Proporciona contexto: {'✅ Sí' if enfasis.get('proporciona_contexto') else '❌ No'}")
                    
                    # Perspectivas
                    perspectivas = datos.get('balance_perspectivas', {})
                    if perspectivas:
                        st.markdown("**🔄 Balance de Perspectivas**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"- Solo una perspectiva: {'❌ Sí (Malo)' if perspectivas.get('solo_una_perspectiva') else '✅ No (Bien)'}")
                        with col2:
                            st.write(f"- Menciona críticas: {'✅ Sí' if perspectivas.get('menciona_criticas') else '❌ No'}")
                        with col3:
                            st.write(f"- Posiciones opuestas: {'✅ Sí' if perspectivas.get('menciona_posiciones_opuestas') else '❌ No'}")
                    
                    # Indicadores de sesgo
                    indicadores = datos.get('indicadores_clave_de_sesgo', [])
                    if indicadores:
                        st.markdown("**🚨 Indicadores de Sesgo Detectados**")
                        for ind in indicadores:
                            st.warning(f"→ {ind}")
                    
                    # Puntos fuertes y mejora
                    fortalezas = datos.get('puntos_fuertes', [])
                    mejoras = datos.get('areas_mejora', [])
                    
                    if fortalezas:
                        st.success(f"✅ **Fortalezas**: {', '.join(fortalezas)}")
                    if mejoras:
                        st.info(f"💡 **Áreas de mejora**: {', '.join(mejoras)}")
        
        st.markdown("---")
        
        # Palabras más frecuentes
        palabras_por_medio = analisis.get('palabras_mas_frecuentes_por_medio', {})
        if palabras_por_medio:
            st.markdown("### 📊 Palabras Frecuentes por Medio")
            for medio, palabras in palabras_por_medio.items():
                st.markdown(f"**{medio}:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"✅ Positivas: {', '.join(palabras.get('positivas', [])[:3])}")
                with col2:
                    st.caption(f"❌ Negativas: {', '.join(palabras.get('negativas', [])[:3])}")
                with col3:
                    st.caption(f"⚪ Neutras: {', '.join(palabras.get('neutras', [])[:3])}")
        
        # Omisiones relevantes
        st.markdown("---")
        st.markdown("#### 🚫 Omisiones Relevantes")
        omisiones = analisis.get('omisiones_importantes', [])
        if omisiones:
            for om in omisiones:
                st.warning(f"**{om['medio']}**: {om['informacion_omitida']}")
        else:
            st.success("No se detectaron omisiones relevantes entre medios")


    with tab4:
        st.subheader("🔄 Divergencias Principales en la Cobertura")
        
        divergencias = analisis.get('divergencias_principales', [])
        
        if divergencias:
            st.info(f"Se detectaron **{len(divergencias)}** divergencias significativas entre medios")
            
            for idx, div in enumerate(divergencias, 1):
                with st.expander(f"📌 Divergencia {idx}: {div.get('aspecto', 'Aspecto')}", expanded=(idx == 1)):
                    # Descripción de la divergencia
                    st.markdown(f"**Diferencia detectada:**")
                    st.write(div.get('diferencia', 'No disponible'))
                    
                    # Impacto en la percepción
                    st.markdown(f"**Impacto en la percepción del lector:**")
                    st.info(div.get('impacto_percepcion', 'No disponible'))
                    
                    # Perspectivas de cada medio
                    st.markdown(f"**Perspectivas por medio:**")
                    perspectivas_medios = div.get('perspectivas_medios', {})
                    
                    if perspectivas_medios:
                        for medio, perspectiva in perspectivas_medios.items():
                            st.markdown(f"**{medio}:**")
                            st.write(perspectiva)
                            st.markdown("---")
        else:
            st.success("No se detectaron divergencias significativas entre medios")
        
        # Recomendación para el lector
        st.markdown("---")
        st.markdown("### 💡 Recomendación para Obtener la Visión Más Completa")
        recomendacion = analisis.get('recomendacion_para_lector', '')
        if recomendacion:
            st.info(recomendacion)
        
        # Nueva sección: Cobertura por medio
        st.markdown("---")
        st.subheader("📰 Cobertura Detallada por Medio")
        
        cobertura_por_medio = analisis.get('cobertura_por_medio', {})
        if cobertura_por_medio:
            for medio, detalles in cobertura_por_medio.items():
                with st.expander(f"📺 {medio}", expanded=False):
                    st.markdown(f"**Enfoque Principal:** {detalles.get('enfoque_principal', 'N/A')}")
                    st.markdown(f"**Tono:** {detalles.get('tono', 'N/A')}")
                    
                    elementos = detalles.get('elementos_destacados', [])
                    if elementos:
                        st.markdown("**Elementos Destacados:**")
                        for elem in elementos:
                            st.markdown(f"- {elem}")


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
    <p>Powered by OpenRouter (Llama 3.3 70B / DeepSeek R1) | Desarrollado por Alfesito</p>
    <p style='font-size: 0.8rem; margin-top: 0.5rem;'>Análisis gratuito sin límites de cuota</p>
</div>
""", unsafe_allow_html=True)
