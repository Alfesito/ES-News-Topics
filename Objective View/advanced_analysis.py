"""
Advanced News Analysis Module
Análisis sofisticado de lenguaje, sesgos, fuentes y énfasis
"""

import re
from collections import Counter
from typing import Dict, List, Tuple

# Palabras emotivas/cargadas por categoría
PALABRAS_EMOTIVAS = {
    'positivas_fuertes': ['excelente', 'triunfo', 'victoria', 'éxito', 'heroico', 'brillante', 'espectacular', 'magnífico'],
    'positivas_moderadas': ['bueno', 'favorable', 'positivo', 'logro', 'avance', 'mejora', 'progreso'],
    'negativas_fuertes': ['catastrofe', 'desastre', 'fracaso', 'derrota', 'tragedia', 'horror', 'abominable', 'deplorable'],
    'negativas_moderadas': ['malo', 'negativo', 'problema', 'crisis', 'controversia', 'preocupación', 'riesgo'],
    'intensificadores': ['claramente', 'obviamente', 'definitivamente', 'indudablemente', 'absolutamente', 'completamente'],
    'dudas': ['supuestamente', 'aparentemente', 'presuntamente', 'según', 'alega', 'asegura']
}

# Patrones de lenguaje tendencioso
PATRONES_SESGO = {
    'personalizacion_negativa': r'\b(X|fulano|el acusado|el culpable)\s+(es|fue)\s+(corrupto|delincuente|criminal)',
    'generalizacion_grupo': r'\b(los \w+|todos los \w+)\s+(son|siempre son)',
    'victimizacion': r'\b(victima|sufridor|desgraciado)\b',
    'dehumanizacion': r'\b(horda|masa|muchedumbre)\b',
    'comparaciones_inflamatorias': r'\b(como un\s+\w+|semejante a\s+\w+)\b',
}

# Palabras neutras alternativas
PALABRAS_NEUTRAS = {
    'murió': ['falleció', 'perdió la vida'],
    'masacre': ['acción violenta', 'incidente'],
    'invasión': ['ocupación', 'intervención'],
    'ataque terrorista': ['incidente violento', 'ataque'],
}

def analizar_lenguaje_sesgado(texto: str) -> Dict:
    """
    Analiza el lenguaje sesgado en un texto.
    
    Retorna:
    - emotividad: 0-100 (0=neutral, 100=muy emotivo)
    - palabras_emotivas: lista de palabras encontradas
    - intensificadores: número de intensificadores
    - dudas: número de palabras que expresan duda
    - patrones_sesgo: sesgos detectados
    """
    texto_lower = texto.lower()
    resultado = {
        'emotividad': 0,
        'palabras_emotivas_positivas': [],
        'palabras_emotivas_negativas': [],
        'intensificadores': [],
        'dudas': [],
        'patrones_sesgo_detectados': [],
        'score_neutralidad': 100
    }
    
    # Contar palabras emotivas
    puntuacion_emocional = 0
    
    for palabra_positiva in PALABRAS_EMOTIVAS['positivas_fuertes']:
        matches = re.findall(rf'\b{palabra_positiva}\b', texto_lower)
        resultado['palabras_emotivas_positivas'].extend(matches)
        puntuacion_emocional += len(matches) * 3
    
    for palabra_positiva in PALABRAS_EMOTIVAS['positivas_moderadas']:
        matches = re.findall(rf'\b{palabra_positiva}\b', texto_lower)
        resultado['palabras_emotivas_positivas'].extend(matches)
        puntuacion_emocional += len(matches) * 1
    
    for palabra_negativa in PALABRAS_EMOTIVAS['negativas_fuertes']:
        matches = re.findall(rf'\b{palabra_negativa}\b', texto_lower)
        resultado['palabras_emotivas_negativas'].extend(matches)
        puntuacion_emocional += len(matches) * 3
    
    for palabra_negativa in PALABRAS_EMOTIVAS['negativas_moderadas']:
        matches = re.findall(rf'\b{palabra_negativa}\b', texto_lower)
        resultado['palabras_emotivas_negativas'].extend(matches)
        puntuacion_emocional += len(matches) * 1
    
    # Intensificadores
    for intensificador in PALABRAS_EMOTIVAS['intensificadores']:
        matches = re.findall(rf'\b{intensificador}\b', texto_lower)
        resultado['intensificadores'].extend(matches)
        puntuacion_emocional += len(matches) * 2
    
    # Palabras de duda
    for duda in PALABRAS_EMOTIVAS['dudas']:
        matches = re.findall(rf'\b{duda}\b', texto_lower)
        resultado['dudas'].extend(matches)
    
    # Detectar patrones de sesgo
    for tipo_sesgo, patron in PATRONES_SESGO.items():
        matches = re.findall(patron, texto_lower)
        if matches:
            resultado['patrones_sesgo_detectados'].append({
                'tipo': tipo_sesgo,
                'ocurrencias': len(matches)
            })
    
    # Calcular scores
    palabras_totales = len(texto_lower.split())
    resultado['emotividad'] = min(100, (puntuacion_emocional / max(palabras_totales, 1)) * 100)
    resultado['score_neutralidad'] = max(0, 100 - resultado['emotividad'])
    
    return resultado


