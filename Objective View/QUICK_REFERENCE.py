"""
ÍNDICE RÁPIDO DE FUNCIONES - Advanced Analysis Module

Referencia rápida de todas las funciones disponibles en el módulo de análisis avanzado.
"""

# ============================================================================
# FUNCIONES DE ANÁLISIS (advanced_analysis.py)
# ============================================================================

"""
1. analizar_lenguaje_sesgado(texto: str) -> Dict
   ├─ Detecta: Palabras emotivas, intensificadores, patrones sesgados
   ├─ Retorna: emotividad (0-100), palabras_emotivas, score_neutralidad
   └─ Ejemplo:
       resultado = analizar_lenguaje_sesgado("El hermoso logro...")
       print(resultado['emotividad'])  # 75.5

2. analizar_atribucion_fuentes(texto: str) -> Dict
   ├─ Detecta: Citas directas, indirectas, tipos de fuentes
   ├─ Retorna: numero_citas_directas, calidad_fuentes, score_atribucion
   └─ Ejemplo:
       resultado = analizar_atribucion_fuentes("Según experto: ...")
       print(resultado['score_atribucion'])  # 68.3

3. analizar_enfasis_colocacion(titulo: str, subtitulo: str, parrafos: str) -> Dict
   ├─ Detecta: Qué va en título, intro, final, contexto
   ├─ Retorna: temas_titulo, temas_inicio, score_enfasis, tiene_contexto
   └─ Ejemplo:
       resultado = analizar_enfasis_colocacion(title, subtitle, text)
       print(resultado['score_enfasis'])  # 72

4. analizar_equilibrio_perspectivas(texto: str) -> Dict
   ├─ Detecta: Perspectivas múltiples, contrapuntos, críticas
   ├─ Retorna: balance ('equilibrado'/'unilateral'), score_balance
   └─ Ejemplo:
       resultado = analizar_equilibrio_perspectivas("Sin embargo...")
       print(resultado['balance'])  # 'equilibrado'

5. calcular_score_sesgo_total(texto, titulo, subtitulo, parrafos) -> Dict
   ├─ Combina: Todos los análisis en un score único
   ├─ Retorna: score_sesgo_total (0-100), detalles completos
   └─ Ejemplo:
       resultado = calcular_score_sesgo_total(...)
       print(resultado['score_sesgo_total'])  # 42.5

6. generar_reporte_sesgo_detallado(articulo: Dict) -> Dict
   ├─ Usa: Todas las funciones anteriores
   ├─ Retorna: Reporte completo con indicadores y recomendaciones
   └─ Ejemplo:
       reporte = generar_reporte_sesgo_detallado(articulo)
       print(reporte['indicadores_clave'])
"""

# ============================================================================
# FUNCIONES DE VISUALIZACIÓN (visualization_utils.py)
# ============================================================================

"""
1. crear_matriz_comparativa(medios: Dict) -> plt.Figure
   ├─ Crea: Gráfico de barras agrupadas
   ├─ Dimensiones: Objetividad, Fuentes, Perspectivas, Énfasis
   └─ Uso:
       fig = crear_matriz_comparativa(medios_dict)
       st.pyplot(fig)

2. crear_radar_objetividad(medios: Dict) -> plt.Figure
   ├─ Crea: Gráfico radar multidimensional
   ├─ Ejes: Neutralidad, Fuentes, Balance, Contexto, Claridad
   └─ Uso:
       fig = crear_radar_objetividad(medios_dict)
       st.pyplot(fig)

3. crear_tabla_divergencias(divergencias: List) -> str
   ├─ Crea: Tabla HTML con divergencias
   ├─ Columnas: Aspecto, Divergencia, Medios Afectados
   └─ Uso:
       html = crear_tabla_divergencias(divergencias_list)
       st.markdown(html, unsafe_allow_html=True)

4. crear_scorecard_medio(nombre: str, datos: Dict) -> None
   ├─ Muestra: Tarjeta visual con 4 métricas principales
   └─ Uso:
       crear_scorecard_medio("El País", medio_datos)

5. generar_resumen_ejecutivo(analisis: Dict) -> str
   ├─ Genera: Resumen en markdown con puntos clave
   └─ Uso:
       resumen = generar_resumen_ejecutivo(analisis_completo)
       st.markdown(resumen)
"""

# ============================================================================
# FLUJO TÍPICO DE USO
# ============================================================================

