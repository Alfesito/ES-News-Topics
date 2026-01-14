# utils_groq.py
import json
import requests
from collections import Counter
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
import re
import time

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_JSON_URL = os.getenv("NEWS_JSON_URL")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY no encontrada en .env")

ANALISIS_FILE = Path("analisis_historico.json")

ultimo_request_time = 0
MIN_DELAY_BETWEEN_REQUESTS = 2  # 30 RPM = cada 2 segundos

def esperar_rate_limit():
    """Espera el tiempo necesario para respetar rate limits"""
    global ultimo_request_time
    tiempo_transcurrido = time.time() - ultimo_request_time

    if tiempo_transcurrido < MIN_DELAY_BETWEEN_REQUESTS:
        tiempo_espera = MIN_DELAY_BETWEEN_REQUESTS - tiempo_transcurrido
        print(f"⏳ Esperando {tiempo_espera:.1f}s para respetar rate limit...")
        time.sleep(tiempo_espera)

    ultimo_request_time = time.time()

def llamar_groq_con_retry(model_name, messages, max_retries=3):
    """Llama a Groq con retry automático usando requests"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    for intento in range(max_retries):
        try:
            esperar_rate_limit()

            print(f"🤖 Llamando a Groq ({model_name}) - intento {intento + 1}/{max_retries}...")

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 8000
            }

            response = requests.post(
                url, 
                headers=headers, 
                json=payload,
                timeout=120
            )

            response.raise_for_status()
            result = response.json()

            return result['choices'][0]['message']['content'].strip()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                tiempo_espera = 30 * (intento + 1)
                print(f"⚠️ Rate limit alcanzado. Esperando {tiempo_espera}s...")
                time.sleep(tiempo_espera)
                continue

            if intento == max_retries - 1:
                try:
                    error_detail = e.response.json()
                    raise Exception(f"Error HTTP: {error_detail}")
                except:
                    raise Exception(f"Error HTTP: {str(e)[:300]}")

            print(f"⚠️ Error HTTP. Reintentando en 10s...")
            time.sleep(10)

        except Exception as e:
            if intento == max_retries - 1:
                raise Exception(f"Error después de {max_retries} intentos: {str(e)[:300]}")

            print(f"⚠️ Error: {str(e)[:200]}. Reintentando en 10s...")
            time.sleep(10)

    raise Exception("No se pudo completar la llamada")

def completar_analisis_faltante(analisis, lista_medios, noticias_filtradas):
    """Completa medios faltantes en el análisis para garantizar cobertura completa"""

    # Completar sesgos detectados
    sesgos = analisis.get('sesgo_detectado', {})
    for medio in lista_medios:
        if medio not in sesgos:
            noticias_medio = [n for n in noticias_filtradas if n['newspaper'] == medio]
            sesgos[medio] = {
                "orientacion_detectada": "Cobertura estándar - análisis pendiente",
                "nivel_bias": 0.5,
                "indicadores": [
                    f"Medio con {len(noticias_medio)} artículos en la muestra",
                    "Requiere análisis manual complementario"
                ]
            }
    analisis['sesgo_detectado'] = sesgos

    # Completar divergencias
    divergencias = analisis.get('divergencias', [])
    for div in divergencias:
        perspectivas = div.get('perspectivas', [])
        medios_en_perspectiva = {p.get('medio', '') for p in perspectivas}

        for medio in lista_medios:
            if medio not in medios_en_perspectiva:
                noticias_medio = [n for n in noticias_filtradas if n['newspaper'] == medio]
                if noticias_medio:
                    perspectivas.append({
                        "medio": medio,
                        "enfoque": "Cobertura general sin énfasis específico en este aspecto"
                    })
                else:
                    perspectivas.append({
                        "medio": medio,
                        "enfoque": "Sin cobertura detectada de este aspecto"
                    })

        div['perspectivas'] = perspectivas

    analisis['divergencias'] = divergencias

    # Completar cobertura por medio
    cobertura = analisis.get('cobertura_por_medio', {})
    for medio in lista_medios:
        if medio not in cobertura:
            noticias_medio = [n for n in noticias_filtradas if n['newspaper'] == medio]
            cobertura[medio] = {
                "enfoque_principal": "Cobertura estándar del evento",
                "tono": "neutral",
                "elementos_destacados": [f"{len(noticias_medio)} artículos publicados sobre el tema"]
            }
    analisis['cobertura_por_medio'] = cobertura

    return analisis

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
        response = requests.get(NEWS_JSON_URL, timeout=26)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.RequestException as e:
        raise Exception(f"Error al cargar noticias: {str(e)}")

def extraer_tags_unicos(noticias):
    todos_tags = set()
    for noticia in noticias:
        todos_tags.update(noticia.get('tags', []))
    return sorted(list(todos_tags))

def filtrar_noticias(noticias, tags_seleccionados, limite=30):
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

def analizar_con_groq(noticias_filtradas, titulo_tema, tags_seleccionados, usar_pro=True, callback_progreso=None):
    """
    Análisis con Groq - Analiza TODAS las noticias proporcionadas
    """
    
    # Siempre usar el modelo más potente (es gratuito)
    model_name = "llama-3.3-70b-versatile"
    
    # O si quieres mantener la flexibilidad:
    if usar_pro:
        model_name = "llama-3.3-70b-versatile"  # Mejor para análisis profundo
    else:
        model_name = "llama-3.1-8b-instant"     # Más rápido pero menos preciso

    if callback_progreso:
        callback_progreso(f"Preparando {len(noticias_filtradas)} noticias para análisis...")

    # Preparar información de noticias
    noticias_info = []
    medios_unicos = set()
    for i, n in enumerate(noticias_filtradas):
        medios_unicos.add(n['newspaper'])
        noticias_info.append({
            "indice": i + 1,
            "medio": n['newspaper'],
            "titulo": n['title'],
            "fecha": n['date'][:10],
            "url": n['url'],
            "contenido_preview": n.get('content', '')[:800] if n.get('content') else ""  # Aumentado de 600 a 800
        })

    lista_medios = sorted(list(medios_unicos))

    if callback_progreso:
        callback_progreso(f"Analizando {len(lista_medios)} medios distintos...")

    # Preparar texto con noticias agrupadas por medio
    noticias_por_medio = {}
    for medio in lista_medios:
        noticias_por_medio[medio] = [n for n in noticias_info if n['medio'] == medio]

    noticias_texto = ""
    for medio in lista_medios:
        noticias_texto += f"\n=== MEDIO: {medio} ({len(noticias_por_medio[medio])} artículos) ===\n"
        for n in noticias_por_medio[medio]:
            noticias_texto += f"[{n['indice']}] {n['titulo']} ({n['fecha']})\n"
            noticias_texto += f"Preview: {n['contenido_preview']}\n"
            noticias_texto += f"URL: {n['url']}\n\n"

    # Construir ejemplos para divergencias
    ejemplo_divergencias = []
    ejemplo_divergencias.append("    {")
    ejemplo_divergencias.append('      "perspectivas": [')
    for idx, medio in enumerate(lista_medios):
        coma = "," if idx < len(lista_medios) - 1 else ""
        ejemplo_divergencias.append(f'        {{"medio": "{medio}", "enfoque": "Analizar enfoque de {medio} sobre este aspecto"}}{coma}')
    ejemplo_divergencias.append('      ]')
    ejemplo_divergencias.append('    }')

    divergencias_template = "\n".join(ejemplo_divergencias)

    # Construir ejemplos para sesgo_detectado
    sesgo_items = []
    for idx, medio in enumerate(lista_medios):
        coma = "," if idx < len(lista_medios) - 1 else ""
        sesgo_items.append(f'    "{medio}": {{"orientacion_detectada": "Analizar orientación", "nivel_bias": 0.5, "indicadores": ["Indicador 1", "Indicador 2"]}}{coma}')
    sesgo_template = "\n".join(sesgo_items)

    # Construir ejemplos para cobertura_por_medio
    cobertura_items = []
    for idx, medio in enumerate(lista_medios):
        coma = "," if idx < len(lista_medios) - 1 else ""
        cobertura_items.append(f'    "{medio}": {{"enfoque_principal": "Enfoque de {medio}", "tono": "neutral", "elementos_destacados": ["Elemento 1"]}}{coma}')
    cobertura_template = "\n".join(cobertura_items)

    prompt = f"""Analiza estas {len(noticias_filtradas)} noticias españolas sobre "{titulo_tema}".

