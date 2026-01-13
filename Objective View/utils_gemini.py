# utils.py
import json
import requests
from collections import Counter
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
import re
import time

from google import genai
from google.genai import types

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEWS_JSON_URL = os.getenv("NEWS_JSON_URL")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY no encontrada en .env")

client = genai.Client(api_key=GOOGLE_API_KEY)
ANALISIS_FILE = Path("analisis_historico.json")

ultimo_request_time = 0
MIN_DELAY_BETWEEN_REQUESTS = 5


def esperar_rate_limit():
    """Espera el tiempo necesario para respetar rate limits"""
    global ultimo_request_time
    tiempo_transcurrido = time.time() - ultimo_request_time
    
    if tiempo_transcurrido < MIN_DELAY_BETWEEN_REQUESTS:
        tiempo_espera = MIN_DELAY_BETWEEN_REQUESTS - tiempo_transcurrido
        print(f"⏳ Esperando {tiempo_espera:.1f}s para respetar rate limit...")
        time.sleep(tiempo_espera)
    
    ultimo_request_time = time.time()


def llamar_gemini_con_retry(model_name, prompt, urls=None, max_output_tokens=3000, max_retries=3):
    """Llama a Gemini con retry automático y soporte para URLs"""
    
    for intento in range(max_retries):
        try:
            esperar_rate_limit()
            
            print(f"🤖 Llamando a Gemini (intento {intento + 1}/{max_retries})...")
            
            # Configurar herramientas si hay URLs
            tools = None
            if urls and len(urls) > 0:
                tools = [types.Tool(url_context={})]
                print(f"📎 Usando URL Context para {len(urls)} URLs")
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json",
                    tools=tools
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            error_str = str(e)
            
            if '429' in error_str or 'quota' in error_str.lower() or 'rate' in error_str.lower():
                tiempo_espera = 60 * (intento + 1)
                print(f"⚠️ Rate limit alcanzado. Esperando {tiempo_espera}s...")
                time.sleep(tiempo_espera)
                continue
            
            if intento == max_retries - 1:
                raise Exception(f"Error después de {max_retries} intentos: {error_str[:300]}")
            
            print(f"⚠️ Error: {error_str[:200]}. Reintentando en 10s...")
            time.sleep(10)
    
    raise Exception("No se pudo completar la llamada")