"""
OPCIÓN 1: Análisis de un solo artículo
────────────────────────────────────────
from advanced_analysis import generar_reporte_sesgo_detallado

articulo = {
    'id': '123',
    'source': 'El País',
    'title': 'Título',
    'subtitle': 'Subtítulo',
    'body': 'Contenido completo...'
}

reporte = generar_reporte_sesgo_detallado(articulo)
print(f"Score: {reporte['score_sesgo']}")
print(f"Indicadores: {reporte['indicadores_clave']}")


OPCIÓN 2: Análisis manual por dimensiones
──────────────────────────────────────────
from advanced_analysis import (
    analizar_lenguaje_sesgado,
    analizar_atribucion_fuentes,
    analizar_equilibrio_perspectivas,
    calcular_score_sesgo_total
)

texto = "Artículo completo..."
titulo = "Título"
subtitulo = "Subtítulo"

# 1. Lenguaje
lang = analizar_lenguaje_sesgado(texto)
print(f"Emotividad: {lang['emotividad']}")

# 2. Fuentes
fuentes = analizar_atribucion_fuentes(texto)
print(f"Citas directas: {fuentes['numero_citas_directas']}")

# 3. Perspectivas
persp = analizar_equilibrio_perspectivas(texto)
print(f"Balance: {persp['balance']}")

# 4. Score total
total = calcular_score_sesgo_total(texto, titulo, subtitulo, texto[:500])
print(f"Sesgo total: {total['score_sesgo_total']}")


OPCIÓN 3: Análisis con visualizaciones
───────────────────────────────────────
import streamlit as st
from visualization_utils import crear_matriz_comparativa, crear_radar_objetividad

# Datos de varios medios
medios = {
    'El País': {...datos...},
    'La Vanguardia': {...datos...}
}

# Visualizaciones
col1, col2 = st.columns(2)
with col1:
    fig1 = crear_matriz_comparativa(medios)
    st.pyplot(fig1)
with col2:
    fig2 = crear_radar_objetividad(medios)
    st.pyplot(fig2)
"""

# ============================================================================
# ESTRUCTURA DE DATOS RETORNADOS
# ============================================================================

"""
ESTRUCTURA: Resultado de analizar_lenguaje_sesgado()
────────────────────────────────────────────────────
{
    'emotividad': 45.2,                          # 0-100 (más alto = más emotivo)
    'palabras_emotivas_positivas': ['logro'],
    'palabras_emotivas_negativas': ['crisis'],
    'intensificadores': ['claramente'],
    'dudas': ['supuestamente'],
    'patrones_sesgo_detectados': [
        {'tipo': 'personalizacion_negativa', 'ocurrencias': 1}
    ],
    'score_neutralidad': 54.8                    # 0-100 (100 = neutral)
}


ESTRUCTURA: Resultado de generar_reporte_sesgo_detallado()
──────────────────────────────────────────────────────────
{
    'articulo_id': '123',
    'medio': 'El País',
    'score_sesgo': 35.5,                         # 0-100
    'indicadores_clave': [
        'Buen uso de fuentes',
        'Presenta múltiples perspectivas'
    ],
    'analisis_detallado': {
        'score_sesgo_total': 35.5,
        'score_neutralidad': 72.3,
        'score_atribucion': 85.6,
        'score_balance': 78.2,
        'score_enfasis': 68.1,
        'detalles': {
            'lenguaje': {...},
            'fuentes': {...},
            'colocacion': {...},
            'perspectivas': {...}
        }
    }
}


ESTRUCTURA: Datos para crear_matriz_comparativa()
─────────────────────────────────────────────────
{
    'El País': {
        'score_sesgo_0_100': 35,
        'atribucion_fuentes': {'score_calidad_fuentes_0_100': 85},
        'balance_perspectivas': {'score_balance_0_100': 78},
        'enfasis_colocacion': {'score_enfasis_equilibrado_0_100': 72}
    },
    'La Vanguardia': {...}
}
"""

# ============================================================================
# INTERPRETACIÓN DE SCORES
# ============================================================================