MEDIOS PRESENTES (TODOS deben ser analizados): {', '.join(lista_medios)}
Total de medios: {len(lista_medios)}
Total de artículos: {len(noticias_filtradas)}

DISTRIBUCIÓN POR MEDIO:
{chr(10).join([f"- {medio}: {len(noticias_por_medio[medio])} artículos" for medio in lista_medios])}

{noticias_texto}

Genera un análisis en formato JSON válido (sin markdown, sin bloques de código):

{{
  "tema": "{titulo_tema}",
  "tags_analizados": {json.dumps(tags_seleccionados, ensure_ascii=False)},
  "fecha_analisis": "{datetime.now().isoformat()}",
  "resumen_objetivo": "Resumen objetivo de 3 párrafos con hechos verificables en TODAS las noticias analizadas. Menciona cifras concretas, fechas y actores principales.",

  "analisis_5w1h": {{
    "que": "¿Qué ha ocurrido? (Basado en TODAS las noticias)",
    "quien": "¿Quién está involucrado? (Todos los actores mencionados)",
    "cuando": "¿Cuándo ocurrió? (Línea temporal completa)",
    "donde": "¿Dónde sucedió? (Todos los lugares mencionados)",
    "por_que": "¿Por qué ocurrió? (Causas identificadas en los artículos)",
    "como": "¿Cómo se desarrolló? (Secuencia de eventos completa)"
  }},

  "puntos_comunes": [
    "Hecho común 1 verificado en múltiples medios",
    "Hecho común 2 verificado en múltiples medios",
    "Hecho común 3 verificado en múltiples medios",
    "Hecho común 4 verificado en múltiples medios"
  ],

  "divergencias": [
{divergencias_template},
    {{
      "aspecto": "Otro aspecto de divergencia importante",
      "perspectivas": [
        (INCLUIR PERSPECTIVA DE TODOS LOS {len(lista_medios)} MEDIOS)
      ]
    }}
  ],

  "cobertura_por_medio": {{
{cobertura_template}
  }},

  "analisis_sentimiento": {{
    "tono_general": "neutral/positivo/negativo/mixto",
    "nivel_sensacionalismo_promedio": 0.5,
    "descripcion": "Descripción del tono general observado en TODOS los artículos"
  }},

  "sesgo_detectado": {{
{sesgo_template}
  }},

  "omisiones_relevantes": [
    {{"medio": "Medio1", "informacion_omitida": "Información importante omitida en comparación con otros medios"}}
    {{"medio": "Medio2", "informacion_omitida": "Información importante omitida en comparación con otros medios"}}
    {{"medio": "Medio3", "informacion_omitida": "Información importante omitida en comparación con otros medios"}}
  ]
}}

