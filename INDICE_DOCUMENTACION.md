# 📚 ÍNDICE DE DOCUMENTACIÓN - ES-News-Topics

**Mapa completo de toda la documentación del proyecto**

---

## 📖 Documentación Principal

### Para Empezar
- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** ⭐ **COMIENZA AQUÍ**
  - Setup en 5 minutos
  - Comandos principales
  - Casos de uso rápidos
  - Troubleshooting común

### Documentación Completa
- **[DOCUMENTACION_COMPLETA.md](DOCUMENTACION_COMPLETA.md)** 📖 **REFERENCIA COMPLETA**
  - Visión general del proyecto
  - Estructura detallada
  - Componentes y módulos
  - API y configuración
  - Casos de uso avanzados

---

## 🎯 Módulo: Objective View (Análisis de Objetividad)

### Documentación
- **[Objective View/MEJORAS.md](Objective%20View/MEJORAS.md)**
  - Mejoras en v2.0
  - 6 dimensiones de análisis
  - Visualizaciones
  - Antes vs Después

- **[Objective View/CHANGELOG.md](Objective%20View/CHANGELOG.md)**
  - Historial de versiones
  - Cambios recientes
  - Roadmap futuro
  - Bugs arreglados

- **[Objective View/RESUMEN_MEJORAS.txt](Objective%20View/RESUMEN_MEJORAS.txt)**
  - Resumen ejecutivo
  - Impacto de cambios
  - Checklist de features

### Referencia de API
- **[Objective View/QUICK_REFERENCE.py](Objective%20View/QUICK_REFERENCE.py)**
  - Guía de funciones
  - Ejemplos de código
  - Estructura de datos
  - Interpretación de scores

### Ejemplos
- **[Objective View/ejemplo_uso.py](Objective%20View/ejemplo_uso.py)**
  - Demos prácticas
  - Compara artículo objetivo vs sesgado
  - Ejecutable: `python Objective\ View/ejemplo_uso.py`

### Configuración
- **[Objective View/config.py](Objective%20View/config.py)**
  - Features ON/OFF
  - Pesos de scoring
  - Umbrales de clasificación
  - Palabras clave

---

## 🗂️ Guía de Carpetas

### Newspapers/ (Scrapers)
Contiene scrapers para 10 medios españoles.

**Archivos principales:**
- `api_elpais.py` - El País
- `api_eldiario.py` - El Diario
- `api_larazon.py` - La Razón
- (+ 7 más)

**Clase base:**
- `Base_Scraper.py` - Plantilla para nuevos scrapers

**Enriquecimiento:**
- `TagEnricher.py` - Expande tags automáticamente

**Uso:**
```python
from Newspapers.api_elpais import ElPaisScraper
scraper = ElPaisScraper()
articulos = scraper.scrape()
```

### Utils/ (Utilidades)
Funciones generales para procesar datos.

- `Article_Utils.py` - Procesar artículos
- `Date_Utils.py` - Manejo de fechas
- `Id_Utils.py` - Generación de IDs
- `Image_Utils.py` - Procesar imágenes
- `Text_Utils.py` - Procesar texto

### Http_Client/ (Cliente HTTP)
Cliente HTTP personalizado.

- `http_client.py` - Descarga con reintentos
- `user_agents.py` - User agents variados

### Scraper/ (Base)
- `Base_Scraper.py` - Clase base para todos los scrapers

### Flask_App/ (API REST)
- `Flask_App.py` - API HTTP experimental

### Objective View/ (Análisis)
Sistema completo de análisis de objetividad.

Ver sección anterior para detalles.

---

## 🔧 Scripts Principales

### scraper_cron_lv1.py
**Descarga noticias de hoy**

```bash
python scraper_cron_lv1.py
```

- Raspa 10 medios
- Enriquece tags con TagEnricher
- Genera: `news_json/noticias_24h.json`
- Tiempo: 2-5 minutos

### scraper_cron_lv2.py
**Mantiene histórico de 7 días**

```bash
python scraper_cron_lv2.py
```

- Carga histórico anterior
- Añade noticias nuevas
- Genera: `news_json/noticias_completas.json`
- Tiempo: 1-2 minutos

### trends_scraper.py
**Descarga tendencias Google + X**

```bash
python trends_scraper.py
```

- Google Trends (últimas 24h)
- X Trends (trending topics)
- Cuenta menciones en noticias
- Genera: `tags_json/trends_google&x.json`
- Tiempo: 3-5 minutos

### analyze_news_tags.py
**Analiza relaciones entre tags**

```bash
python analyze_news_tags.py
```

- Construye grafo de co-ocurrencias
- Identifica clusters
- Calcula frecuencias
- Genera: `tags_json/tag_relations.json`
- Tiempo: 1-2 minutos

### news_api_app.py
**API REST para noticias**

```bash
python news_api_app.py
```

- GET /noticias - Últimas noticias
- GET /tendencias - Tendencias
- GET /tags - Tags disponibles

### Objective View/app.py
**Interfaz web de análisis**

```bash
cd "Objective View"
streamlit run app.py
```

- Análisis de objetividad
- Visualizaciones interactivas
- 4 tabs principales
- Abre: http://localhost:8501

---

## 📊 Flujo de Datos

```
scraper_cron_lv1.py
├─ Descarga noticias
├─ Enriquece tags (TagEnricher)
└─ Genera: noticias_24h.json

scraper_cron_lv2.py
├─ Carga histórico
├─ Añade noticias nuevas
└─ Genera: noticias_completas.json

trends_scraper.py
├─ Google Trends + X Trends
└─ Genera: trends_google&x.json

analyze_news_tags.py
├─ Construye grafo
├─ Identifica clusters
└─ Genera: tag_relations.json

Objective View/app.py
├─ Carga noticias
├─ Análisis avanzado
└─ Visualiza resultados
```

