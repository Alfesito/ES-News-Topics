# 📰 ES-News-Topics - Documentación Completa

**Sistema integral de análisis de noticias españolas con detección de sesgos y tendencias**

---

## 📑 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Componentes Principales](#componentes-principales)
4. [Instalación y Setup](#instalación-y-setup)
5. [Cómo Funciona](#cómo-funciona)
6. [Módulos Detallados](#módulos-detallados)
7. [Uso Práctico](#uso-práctico)
8. [API y Configuración](#api-y-configuración)
9. [Troubleshooting](#troubleshooting)
10. [Roadmap](#roadmap)

---

## 🎯 Visión General

**ES-News-Topics** es un sistema completo que:

✅ **Raspa noticias** de 10+ medios españoles diarios  
✅ **Analiza tendencias** de Google Trends y X (Twitter)  
✅ **Enriquece tags** automáticamente  
✅ **Detecta sesgos** con análisis de objetividad  
✅ **Proporciona visualizaciones** interactivas  
✅ **Genera reportes** automáticos  

### Público Objetivo
- Investigadores de medios
- Periodistas
- Analistas de desinformación
- Interesados en pluralismo mediático

### Stack Tecnológico
- **Backend**: Python 3.9+
- **Web Scraping**: BeautifulSoup4, Playwright
- **IA/Análisis**: Groq API (gratis)
- **UI**: Streamlit
- **Base de datos**: JSON
- **Extras**: Flask, requests

---

## 📁 Estructura del Proyecto

```
ES-News-Topics/
│
├── 📂 Newspapers/                    ← Scrapers de medios
│   ├── api_eldiario.py              ← El Diario
│   ├── api_elpais.py                ← El País
│   ├── api_larazon.py               ← La Razón
│   ├── api_elmundo.py               ← El Mundo
│   ├── api_publico.py               ← Público
│   ├── api_elespanol.py             ← El Español
│   ├── api_lavanguardia.py          ← La Vanguardia
│   ├── api_abc.py                   ← ABC
│   ├── api_lavozdegalicia.py        ← La Voz de Galicia
│   ├── api_20minutos.py             ← 20 Minutos
│   ├── TagEnricher.py               ← Enriquecedor de tags
│   └── __pycache__/
│
├── 📂 Objective View/                ← Análisis de Objetividad
│   ├── app.py                        ← UI Principal (Streamlit)
│   ├── utils_groq.py                ← Funciones Groq
│   ├── utils_gemini.py              ← Funciones Gemini (alternativa)
│   ├── advanced_analysis.py         ← Análisis avanzado de sesgo
│   ├── visualization_utils.py       ← Visualizaciones gráficas
│   ├── config.py                    ← Configuración
│   ├── ejemplo_uso.py               ← Demostración práctica
│   ├── QUICK_REFERENCE.py           ← Referencia de funciones
│   ├── analisis_historico.json      ← BD de análisis
│   ├── requirements.txt             ← Dependencias
│   ├── MEJORAS.md                   ← Documentación de mejoras
│   ├── CHANGELOG.md                 ← Historial de cambios
│   └── RESUMEN_MEJORAS.txt          ← Resumen ejecutivo
│
├── 📂 Scraper/                       ← Base del scraper
│   ├── Base_Scraper.py              ← Clase base
│   └── __pycache__/
│
├── 📂 Utils/                         ← Utilidades generales
│   ├── Article_Utils.py
│   ├── Date_Utils.py
│   ├── Id_Utils.py
│   ├── Image_Utils.py
│   ├── Text_Utils.py
│   └── __pycache__/
│
├── 📂 Http_Client/                   ← Cliente HTTP
│   ├── http_client.py
│   ├── user_agents.py
│   └── __pycache__/
│
├── 📂 Flask_App/                     ← API REST (experimental)
│   ├── Flask_App.py
│   └── __pycache__/
│
├── 📂 news_json/                     ← Base de datos (noticias)
│   ├── noticias_24h.json            ← Últimas 24 horas
│   └── noticias_completas.json      ← Histórico 7 días
│
├── 📂 tags_json/                     ← Base de datos (tags)
│   ├── tag_relations.json           ← Relaciones entre tags
│   └── trends_google&x.json         ← Tendencias combinadas
│
├── 📂 Objective View/                (BD análisis)
│   └── analisis_historico.json
│
├── 📄 scraper_cron_lv1.py           ← Descarga noticias (nivel 1)
├── 📄 scraper_cron_lv2.py           ← Descarga noticias (nivel 2)
├── 📄 trends_scraper.py             ← Descarga tendencias
├── 📄 analyze_news_tags.py          ← Analiza relaciones entre tags
├── 📄 news_api_app.py               ← API de noticias
├── 📄 requirements.txt              ← Dependencias globales
└── README.md                        ← Este archivo

```

---

## 🧩 Componentes Principales

### 1️⃣ **Sistema de Scraping** (Newspapers/)

Raspa automáticamente noticias de 10 medios españoles.

```python
# Uso básico
from Newspapers.api_elpais import ElPaisScraper

scraper = ElPaisScraper()
articulos = scraper.scrape()  # Lista de artículos con tags
```

**Medios soportados:**
- ✅ El Diario, El País, La Razón
- ✅ Público, El Español, La Vanguardia
- ✅ ABC, El Mundo, La Voz de Galicia
- ✅ 20 Minutos

**Qué extrae:**
- Título, subtítulo, cuerpo
- Tags, autor, fecha
- Imagen (URL, créditos)
- Enlace directo

### 2️⃣ **Enriquecimiento de Tags** (TagEnricher.py)

Añade tags automáticamente basado en relaciones conocidas.

```python
# Uso básico
from Newspapers.TagEnricher import TagEnricher

enricher = TagEnricher()
tags_mejorados = enricher.enrich_tags(
    tags_existentes=["política"],
    title="Nuevo cambio en gobierno",
    subtitle="Ministro dimite",
    body="Contenido del artículo..."
)
```

**Cómo funciona:**
1. Carga relaciones entre tags desde JSON
2. Busca tags en título, subtítulo y body
3. Agrega tags relacionados si están presentes
4. Retorna lista expandida de tags

### 3️⃣ **Análisis de Tendencias** (trends_scraper.py)

Combina Google Trends y X (Twitter) Trends.

```bash
python trends_scraper.py
```

**Genera:**
- trends_google&x.json con 200+ tendencias
- IDs: 1-99 (Google), 100+ (X Trends), 200+ (Tags)
- Campos: id, title, source, volume, news_count

### 4️⃣ **Análisis de Objetividad** (Objective View/)

Sistema sofisticado de detección de sesgos.

```bash
cd "Objective View"
streamlit run app.py
```

**Características:**
- ✅ 6 dimensiones de análisis
- ✅ 20+ métricas granulares
- ✅ Scores 0-100
- ✅ Visualizaciones avanzadas
- ✅ Reportes comparativos

### 5️⃣ **Análisis de Tags** (analyze_news_tags.py)

Encuentra relaciones y clusters entre tags.

```bash
python analyze_news_tags.py
```

**Genera:**
- tag_relations.json con:
  - Frecuencia de cada tag
  - Tags relacionados
  - Clusters identificados

### 6️⃣ **API REST** (news_api_app.py)

Sirve noticias vía HTTP.

```bash
python news_api_app.py
```

**Endpoints:**
- GET /noticias - Últimas noticias
- GET /noticias/tags - Por tags
- GET /tendencias - Tendencias actuales

---

## 🚀 Instalación y Setup

### Requisitos Previos
- Python 3.9+
- pip o conda
- Git

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/Alfesito/ES-News-Topics.git
cd ES-News-Topics
```

### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
```
requests==2.32.3          # Descargas HTTP
beautifulsoup4==4.12.3    # Parsing HTML
lxml==5.2.1              # Parser XML
unidecode==1.3.8         # Normalización de texto
flask==3.0.0             # API REST
playwright               # Navegador automatizado
streamlit                # UI web
matplotlib               # Gráficos
numpy                    # Cálculos
```

### Paso 3: Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env`:
```
GROQ_API_KEY=tu_clave_aqui
GOOGLE_API_KEY=opcional_para_gemini
NEWS_JSON_URL=https://raw.githubusercontent.com/Alfesito/ES-News-Topics/main/news_json/noticias_24h.json
```

**Cómo obtener GROQ_API_KEY:**
1. Ir a https://console.groq.com
2. Registrarse (gratis)
3. Copiar API Key

### Paso 4: Descargar datos iniciales

```bash
# Descargar noticias de hoy
python scraper_cron_lv1.py

# Descargar tendencias
python trends_scraper.py

# Analizar relaciones entre tags
python analyze_news_tags.py
```

---

## 🔄 Cómo Funciona

### Flujo de Datos Diario

```
1. SCRAPING (scraper_cron_lv1.py)
   ├─ Raspa 10 medios
   ├─ Extrae: título, body, tags, imagen
   ├─ Deduplica por hash
   └─ Guarda en noticias_24h.json

2. ENRIQUECIMIENTO (scraper_cron_lv1.py)
   ├─ Carga tag_relations.json
   ├─ TagEnricher busca tags adicionales
   ├─ Añade tags relacionados
   └─ Actualiza noticias_completas.json

3. ANÁLISIS DE TENDENCIAS (trends_scraper.py)
   ├─ Google Trends (volumen de búsqueda)
   ├─ X Trends (trending topics)
   ├─ Cuenta menciones en noticias
   └─ Genera trends_google&x.json

4. ANÁLISIS DE TAGS (analyze_news_tags.py)
   ├─ Construye grafo de co-ocurrencias
   ├─ Identifica clusters
   ├─ Calcula frecuencias
   └─ Actualiza tag_relations.json

5. ANÁLISIS DE OBJETIVIDAD (Objective View/app.py)
   ├─ Carga noticias filtradas
   ├─ Análisis de lenguaje sesgado
   ├─ Análisis de fuentes
   ├─ Análisis de perspectivas
   ├─ Genera score de sesgo (0-100)
   └─ Visualiza resultados interactivos
```

### Ciclo Completo (Recomendado)

```bash
#!/bin/bash
# Ejecutar cada 24 horas

# 1. Descargar noticias nuevas
python scraper_cron_lv1.py

# 2. Mantener histórico (7 días)
python scraper_cron_lv2.py

# 3. Descargar tendencias actuales
python trends_scraper.py

# 4. Recalcular relaciones de tags
python analyze_news_tags.py

# 5. Activar UI de análisis
cd "Objective View"
streamlit run app.py
```

---

## 📚 Módulos Detallados

### A. Base_Scraper.py (Clase Base)

```python
class NewsScraperBase:
    """Base para todos los scrapers"""
    
    def scrape(self) -> List[Dict]:
        """Retorna lista de artículos"""
        
    def _scrape_list_articles(self, soup, base_url):
        """Extrae lista de artículos de portada"""
        
    def _scrape_article_details(self, soup):
        """Extrae detalles del artículo individual"""
```

### B. TagEnricher.py

```python
class TagEnricher:
    """Enriquece tags usando búsqueda de palabras completas"""
    
    def __init__(self, json_url: str):
        """Carga relaciones entre tags"""
        
    def enrich_tags(self, existing_tags, title, subtitle, body):
        """Añade tags basado en tag_relations.json"""
        
    def _is_word_in_text(self, word, text):
        """Busca palabra completa (no substring)"""
```

**Importante:** Usa búsqueda de palabra completa, no substring.
- ✅ "era" en "era importante"
- ❌ "era" en "general está aquí"

### C. advanced_analysis.py (Análisis de Sesgo)

```python
# 6 funciones principales:

1. analizar_lenguaje_sesgado(texto)
   → emotividad, palabras_emotivas, score_neutralidad

2. analizar_atribucion_fuentes(texto)
   → citas_directas, calidad_fuentes, score_atribucion

3. analizar_enfasis_colocacion(titulo, subtitulo, parrafos)
   → que_va_en_titulo, contexto, score_enfasis

4. analizar_equilibrio_perspectivas(texto)
   → balance, menciona_criticas, score_balance

5. calcular_score_sesgo_total(...)
   → score_sesgo_total (0-100, ponderado)

6. generar_reporte_sesgo_detallado(articulo)
   → Reporte completo con indicadores
```

### D. visualization_utils.py (Gráficos)

```python
1. crear_matriz_comparativa(medios)
   → Gráfico barras agrupadas (4 dimensiones)

2. crear_radar_objetividad(medios)
   → Gráfico radar multidimensional

3. crear_scorecard_medio(nombre, datos)
   → Tarjeta visual con 4 métricas

4. generar_resumen_ejecutivo(analisis)
   → Resumen markdown automático
```

---

## 💻 Uso Práctico

### Ejemplo 1: Descargar Noticias Hoy

```python
from Newspapers.api_elpais import ElPaisScraper

scraper = ElPaisScraper()
articulos = scraper.scrape()

for art in articulos[:3]:
    print(f"📰 {art['title']}")
    print(f"   Tags: {', '.join(art['tags'])}")
    print(f"   Fuente: {art['source']}\n")
```

### Ejemplo 2: Enriquecer Tags Automáticamente

```python
from Newspapers.TagEnricher import TagEnricher

enricher = TagEnricher()

articulo = {
    'tags': ['política'],
    'title': 'Nuevo acuerdo gobierno-oposición',
    'subtitle': 'Ambas partes cierran negociación',
    'body': 'Tras meses de conversaciones...'
}

tags_mejorados = enricher.enrich_tags(
    articulo['tags'],
    articulo['title'],
    articulo['subtitle'],
    articulo['body']
)

print(f"Tags originales: {articulo['tags']}")
print(f"Tags mejorados: {tags_mejorados}")
# Output: ['política', 'congreso', 'legislación', ...]
```

### Ejemplo 3: Analizar Sesgo de un Artículo

```python
from Objective_View.advanced_analysis import generar_reporte_sesgo_detallado

articulo = {
    'id': '123',
    'source': 'El País',
    'title': 'Política: Cambios en el gobierno',
    'subtitle': 'Reshuffle ministerial anunciado',
    'body': 'Contenido del artículo...'
}

reporte = generar_reporte_sesgo_detallado(articulo)

print(f"Score de sesgo: {reporte['score_sesgo']:.1f}/100")
print(f"Indicadores clave:")
for ind in reporte['indicadores_clave']:
    print(f"  • {ind}")
```

### Ejemplo 4: Comparar Objetividad Entre Medios

```bash
cd "Objective View"
streamlit run app.py
```

1. Selecciona tags
2. Escribe tema de análisis
3. Espera análisis (2-3 min)
4. Visualiza:
   - Scores por medio
   - Divergencias
   - Indicadores de sesgo
   - Palabras más usadas

---

## ⚙️ API y Configuración

### Variables de Entorno (.env)

```bash
# GROQ (Recomendado - Gratis)
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
GROQ_MODEL=llama-3.1-8b-instant

# GEMINI (Alternativa - Pago)
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxxx

# URLs de datos
NEWS_JSON_URL=https://raw.githubusercontent.com/.../noticias_24h.json

# Logging
LOG_LEVEL=INFO
DEBUG=False
```

### config.py (Objective View)

```python
# Pesos de scoring
SCORE_WEIGHTS = {
    'neutralidad': 0.30,      # Lenguaje
    'atribucion': 0.20,       # Fuentes
    'balance': 0.30,          # Perspectivas
    'enfasis': 0.20           # Énfasis
}

# Umbrales de clasificación
SCORE_THRESHOLDS = {
    'muy_objetivo': 30,
    'mayormente_objetivo': 50,
    'parcialmente_sesgado': 70
}

# Features
ENABLE_ADVANCED_LANGUAGE_ANALYSIS = True
ENABLE_COMPARISON_MATRIX = True
ENABLE_RADAR_CHART = True
```

---

## 🔍 Troubleshooting

### Problema: "ImportError: No module named 'beautifulsoup4'"

**Solución:**
```bash
pip install -r requirements.txt
```

### Problema: GROQ_API_KEY no encontrada

**Solución:**
1. Crea archivo `.env` en raíz del proyecto
2. Añade: `GROQ_API_KEY=tu_clave_aqui`
3. Obtén clave en https://console.groq.com

### Problema: Noticias_24h.json vacío

**Solución:**
```bash
python scraper_cron_lv1.py  # Ejecutar scraper
```

Espera 2-5 minutos según número de medios.

### Problema: TagEnricher no agrega tags

**Solución:**
- Verificar que `tag_relations.json` existe
- Ejecutar: `python analyze_news_tags.py`
- Asegurar que palabras son búsqueda completa (no substring)

### Problema: Streamlit muy lento

**Solución:**
- Reducir número de artículos: `MAX_ARTICULOS = 30`
- Usar modelo más rápido: `llama-3.1-8b-instant`
- Limpiar cache: `streamlit cache clear`

### Problema: "Permission denied" en Linux/Mac

**Solución:**
```bash
chmod +x scraper_cron_lv1.py
chmod +x trends_scraper.py
```

---

## 📊 Formatos de Datos

### JSON de Noticias (noticias_24h.json)

```json
[
  {
    "id": "eldiario_20260131_abc123",
    "source": "El Diario",
    "title": "Título de la noticia",
    "subtitle": "Subtítulo",
    "body": "Contenido...",
    "tags": ["política", "congreso", "legislatura"],
    "author": "Juan García",
    "date": "2026-01-31T15:30:00",
    "link": "https://www.eldiario.es/...",
    "image": {
      "url": "https://...",
      "credits": "Foto: EFE"
    },
    "hash": "a1b2c3d4e5f6"
  }
]
```

### JSON de Tendencias (trends_google&x.json)

```json
[
  {
    "id": 1,
    "title": "Tema tendencia",
    "source": "Google Trends",
    "volume": 850000,
    "timeframe": "last_24h",
    "news_count": 127
  }
]
```

### JSON de Relaciones (tag_relations.json)

```json
{
  "metadata": {
    "total_tags": 523,
    "total_articles": 1200,
    "total_relations": 2847,
    "total_clusters": 42
  },
  "tag_stats": {
    "Política": {
      "frequency": 234,
      "related_count": 15,
      "related_tags": ["Congreso", "Gobierno", ...]
    }
  },
  "clusters": [
    {
      "size": 8,
      "tags": ["Política", "Congreso", "Legislatura", ...]
    }
  ]
}
```

---

## 🎯 Casos de Uso

### 1. Monitoreo de Cobertura
Seguimiento de cómo diferentes medios cubren un tema.

```bash
python scraper_cron_lv1.py
# Luego abrir: Objective View → Seleccionar tags → Analizar
```

### 2. Detección de Sesgos
Identificar sesgo editorial en artículos específicos.

```bash
cd "Objective View"
streamlit run app.py
# Seleccionar tema → Ver scores por medio
```

### 3. Análisis de Tendencias
Entender qué está tendiendo vs qué se cubre.

```bash
python trends_scraper.py
# Compara Google Trends con cobertura real
```

### 4. Investigación de Relaciones
Encontrar cómo se relacionan diferentes temas.

```bash
python analyze_news_tags.py
# Ver clusters de tags relacionados
```

### 5. Alimentar Aplicaciones
Servir noticias vía API REST.

```bash
python news_api_app.py
# GET http://localhost:5000/noticias
```

---

## 🚀 Próximas Mejoras (Roadmap)

### Fase 2 (Febrero 2026)
- [ ] Análisis de imágenes (detectar sesgo visual)
- [ ] Dashboard histórico (tendencias temporales)
- [ ] Seguimiento por medio (scoring histórico)

### Fase 3 (Marzo 2026)
- [ ] Análisis de comentarios (sentimiento lector)
- [ ] Detección de clickbait
- [ ] Desinformación específica

### Fase 4 (Abril 2026)
- [ ] Exportación PDF con gráficos
- [ ] API pública (para otros desarrolladores)
- [ ] Machine learning (predicción de sesgo)

---

## 📝 Contribuir

### Reportar Bugs
1. Abre issue en GitHub
2. Incluye: versión Python, logs de error, pasos para reproducir

### Añadir Medios
1. Crea `Newspapers/api_nuevo_medio.py`
2. Hereda de `Base_Scraper`
3. Implementa `_scrape_list_articles()` y `_scrape_article_details()`
4. Añade a `scraper_cron_lv1.py`

### Mejorar Análisis
1. Edita `advanced_analysis.py`
2. Añade nuevas dimensiones o métricas
3. Actualiza `config.py` si necesario
4. Ejecuta tests

---

## 📞 Soporte y Contacto

- **Issues**: GitHub Issues
- **Email**: contacto@proyecto.es
- **Documentación**: Este archivo
- **API Reference**: `QUICK_REFERENCE.py`
- **Ejemplos**: `ejemplo_uso.py`

---

## 📄 Licencia

MIT License - Ver LICENSE.md

---

## 🙏 Agradecimientos

- BeautifulSoup4 (web scraping)
- Groq API (análisis IA - gratis)
- Streamlit (UI)
- Comunidad open source

---

**Última actualización:** 31 de enero de 2026  
**Versión:** 2.0  
**Status:** ✅ Estable y Funcional  

---

## 📈 Estadísticas

- **Medios soportados**: 10
- **Artículos/día**: 500+
- **Tags únicos**: 500+
- **Dimensiones de análisis**: 6+
- **Líneas de código**: 5000+
- **Documentación**: 100+ páginas

---

**¡Gracias por usar ES-News-Topics!** 🎉

Para más información, consulta los archivos README en cada carpeta.