INSTRUCCIONES CRÍTICAS:
1. OBLIGATORIO: Analiza TODAS las {len(noticias_filtradas)} noticias proporcionadas
2. OBLIGATORIO: Incluye TODOS estos {len(lista_medios)} medios: {', '.join(lista_medios)}
3. OBLIGATORIO: En "sesgo_detectado" → TODOS los medios con análisis real
4. OBLIGATORIO: En "cobertura_por_medio" → TODOS los medios con análisis real
5. OBLIGATORIO: En cada aspecto de "divergencias" → TODOS los medios con su perspectiva
6. Si un medio no enfatiza un aspecto, indica específicamente qué enfoca en su lugar
7. Identifica al menos 3 aspectos de divergencia significativos
8. El resumen debe reflejar TODA la información de las {len(noticias_filtradas)} noticias
9. Responde SOLO JSON válido, sin ```json ni ```
10. Basa el análisis en hechos verificables de TODAS las noticias proporcionadas
"""

    if callback_progreso:
        callback_progreso(f"Enviando a Groq ({model_name})...")

    try:
        messages = [
            {
                "role": "system",
                "content": f"Eres un analista objetivo de noticias. Debes analizar TODAS las {len(noticias_filtradas)} noticias proporcionadas. DEBES analizar TODOS estos {len(lista_medios)} medios: {', '.join(lista_medios)}. En CADA sección (sesgo_detectado, cobertura_por_medio, divergencias), TODOS los medios deben aparecer con análisis real basado en sus artículos. Respondes SOLO con JSON válido."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        texto = llamar_groq_con_retry(
            model_name=model_name,
            messages=messages,
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

        # COMPLETAR AUTOMÁTICAMENTE MEDIOS FALTANTES
        if callback_progreso:
            callback_progreso("Completando análisis...")

        analisis = completar_analisis_faltante(analisis, lista_medios, noticias_filtradas)

        # Añadir metadata completa
        analisis['modelo_usado'] = model_name
        analisis['noticias_analizadas'] = len(noticias_filtradas)
        analisis['medios_unicos'] = len(lista_medios)
        analisis['lista_medios'] = lista_medios
        analisis['metodo'] = 'groq_api'
        analisis['distribucion_articulos_por_medio'] = {
            medio: len(noticias_por_medio[medio]) 
            for medio in lista_medios
        }

        if callback_progreso:
            callback_progreso(f"✓ Análisis completado ({len(noticias_filtradas)} noticias, {len(lista_medios)} medios)")

        return analisis

    except Exception as e:
        error_msg = str(e)
        if '429' in error_msg or 'quota' in error_msg.lower():
            raise Exception(
                "⚠️ Límite de API alcanzado. Espera 1 minuto.\n"
                "Registra tu cuenta en: https://console.groq.com"
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