def analizar_atribucion_fuentes(texto: str) -> Dict:
    """
    Analiza la atribución de fuentes y citas en el texto.
    
    Retorna:
    - numero_citas: cantidad de citas encontradas
    - citas_directas: número de citas directas (entrecomilladas)
    - citas_indirectas: número de citas indirectas
    - citas_sin_fuente: afirmaciones sin fuente
    - tipos_fuentes: tipos de fuentes mencionadas
    """
    resultado = {
        'numero_citas_directas': len(re.findall(r'"[^"]*"', texto)),
        'numero_citas_indirectas': len(re.findall(r'según|afirma|declara|comenta|menciona|señala', texto, re.IGNORECASE)),
        'afirmaciones_sin_fuente': 0,
        'calidad_fuentes': 'media',
        'tipos_fuentes': [],
        'score_atribucion': 50
    }
    
    # Detectar tipos de fuentes
    fuentes_patrones = {
        'oficial': r'(gobierno|ministerio|autoridad|funcionario oficial)',
        'experto': r'(experto|investigador|académico|profesor|especialista)',
        'testigo': r'(testigo|víctima|presente)',
        'médios': r'(medio de comunicación|reportero|corresponsal)',
        'anónima': r'(fuente anónima|sin revelar identidad)'
    }
    
    for tipo_fuente, patron in fuentes_patrones.items():
        if re.search(patron, texto, re.IGNORECASE):
            resultado['tipos_fuentes'].append(tipo_fuente)
    
    # Calcular score de atribución (0-100)
    citas_totales = resultado['numero_citas_directas'] + resultado['numero_citas_indirectas']
    palabras_totales = len(texto.split())
    
    if palabras_totales > 0:
        resultado['score_atribucion'] = min(100, (citas_totales / max(palabras_totales / 50, 1)) * 100)
    
    if citas_totales > 0 and resultado['numero_citas_directas'] > resultado['numero_citas_indirectas']:
        resultado['calidad_fuentes'] = 'alta'
    elif citas_totales == 0:
        resultado['calidad_fuentes'] = 'baja'
    
    return resultado


def analizar_enfasis_colocacion(titulo: str, subtitulo: str, primeros_parrafos: str) -> Dict:
    """
    Analiza qué información se enfatiza por colocación.
    
    Retorna:
    - temas_titulo: temas principales en el título
    - temas_inicio: temas en primeros párrafos
    - score_relevancia_percibida: 0-100
    """
    resultado = {
        'temas_titulo': titulo,
        'temas_inicio': subtitulo,
        'longitud_titulo': len(titulo.split()),
        'longitud_intro': len(primeros_parrafos.split()),
        'score_enfasis': 50,
        'enfoque_principal': '',
        'info_retrasada': ''
    }
    
    # Análisis simple de énfasis
    palabras_clave_titulo = set(titulo.lower().split())
    palabras_clave_intro = set(primeros_parrafos.lower().split())
    
    # Calcular superposición
    superposicion = len(palabras_clave_titulo & palabras_clave_intro)
    total_palabras = len(palabras_clave_titulo | palabras_clave_intro)
    
    if total_palabras > 0:
        resultado['score_enfasis'] = (superposicion / total_palabras) * 100
    
    # Detectar si hay contexto en los primeros párrafos
    palabras_contexto = ['antecedente', 'previamente', 'anteriormente', 'contexto', 'situación']
    tiene_contexto = any(palabra in primeros_parrafos.lower() for palabra in palabras_contexto)
    
    resultado['tiene_contexto'] = tiene_contexto
    
    return resultado