"""
SCORE DE SESGO TOTAL (0-100)
────────────────────────────
0-30:   Muy objetivo ✅
        → Lenguaje neutral, buenas fuentes, equilibrado
        → Recomendación: CONFIABLE

30-50:  Mayormente objetivo 👍
        → Generalmente imparcial con ligeros sesgos
        → Recomendación: MAYORMENTE CONFIABLE

50-70:  Parcialmente sesgado ⚠️
        → Sesgo notable, requiere verificación
        → Recomendación: CONTRASTAR CON OTROS MEDIOS

70-100: Muy sesgado 🚩
        → Fuerte sesgo detectado
        → Recomendación: VERIFICAR INFORMACIÓN ANTES DE CREER


SCORE DE NEUTRALIDAD (0-100)
────────────────────────────
0-30:   Muy emotivo 🚩
        → Muchas palabras cargadas, intensificadores
        → Indica falta de objetividad

30-70:  Moderadamente neutral
        → Lenguaje ocasionalmente emotivo

70-100: Muy neutral ✅
        → Lenguaje técnico, factual


SCORE DE ATRIBUCIÓN (0-100)
───────────────────────────
0-30:   Pocas fuentes 🚩
        → Afirmaciones sin fuentes verificables
        → Riesgo: Desinformación

30-70:  Fuentes moderadas
        → Algunas citas pero podría mejorar

70-100: Excelentes fuentes ✅
        → Bien atribuido, citas directas y verificables


SCORE DE BALANCE (0-100)
────────────────────────
0-30:   Unilateral 🚩
        → Solo una perspectiva
        → Falta de equidad editorial

30-70:  Mayormente equilibrado
        → Presenta perspectivas alternas

70-100: Muy equilibrado ✅
        → Múltiples perspectivas consideradas
"""

# ============================================================================
# CASOS DE USO COMUNES
# ============================================================================

"""
CASO 1: Comparar objetividad entre medios
──────────────────────────────────────────
from advanced_analysis import generar_reporte_sesgo_detallado

articulos = [...]  # Lista de artículos de diferentes medios

reportes = [generar_reporte_sesgo_detallado(art) for art in articulos]
reportes_ordenados = sorted(reportes, key=lambda x: x['score_sesgo'])

print("De más objetivo a más sesgado:")
for reporte in reportes_ordenados:
    print(f"{reporte['medio']}: {reporte['score_sesgo']:.1f}/100")


CASO 2: Identificar qué hace un artículo sesgado
─────────────────────────────────────────────────
from advanced_analysis import generar_reporte_sesgo_detallado

reporte = generar_reporte_sesgo_detallado(articulo)

print("Indicadores de sesgo encontrados:")
for indicador in reporte['indicadores_clave']:
    print(f"  • {indicador}")


CASO 3: Encontrar artículos con problemas de fuentes
────────────────────────────────────────────────────
from advanced_analysis import analizar_atribucion_fuentes

for articulo in articulos:
    fuentes = analizar_atribucion_fuentes(articulo['body'])
    if fuentes['numero_citas_directas'] == 0:
        print(f"ALERTA: {articulo['title']} sin citas directas")


CASO 4: Visualizar comparativa de medios
────────────────────────────────────────
import streamlit as st
from visualization_utils import crear_matriz_comparativa

medios_datos = {...}  # Datos procesados
fig = crear_matriz_comparativa(medios_datos)
st.pyplot(fig)

# Usuarios pueden ver instantáneamente qué medio es más objetivo
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
PROBLEMA: Score siempre es similar para todos los artículos
SOLUCIÓN: 
  → Verificar que advanced_analysis esté siendo usado por Groq
  → Ver en utils_groq.py que el prompt incluya todos los análisis
  → Revisar que los artículos sean lo suficientemente diferentes

PROBLEMA: No se detectan palabras emotivas
SOLUCIÓN:
  → Verificar PALABRAS_EMOTIVAS en config.py
  → Asegurarse que las palabras tienen similitud ortográfica
  → Palabras con acentos deben estar normalizadas

PROBLEMA: Score de fuentes siempre bajo
SOLUCIÓN:
  → Algunos artículos de noticia no incluyen citas directas
  → Revisar si las citas están con comillas ("")
  → Confirmar que los artículos tienen sustancia suficiente

PROBLEMA: Visualizaciones no aparecen
SOLUCIÓN:
  → Verificar importaciones en app.py
  → Revisar que matplotlib esté instalado
  → Confirmar que hay datos suficientes (2+ medios)
"""

# ============================================================================
print("✅ Guía rápida de funciones cargada correctamente")
print("Consulta los comentarios en este archivo para ejemplos de uso")
