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
                "temperature": 0.1,
                "max_tokens": 8000  # Groq soporta más tokens
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

def analizar_con_groq(noticias_filtradas, titulo_tema, tags_seleccionados, usar_pro=False, callback_progreso=None):
    """
    Análisis con Groq - Ultra rápido y generoso en límites gratuitos
    """
    
    if len(noticias_filtradas) > 20:
        noticias_filtradas = noticias_filtradas[:20]
    
    # Modelos disponibles en Groq (todos gratuitos)
    if usar_pro:
        model_name = "llama-3.3-70b-versatile"  # Más potente
    else:
        model_name = "llama-3.1-8b-instant"  # Más rápido
    
    if callback_progreso:
        callback_progreso("Preparando datos de noticias...")
    
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
            "contenido_preview": n.get('content', '')[:800] if n.get('content') else ""
        })
    
    # Lista de medios únicos para el prompt
    lista_medios = sorted(list(medios_unicos))
    medios_str = ", ".join([f'"{m}"' for m in lista_medios])
    
    # Preparar texto con noticias
    noticias_texto = ""
    for n in noticias_info:
        noticias_texto += f"NOTICIA {n['indice']}:\n"
        noticias_texto += f"Medio: {n['medio']}\n"
        noticias_texto += f"Título: {n['titulo']}\n"
        noticias_texto += f"Fecha: {n['fecha']}\n"
        noticias_texto += f"URL: {n['url']}\n"
        noticias_texto += f"Preview: {n['contenido_preview']}\n\n"
    
    # Plantilla de sesgo para cada medio
    plantilla_sesgos_lista = []
    for medio in lista_medios:
        plantilla_sesgos_lista.append(f'"{medio}": {{"orientacion_detectada": "...", "nivel_bias": 0.0, "indicadores": ["..."]}}')
    plantilla_sesgos = ",\n    ".join(plantilla_sesgos_lista)
    
    # Plantilla de cobertura por medio
    cobertura_lista = []
    for m in lista_medios:
        cobertura_lista.append(f'"{m}": {{"enfoque_principal": "...", "tono": "...", "elementos_destacados": ["..."]}}')
    cobertura_template = ",\n    ".join(cobertura_lista)
    
    # Construir lista de medios con saltos de línea
    medios_checklist = ""
    for m in lista_medios:
        medios_checklist += f"- {m}\n"
    
    # Construir el prompt completo SIN f-strings anidados
    prompt = "Analiza estas " + str(len(noticias_filtradas)) + " noticias españolas sobre \"" + titulo_tema + "\".\n\n"
    prompt += "MEDIOS PRESENTES EN EL ANÁLISIS (TODOS DEBEN SER INCLUIDOS): " + medios_str + "\n"
    prompt += "Total de medios diferentes: " + str(len(lista_medios)) + "\n\n"
    prompt += "NOTICIAS:\n" + noticias_texto + "\n"
    prompt += "Genera un JSON válido (sin markdown, sin bloques de código) con esta estructura exacta:\n\n"
    prompt += "{\n"
    prompt += '  "tema": "' + titulo_tema + '",\n'
    prompt += '  "tags_analizados": ' + json.dumps(tags_seleccionados, ensure_ascii=False) + ',\n'
    prompt += '  "fecha_analisis": "' + datetime.now().isoformat() + '",\n'
    prompt += '  "resumen_objetivo": "Resumen objetivo de 2-3 oraciones con hechos verificables",\n'
    prompt += '  "analisis_5w1h": {\n'
    prompt += '    "que": "¿Qué ha ocurrido? Describe el evento o situación principal",\n'
    prompt += '    "quien": "¿Quién está involucrado? Personas, organizaciones, instituciones",\n'
    prompt += '    "cuando": "¿Cuándo ocurrió? Fechas y cronología de eventos",\n'
    prompt += '    "donde": "¿Dónde sucedió? Lugares y contexto geográfico",\n'
    prompt += '    "por_que": "¿Por qué ocurrió? Causas, motivos y contexto",\n'
    prompt += '    "como": "¿Cómo se desarrolló? Proceso, método y consecuencias"\n'
    prompt += '  },\n'
    prompt += '  "puntos_comunes": [\n'
    prompt += '    "Hecho común 1 entre todos los medios",\n'
    prompt += '    "Hecho común 2 entre todos los medios",\n'
    prompt += '    "Hecho común 3 entre todos los medios"\n'
    prompt += '  ],\n'
    prompt += '  "divergencias": [\n'
    prompt += '    {\n'
    prompt += '      "aspecto": "Aspecto específico donde divergen los medios",\n'
    prompt += '      "perspectivas": [\n'
    prompt += '        {"medio": "Medio 1", "enfoque": "Enfoque específico"},\n'
    prompt += '        {"medio": "Medio 2", "enfoque": "Enfoque específico"},\n'
    prompt += '        (INCLUIR TODOS LOS MEDIOS: ' + medios_str + ')\n'
    prompt += '      ]\n'
    prompt += '    }\n'
    prompt += '  ],\n'
    prompt += '  "cobertura_por_medio": {\n'
    prompt += '    ' + cobertura_template + '\n'
    prompt += '  },\n'
    prompt += '  "analisis_sentimiento": {\n'
    prompt += '    "tono_general": "neutral",\n'
    prompt += '    "nivel_sensacionalismo_promedio": 0.5,\n'
    prompt += '    "descripcion": "Breve descripción del tono detectado"\n'
    prompt += '  },\n'
    prompt += '  "sesgo_detectado": {\n'
    prompt += '    ' + plantilla_sesgos + '\n'
    prompt += '  },\n'
    prompt += '  "omisiones_relevantes": [\n'
    prompt += '    {"medio": "Nombre exacto del medio", "informacion_omitida": "Qué información relevante omite comparado con otros medios"}\n'
    prompt += '  ]\n'
    prompt += '}\n\n'
    prompt += 'INSTRUCCIONES CRÍTICAS:\n'
    prompt += '1. OBLIGATORIO: En "sesgo_detectado" DEBES incluir TODOS Y CADA UNO de estos medios: ' + medios_str + '\n'
    prompt += '2. OBLIGATORIO: En "divergencias", dentro de cada "aspecto", la lista "perspectivas" DEBE contener TODOS los medios: ' + medios_str + '\n'
    prompt += '   - Si un medio tiene un enfoque similar a otro, especifícalo pero inclúyelo\n'
    prompt += '   - Si un medio no cubre un aspecto, indica "No cubre este aspecto específicamente"\n'
    prompt += '3. NUEVO: Añade "cobertura_por_medio" con análisis individual de CADA medio presente\n'
    prompt += '4. Cada medio en "sesgo_detectado" debe tener:\n'
    prompt += '   - "orientacion_detectada": Describe la orientación política/editorial detectada\n'
    prompt += '   - "nivel_bias": número entre 0.0 (neutral) y 1.0 (muy sesgado)\n'
    prompt += '   - "indicadores": lista de 2-3 indicadores concretos del sesgo\n'
    prompt += '5. Identifica al menos 2-3 aspectos diferentes donde los medios tengan divergencias\n'
    prompt += '6. En cada aspecto de divergencias, TODOS los medios (' + str(len(lista_medios)) + ') deben aparecer\n'
    prompt += '7. Responde SOLO el JSON válido, sin texto adicional, sin ```json ni ```\n'
    prompt += '8. Sé objetivo y basa tu análisis en hechos verificables de las noticias proporcionadas\n\n'
    prompt += 'MEDIOS QUE DEBEN APARECER EN CADA SECCIÓN (VERIFICAR):\n'
    prompt += medios_checklist

    if callback_progreso:
        callback_progreso(f"Enviando a Groq ({model_name}) - Analizando {len(lista_medios)} medios...")
    
    try:
        messages = [
            {
                "role": "system",
                "content": "Eres un analista objetivo de noticias especializado en análisis comparativo multi-medio. DEBES analizar TODOS Y CADA UNO de estos " + str(len(lista_medios)) + " medios: " + medios_str + ". En la sección 'divergencias', CADA aspecto debe incluir la perspectiva de TODOS los medios listados. Respondes SOLO con JSON válido, sin markdown."
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
        
        # Verificar completitud del análisis
        sesgos = analisis.get('sesgo_detectado', {})
        medios_faltantes_sesgo = [m for m in lista_medios if m not in sesgos]
        
        # Verificar divergencias
        divergencias = analisis.get('divergencias', [])
        medios_en_divergencias = set()
        for div in divergencias:
            for persp in div.get('perspectivas', []):
                medios_en_divergencias.add(persp.get('medio', ''))
        medios_faltantes_div = [m for m in lista_medios if m not in medios_en_divergencias]
        
        if callback_progreso:
            if medios_faltantes_sesgo:
                callback_progreso(f"⚠️ {len(medios_faltantes_sesgo)} medios sin análisis de sesgo")
            if medios_faltantes_div:
                callback_progreso(f"⚠️ {len(medios_faltantes_div)} medios sin análisis de divergencias")
        
        # Añadir metadata
        analisis['modelo_usado'] = model_name
        analisis['noticias_analizadas'] = len(noticias_filtradas)
        analisis['medios_unicos'] = len(lista_medios)
        analisis['lista_medios'] = lista_medios
        analisis['medios_faltantes_sesgo'] = medios_faltantes_sesgo
        analisis['medios_faltantes_divergencias'] = medios_faltantes_div
        analisis['metodo'] = 'groq_api'
        
        if callback_progreso:
            callback_progreso("¡Análisis completado!")
        
        return analisis
        
    except Exception as e:
        error_msg = str(e)
        if '429' in error_msg or 'quota' in error_msg.lower():
            raise Exception(
                "⚠️ Límite de API alcanzado. Espera 1 minuto e intenta de nuevo.\n"
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