def analizar_equilibrio_perspectivas(texto: str) -> Dict:
    """
    Analiza si se presentan múltiples perspectivas.
    
    Retorna:
    - numero_perspectivas: número de perspectivas encontradas
    - perspectivas_mencionadas: tipos de perspectivas
    - balance: 'unilateral', 'parcial', 'equilibrado'
    - score_balance: 0-100
    """
    resultado = {
        'perspectivas_encontradas': [],
        'balance': 'desconocido',
        'score_balance': 50,
        'menciona_criticas': False,
        'menciona_contrapuntos': False,
        'menciona_posiciones_opuestas': False
    }
    
    texto_lower = texto.lower()
    
    # Palabras indicadoras de múltiples perspectivas
    if 'sin embargo' in texto_lower or 'por otra parte' in texto_lower or 'de otro lado' in texto_lower:
        resultado['menciona_contrapuntos'] = True
    
    if 'crítica' in texto_lower or 'crítico' in texto_lower or 'cuestiona' in texto_lower:
        resultado['menciona_criticas'] = True
    
    if 'opuesto' in texto_lower or 'en desacuerdo' in texto_lower or 'diferente opinión' in texto_lower:
        resultado['menciona_posiciones_opuestas'] = True
    
    # Calcular score de balance
    score = 0
    if resultado['menciona_contrapuntos']:
        score += 30
    if resultado['menciona_criticas']:
        score += 30
    if resultado['menciona_posiciones_opuestas']:
        score += 40
    
    resultado['score_balance'] = min(100, score)
    
    # Determinar tipo de balance
    if score >= 70:
        resultado['balance'] = 'equilibrado'
    elif score >= 40:
        resultado['balance'] = 'parcial'
    else:
        resultado['balance'] = 'unilateral'
    
    return resultado


def calcular_score_sesgo_total(
    texto: str,
    titulo: str,
    subtitulo: str,
    primeros_parrafos: str
) -> Dict:
    """
    Calcula un score total de sesgo combinando múltiples análisis.
    
    Retorna un score de 0-100 donde:
    - 0-30: Muy objetivo
    - 30-50: Mayormente objetivo
    - 50-70: Parcialmente sesgado
    - 70-100: Muy sesgado
    """
    
    analisis_lenguaje = analizar_lenguaje_sesgado(texto)
    analisis_fuentes = analizar_atribucion_fuentes(texto)
    analisis_colocacion = analizar_enfasis_colocacion(titulo, subtitulo, primeros_parrafos)
    analisis_perspectivas = analizar_equilibrio_perspectivas(texto)
    
    # Ponderación de factores
    score_final = (
        (100 - analisis_lenguaje['score_neutralidad']) * 0.3 +  # Neutralidad del lenguaje
        (100 - analisis_fuentes['score_atribucion']) * 0.2 +     # Atribución de fuentes
        (100 - analisis_perspectivas['score_balance']) * 0.3 +   # Balance de perspectivas
        (100 - analisis_colocacion['score_enfasis']) * 0.2       # Énfasis adecuado
    )
    
    return {
        'score_sesgo_total': min(100, max(0, score_final)),
        'score_neutralidad': analisis_lenguaje['score_neutralidad'],
        'score_atribucion': analisis_fuentes['score_atribucion'],
        'score_balance': analisis_perspectivas['score_balance'],
        'score_enfasis': analisis_colocacion['score_enfasis'],
        'detalles': {
            'lenguaje': analisis_lenguaje,
            'fuentes': analisis_fuentes,
            'colocacion': analisis_colocacion,
            'perspectivas': analisis_perspectivas
        }
    }


def generar_reporte_sesgo_detallado(articulo: Dict) -> Dict:
    """
    Genera un reporte detallado de sesgo para un artículo.
    """
    titulo = articulo.get('title', '')
    subtitulo = articulo.get('subtitle', '')
    cuerpo = articulo.get('body', '')
    
    # Tomar primeros 3 párrafos como "introducción"
    parrafos = cuerpo.split('\n')[:3]
    primeros_parrafos = ' '.join(parrafos)
    
    # Texto completo para análisis
    texto_completo = f"{titulo} {subtitulo} {cuerpo}"
    
    score_total = calcular_score_sesgo_total(
        texto_completo,
        titulo,
        subtitulo,
        primeros_parrafos
    )
    
    # Generar indicadores clave
    indicadores = []
    
    if score_total['detalles']['lenguaje']['emotividad'] > 70:
        indicadores.append("Lenguaje altamente emotivo")
    
    if score_total['detalles']['fuentes']['score_atribucion'] < 40:
        indicadores.append("Escasa atribución de fuentes")
    
    if score_total['detalles']['perspectivas']['balance'] == 'unilateral':
        indicadores.append("Presenta solo una perspectiva")
    
    if score_total['detalles']['lenguaje']['patrones_sesgo_detectados']:
        indicadores.append("Patrones de lenguaje sesgado detectados")
    
    return {
        'articulo_id': articulo.get('id'),
        'medio': articulo.get('source'),
        'score_sesgo': score_total['score_sesgo_total'],
        'indicadores_clave': indicadores,
        'analisis_detallado': score_total
    }
