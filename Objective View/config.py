# Configuración de Objective View - Features y Settings

# ============= FEATURES DE ANÁLISIS =============

# Activar análisis avanzado de lenguaje sesgado
ENABLE_ADVANCED_LANGUAGE_ANALYSIS = True

# Activar análisis de fuentes y atribución
ENABLE_SOURCE_ATTRIBUTION_ANALYSIS = True

# Activar análisis de énfasis y colocación
ENABLE_EMPHASIS_ANALYSIS = True

# Activar análisis de balance de perspectivas
ENABLE_PERSPECTIVE_BALANCE_ANALYSIS = True

# ============= FEATURES DE VISUALIZACIÓN =============

# Activar gráfico de barras horizontal de sesgos
ENABLE_BIAS_BAR_CHART = True

# Activar matriz comparativa (4D)
ENABLE_COMPARISON_MATRIX = True

# Activar gráfico radar multidimensional
ENABLE_RADAR_CHART = True

# Activar palabras frecuentes por medio
ENABLE_WORD_FREQUENCY = True

# Activar scorecard por medio
ENABLE_SCORECARD = True

# ============= CONFIGURACIÓN DE SCORES =============

# Peso de cada dimensión en el score final (debe sumar 1.0)
SCORE_WEIGHTS = {
    'neutralidad': 0.30,      # Neutralidad del lenguaje
    'atribucion': 0.20,       # Calidad de fuentes
    'balance': 0.30,          # Balance de perspectivas
    'enfasis': 0.20           # Énfasis adecuado
}

# Umbrales de clasificación
SCORE_THRESHOLDS = {
    'muy_objetivo': 30,          # 0-30: Muy objetivo
    'mayormente_objetivo': 50,   # 30-50: Mayormente objetivo
    'parcialmente_sesgado': 70   # 50-70: Parcialmente sesgado
    # 70-100: Muy sesgado
}

# Colores para gráficos
SCORE_COLORS = {
    'muy_objetivo': '#2ecc71',        # Verde
    'mayormente_objetivo': '#27ae60', # Verde oscuro
    'parcialmente_sesgado': '#f39c12', # Naranja
    'muy_sesgado': '#e74c3c'         # Rojo
}

# ============= PALABRAS CLAVE PARA ANÁLISIS =============

# Palabras emotivas positivas (fuerte)
PALABRAS_POSITIVAS_FUERTES = [
    'excelente', 'triunfo', 'victoria', 'éxito', 'heroico', 'brillante', 'espectacular', 'magnífico'
]

# Palabras emotivas negativas (fuerte)
PALABRAS_NEGATIVAS_FUERTES = [
    'catastrofe', 'desastre', 'fracaso', 'derrota', 'tragedia', 'horror', 'abominable', 'deplorable'
]

# Intensificadores (fuerzan opinión)
INTENSIFICADORES = [
    'claramente', 'obviamente', 'definitivamente', 'indudablemente', 'absolutamente', 'completamente'
]

# Palabras de duda
PALABRAS_DUDA = [
    'supuestamente', 'aparentemente', 'presuntamente', 'según', 'alega', 'asegura'
]

# ============= CONFIGURACIÓN DE GROQ/IA =============

# Temperatura para análisis (0.0-1.0)
# Más bajo = más consistente y determinista
# Más alto = más creativo y variable
IA_TEMPERATURE = 0.3

# Máximo de tokens para respuesta
IA_MAX_TOKENS = 8000

# Modelo por defecto de Groq
GROQ_MODEL_DEFAULT = "llama-3.1-8b-instant"  # Ultra rápido
GROQ_MODEL_PRO = "llama-3.3-70b-versatile"   # Más potente

# ============= CONFIGURACIÓN DE UI =============

# Número máximo de medios a mostrar en gráficos
MAX_MEDIOS_VISUALIZACION = 10

# Número máximo de divergencias a mostrar
MAX_DIVERGENCIAS_MOSTRAR = 5

# Número máximo de palabras frecuentes por tipo
MAX_PALABRAS_FRECUENTES = 5

# Mostrar resumen ejecutivo en tab1
SHOW_EXECUTIVE_SUMMARY = True

# Mostrar puntos comunes en tab1
SHOW_COMMON_POINTS = True

# ============= EXPORTACIÓN DE DATOS =============

# Guardar análisis en histórico automáticamente
AUTO_SAVE_ANALYSIS = True

# Ruta del archivo histórico
HISTORICO_FILE = 'analisis_historico.json'

# Máximo de análisis guardados
MAX_HISTORICO = 1000

# ============= LOGGING Y DEBUG =============

# Nivel de logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Mostrar tiempos de ejecución
SHOW_EXECUTION_TIMES = False

# Mostrar prompts enviados a IA (útil para debugging)
DEBUG_PROMPTS = False

# ============= FEATURES EXPERIMENTALES =============

# Análisis de imágenes (requiere librerías adicionales)
ENABLE_IMAGE_ANALYSIS = False

# Seguimiento histórico de sesgo por medio
ENABLE_HISTORICAL_TRACKING = False

# Análisis de comentarios de lectores
ENABLE_COMMENTS_ANALYSIS = False

# Detección de clickbait en títulos
ENABLE_CLICKBAIT_DETECTION = False