# Funciones de almacenamiento (iguales que antes)
def inicializar_almacenamiento():
    if not ANALISIS_FILE.exists():
        with open(ANALISIS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def cargar_analisis_historico():
    inicializar_almacenamiento()
    try:
        with open(ANALISIS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def guardar_analisis(nuevo_analisis):
    inicializar_almacenamiento()
    analisis_existentes = cargar_analisis_historico()
    titulo_nuevo = nuevo_analisis.get('tema', '').strip().lower()
    indice_existente = None
    version_anterior = 1
    
    for i, analisis in enumerate(analisis_existentes):
        titulo_existente = analisis.get('tema', '').strip().lower()
        if titulo_existente == titulo_nuevo:
            indice_existente = i
            version_anterior = analisis.get('metadata', {}).get('version', 1)
            break
    
    nuevo_analisis['metadata'] = {
        'guardado_en': datetime.now().isoformat(),
        'version': version_anterior + 1 if indice_existente is not None else 1
    }
    
    if indice_existente is not None:
        analisis_existentes[indice_existente] = nuevo_analisis
        accion = "actualizado"
    else:
        analisis_existentes.append(nuevo_analisis)
        accion = "añadido"
    
    with open(ANALISIS_FILE, 'w', encoding='utf-8') as f:
        json.dump(analisis_existentes, f, ensure_ascii=False, indent=2)
    
    return accion, len(analisis_existentes)

def buscar_analisis_por_titulo(titulo):
    analisis_existentes = cargar_analisis_historico()
    titulo_buscar = titulo.strip().lower()
    for analisis in analisis_existentes:
        if analisis.get('tema', '').strip().lower() == titulo_buscar:
            return analisis
    return None

def eliminar_analisis(titulo):
    analisis_existentes = cargar_analisis_historico()
    titulo_eliminar = titulo.strip().lower()
    analisis_filtrados = [
        a for a in analisis_existentes 
        if a.get('tema', '').strip().lower() != titulo_eliminar
    ]
    eliminados = len(analisis_existentes) - len(analisis_filtrados)
    if eliminados > 0:
        with open(ANALISIS_FILE, 'w', encoding='utf-8') as f:
            json.dump(analisis_filtrados, f, ensure_ascii=False, indent=2)
    return eliminados

def exportar_analisis_individual(analisis, directorio="exports"):
    Path(directorio).mkdir(exist_ok=True)
    titulo_safe = "".join(
        c if c.isalnum() or c in (' ', '_', '-') else '_' 
        for c in analisis['tema']
    )
    titulo_safe = titulo_safe[:50]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{directorio}/{titulo_safe}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(analisis, f, ensure_ascii=False, indent=2)
    return filename

def cargar_noticias():
    try:
        response = requests.get(NEWS_JSON_URL, timeout=10)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.RequestException as e:
        raise Exception(f"Error al cargar noticias: {str(e)}")

def extraer_tags_unicos(noticias):
    todos_tags = set()
    for noticia in noticias:
        todos_tags.update(noticia.get('tags', []))
    return sorted(list(todos_tags))

def filtrar_noticias(noticias, tags_seleccionados, limite=7):
    noticias_filtradas = []
    for noticia in noticias:
        if any(tag in noticia.get('tags', []) for tag in tags_seleccionados):
            noticias_filtradas.append(noticia)
    
    try:
        noticias_filtradas_ordenadas = sorted(
            noticias_filtradas,
            key=lambda x: datetime.fromisoformat(x.get('date', '').replace('Z', '+00:00')),
            reverse=True
        )
    except:
        noticias_filtradas_ordenadas = noticias_filtradas
    
    if len(noticias_filtradas_ordenadas) > limite:
        return noticias_filtradas_ordenadas[:limite]
    
    return noticias_filtradas_ordenadas


def analizar_con_gemini(noticias_filtradas, titulo_tema, tags_seleccionados, usar_pro=False, callback_progreso=None):
    """
    Análisis con Gemini usando URL CONTEXT TOOL
    Gemini lee directamente las URLs sin necesidad de pasar el contenido completo
    """

    # Limitar a 7 URLs (máximo soportado por URL Context Tool)
    if len(noticias_filtradas) > 7:
        noticias_filtradas = noticias_filtradas[:7]
    
    model_name = 'gemini-2.0-flash-exp'
    
    if callback_progreso:
        callback_progreso("Preparando lista de URLs para análisis...")
    
    # Extraer URLs y metadata básica
    urls_lista = []
    metadata_noticias = []
    
    for i, n in enumerate(noticias_filtradas):
        urls_lista.append(n['url'])
        metadata_noticias.append({
            "indice": i + 1,
            "medio": n['newspaper'],
            "titulo": n['title'],
            "fecha": n['date'][:10],
            "url": n['url']
        })
    
    # Preparar prompt con referencias a URLs
    urls_referenciadas = "\n".join([
        f"{m['indice']}. [{m['medio']}] {m['titulo']}\n   URL: {m['url']}\n   Fecha: {m['fecha']}"
        for m in metadata_noticias
    ])
    
    prompt = f"""Analiza estas {len(noticias_filtradas)} noticias españolas sobre "{titulo_tema}".

Lee el contenido completo de cada URL listada abajo y genera un análisis objetivo:

NOTICIAS A ANALIZAR:
{urls_referenciadas}

Genera un JSON válido (sin markdown) con esta estructura:

{{
  "tema": "{titulo_tema}",
  "tags_analizados": {json.dumps(tags_seleccionados, ensure_ascii=False)},
  "fecha_analisis": "{datetime.now().isoformat()}",
  "resumen_objetivo": "Resumen objetivo de 2-3 oraciones con hechos verificables",
  "puntos_comunes": [
    "Hecho común 1 entre todos los medios",
    "Hecho común 2 entre todos los medios",
    "Hecho común 3 entre todos los medios"
  ],
  "divergencias": [
    {{
      "aspecto": "Aspecto donde divergen los medios",
      "perspectivas": [
        {{"medio": "Nombre del medio", "enfoque": "Cómo lo presenta este medio"}}
      ]
    }}
  ],
  "analisis_sentimiento": {{
    "tono_general": "neutral|positivo|negativo",
    "nivel_sensacionalismo_promedio": 0.5,
    "descripcion": "Breve descripción del tono detectado"
  }},
  "sesgo_detectado": {{
    "NombreMedio": {{
      "orientacion_detectada": "Descripción breve de orientación",
      "nivel_bias": 0.5,
      "indicadores": ["Indicador 1", "Indicador 2"]
    }}
  }},
  "fuentes_citadas": ["Fuente 1", "Fuente 2", "Fuente 3"],
  "omisiones_relevantes": [
    {{"medio": "Nombre", "informacion_omitida": "Qué información relevante omite"}}
  ]
}}

IMPORTANTE: 
- Lee el contenido completo de cada URL proporcionada
- Sé objetivo y basa tu análisis en hechos verificables
- Responde SOLO el JSON válido, sin texto adicional"""

    if callback_progreso:
        callback_progreso(f"Enviando {len(urls_lista)} URLs a Gemini (puede tardar 2-4 minutos)...")
    
    try:
        # Llamar con URL Context Tool
        texto = llamar_gemini_con_retry(
            model_name=model_name,
            prompt=prompt,
            urls=urls_lista,  # Las URLs se pasan aquí
            max_output_tokens=4000,
            max_retries=5
        )
        
        if callback_progreso:
            callback_progreso("Procesando respuesta...")
        
        # Limpiar y parsear
        texto = texto.replace('```json', '').replace('```', '').strip()
        
        try:
            analisis = json.loads(texto)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', texto)
            if json_match:
                analisis = json.loads(json_match.group(0))
            else:
                raise Exception(f"No se pudo parsear JSON. Respuesta: {texto[:500]}")
        
        # Añadir metadata
        analisis['modelo_usado'] = model_name
        analisis['noticias_analizadas'] = len(noticias_filtradas)
        analisis['metodo'] = 'url_context_tool'
        analisis['urls_analizadas'] = urls_lista
        
        if callback_progreso:
            callback_progreso("¡Análisis completado!")
        
        return analisis
        
    except Exception as e:
        error_msg = str(e)
        if '429' in error_msg or 'quota' in error_msg.lower():
            raise Exception(
                "⚠️ Límite de API alcanzado. Espera 5 minutos e intenta de nuevo.\n"
                "Verifica tu cuota en: https://aistudio.google.com/app/apikey"
            )
        raise Exception(f"Error en análisis: {error_msg[:400]}")


def generar_estadisticas(noticias_filtradas):
    """Genera estadísticas de cobertura"""
    if not noticias_filtradas:
        return {}
    
    total = len(noticias_filtradas)
    medios = Counter([n['newspaper'] for n in noticias_filtradas])
    
    estadisticas = {
        "total_articulos_analizados": total,
        "distribucion_por_medio": {}
    }
    
    for medio, count in medios.items():
        articulos_medio = [n for n in noticias_filtradas if n['newspaper'] == medio]
        
        fechas = []
        for n in articulos_medio:
            try:
                fecha = datetime.fromisoformat(n['date'].replace('Z', '+00:00'))
                fechas.append(fecha)
            except:
                continue
        
        estadisticas["distribucion_por_medio"][medio] = {
            "num_articulos": count,
            "porcentaje_cobertura": round((count / total) * 100, 2),
            "primera_publicacion": min(fechas).isoformat() if fechas else None,
            "ultima_publicacion": max(fechas).isoformat() if fechas else None,
            "urls": [n['url'] for n in articulos_medio]
        }
    
    estadisticas["distribucion_por_medio"] = dict(
        sorted(
            estadisticas["distribucion_por_medio"].items(),
            key=lambda x: x[1]["num_articulos"],
            reverse=True
        )
    )
    
    return estadisticas