---

## 💾 Base de Datos (JSON)

### news_json/noticias_24h.json
Últimas 24 horas, ~500 artículos

**Estructura:**
```json
[
  {
    "id": "único",
    "source": "Medio",
    "title": "Título",
    "body": "Contenido",
    "tags": ["tag1", "tag2"],
    "date": "ISO 8601",
    "link": "URL"
  }
]
```

### news_json/noticias_completas.json
Histórico 7 días, ~3500 artículos

### tags_json/trends_google&x.json
Tendencias actuales, ~200 trends

**Estructura:**
```json
[
  {
    "id": 1-99,
    "title": "Tema",
    "source": "Google Trends",
    "volume": 850000,
    "news_count": 127
  }
]
```

### tags_json/tag_relations.json
Relaciones entre tags, clusters, frecuencias

**Estructura:**
```json
{
  "metadata": {...},
  "tag_stats": {...},
  "clusters": [...],
  "direct_relations": {...}
}
```

---

## 🎓 Aprendizaje Progresivo

### Nivel 1: Principiante
1. Lee **INICIO_RAPIDO.md**
2. Ejecuta `python scraper_cron_lv1.py`
3. Abre `Objective View/app.py`
4. Juega con la interfaz

### Nivel 2: Intermedio
1. Lee **DOCUMENTACION_COMPLETA.md**
2. Ejecuta `python Objective\ View/ejemplo_uso.py`
3. Examina `news_json/noticias_24h.json`
4. Modifica `config.py`

### Nivel 3: Avanzado
1. Lee `Objective View/QUICK_REFERENCE.py`
2. Estudia `advanced_analysis.py`
3. Crea nuevo scraper en `Newspapers/`
4. Contribuye con mejoras

---

## 🔍 Buscar Información

| Quiero saber... | Dónde encontrarlo |
|-----------------|------------------|
| Cómo empezar rápido | INICIO_RAPIDO.md |
| Visión completa | DOCUMENTACION_COMPLETA.md |
| Cómo usar función X | QUICK_REFERENCE.py |
| Qué cambió en v2.0 | MEJORAS.md |
| Qué se vuelto a quebrar | CHANGELOG.md |
| Ejemplos de código | ejemplo_uso.py |
| Cómo configurar | config.py |
| Problemas comunes | DOCUMENTACION_COMPLETA.md → Troubleshooting |

---

## ✨ Quick Links

| Recurso | URL |
|---------|-----|
| GitHub Repo | https://github.com/Alfesito/ES-News-Topics |
| Groq Console | https://console.groq.com |
| Streamlit Docs | https://docs.streamlit.io |
| BeautifulSoup Docs | https://www.crummy.com/software/BeautifulSoup/ |

---

## 📞 Soporte

- **Preguntas:** Lee DOCUMENTACION_COMPLETA.md
- **API Help:** Ver QUICK_REFERENCE.py
- **Bugs:** Abre GitHub Issues
- **Ejemplos:** Ejecuta ejemplo_uso.py

---

## 🗺️ Mapa de Archivos Importantes

```
ES-News-Topics/
│
├── 📘 INICIO_RAPIDO.md              ← COMIENZA AQUÍ
├── 📖 DOCUMENTACION_COMPLETA.md     ← REFERENCIA COMPLETA
├── 📚 INDICE_DOCUMENTACION.md       ← TÚ ESTÁS AQUÍ
│
├── 🔧 Scripts principales
│   ├── scraper_cron_lv1.py
│   ├── scraper_cron_lv2.py
│   ├── trends_scraper.py
│   └── analyze_news_tags.py
│
├── 📂 Objective View/
│   ├── app.py                        ← Ejecutar: streamlit run app.py
│   ├── advanced_analysis.py          ← Motor de análisis
│   ├── visualization_utils.py        ← Gráficos
│   ├── config.py                     ← Configuración
│   ├── 📖 MEJORAS.md                ← Mejoras v2.0
│   ├── 📖 CHANGELOG.md              ← Historial
│   ├── 📖 QUICK_REFERENCE.py        ← API reference
│   ├── 📄 ejemplo_uso.py             ← Ejecutar: python ejemplo_uso.py
│   └── analisis_historico.json      ← DB de análisis
│
├── 📂 Newspapers/
│   ├── (10 scrapers por medio)
│   ├── Base_Scraper.py
│   └── TagEnricher.py
│
├── 📂 Utils/
│   └── (funciones generales)
│
├── 📂 news_json/
│   ├── noticias_24h.json
│   └── noticias_completas.json
│
└── 📂 tags_json/
    ├── tag_relations.json
    └── trends_google&x.json
```

---

## ✅ Checklist de Lectura

- [ ] He leído INICIO_RAPIDO.md
- [ ] He instalado todo correctamente
- [ ] He ejecutado primer scraper
- [ ] Abrí la interfaz web
- [ ] Ejecuté ejemplo_uso.py
- [ ] Leí DOCUMENTACION_COMPLETA.md
- [ ] Entiendo la estructura de datos
- [ ] Sé dónde encontrar ayuda

---

**¡Está todo documentado!** 📚

**Próximo paso:** Abre [INICIO_RAPIDO.md](INICIO_RAPIDO.md) para empezar en 5 minutos.

---

Última actualización: 31 de enero de 2026
