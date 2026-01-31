# 🚀 ES-News-Topics - Guía de Inicio Rápido

**Para empezar en 5 minutos**

---

## ⚡ Quick Start (5 minutos)

### 1. Instalación

```bash
git clone https://github.com/Alfesito/ES-News-Topics.git
cd ES-News-Topics
pip install -r requirements.txt
```

### 2. Configurar API

```bash
echo "GROQ_API_KEY=tu_clave_aqui" > .env
```

Obtén clave gratis en: https://console.groq.com

### 3. Descargar noticias

```bash
python scraper_cron_lv1.py
```

### 4. Abrir interfaz web

```bash
cd "Objective View"
streamlit run app.py
```

Abre navegador: http://localhost:8501

---

## 📋 Comandos Principales

| Comando | Qué hace | Tiempo |
|---------|----------|--------|
| `python scraper_cron_lv1.py` | Descarga noticias de hoy | 2-5 min |
| `python trends_scraper.py` | Descarga tendencias Google + X | 3-5 min |
| `python analyze_news_tags.py` | Analiza relaciones entre tags | 1-2 min |
| `streamlit run Objective\ View/app.py` | Inicia interfaz web | Inmediato |
| `python news_api_app.py` | Inicia API REST | Inmediato |

---

## 🎯 Casos de Uso

### Caso 1: Ver Noticias de Hoy
```bash
python scraper_cron_lv1.py
# Abre: news_json/noticias_24h.json
```

### Caso 2: Analizar Sesgo de Medios
```bash
cd "Objective View"
streamlit run app.py
# 1. Selecciona tags
# 2. Escribe tema
# 3. Espera 2-3 min
# 4. Visualiza análisis
```

### Caso 3: Enriquecer Tags Automáticamente
```python
from Newspapers.TagEnricher import TagEnricher

enricher = TagEnricher()
new_tags = enricher.enrich_tags(
    ["política"],
    "Título",
    "Subtítulo",
    "Contenido..."
)
```

### Caso 4: Descargar Tendencias
```bash
python trends_scraper.py
# Genera: tags_json/trends_google&x.json
```

### Caso 5: Usar API REST
```bash
python news_api_app.py
# GET http://localhost:5000/noticias
# GET http://localhost:5000/tendencias
```

---

## 📊 Estructura Minimal Entender

```
ES-News-Topics/
├── Newspapers/          ← Scrapers (descarga de medios)
├── Objective View/      ← Análisis de sesgo (interfaz web)
├── news_json/          ← Base de datos (noticias)
├── tags_json/          ← Base de datos (tendencias y tags)
└── *.py                ← Scripts de automation
```

---

## 🔑 Conceptos Clave

### 1. Scraping
**Qué es:** Descargar noticias de medios automáticamente

**Archivos:**
- `scraper_cron_lv1.py` - Descargar noticias nuevas
- `scraper_cron_lv2.py` - Mantener histórico

### 2. Enriquecimiento
**Qué es:** Añadir más tags basado en contenido

**Archivo:**
- `Newspapers/TagEnricher.py` - Enriquecedor

### 3. Tendencias
**Qué es:** Qué está trending en Google + X

**Archivo:**
- `trends_scraper.py` - Descargador de tendencias

### 4. Análisis de Objetividad
**Qué es:** Detectar sesgo en artículos

**Archivo:**
- `Objective View/app.py` - Interfaz web
- `advanced_analysis.py` - Motor de análisis

---

## 📁 Archivos Importantes

| Archivo | Propósito | Usar cuando... |
|---------|-----------|----------------|
| `news_json/noticias_24h.json` | BD de noticias | Necesitas acceder a noticias |
| `tags_json/trends_google&x.json` | DB de tendencias | Necesitas saber qué está trending |
| `tags_json/tag_relations.json` | Relaciones de tags | Necesitas expandir tags |
| `.env` | Credenciales | Guardas API keys |
| `Objective View/analisis_historico.json` | Histórico de análisis | Necesitas histórico de sesgos |

---

## 🐛 Problemas Comunes

### "No module named 'beautifulsoup4'"
```bash
pip install -r requirements.txt
```

### "GROQ_API_KEY not found"
```bash
# Crear .env
echo "GROQ_API_KEY=tu_clave" > .env
```

### Noticias vacías
```bash
# Ejecutar scraper
python scraper_cron_lv1.py
# Esperar 2-5 minutos
```

### Streamlit muy lento
```python
# En config.py:
MAX_ARTICULOS = 30  # Reducir
GROQ_MODEL = "llama-3.1-8b-instant"  # Usar más rápido
```

---

## 📚 Próximos Pasos

1. **Aprender más:**
   - Lee `DOCUMENTACION_COMPLETA.md` para detalle
   - Revisa `QUICK_REFERENCE.py` para API

2. **Personalizar:**
   - Edita `config.py` en Objective View
   - Modifica `EXCLUDED_TERMS` en trends_scraper.py

3. **Automatizar:**
   - Usa cron para ejecutar scripts diarios
   - Setup en servidor para obtener datos 24/7

4. **Extender:**
   - Añade nuevos medios en `Newspapers/`
   - Crea nuevas métricas en `advanced_analysis.py`

---

## 🎓 Aprender Más

### Documentación General
`DOCUMENTACION_COMPLETA.md` - Todo sobre el proyecto

### Referencia de API
`Objective View/QUICK_REFERENCE.py` - Funciones disponibles

### Ejemplos de Código
`Objective View/ejemplo_uso.py` - Demostración práctica

### Novedades
`Objective View/CHANGELOG.md` - Qué cambió en v2.0

---

## ✅ Checklist de Setup

- [ ] Python 3.9+ instalado
- [ ] Git instalado
- [ ] Repositorio clonado
- [ ] requirements.txt instalado
- [ ] .env creado con GROQ_API_KEY
- [ ] scraper_cron_lv1.py ejecutado
- [ ] noticias_24h.json no vacío
- [ ] Streamlit abierto sin errores

---

## 🆘 Necesito Ayuda

1. **Error de código:** Revisa `DOCUMENTACION_COMPLETA.md` → Troubleshooting
2. **Cómo usar función:** Abre `Objective View/QUICK_REFERENCE.py`
3. **Ejemplo:** Ejecuta `python Objective\ View/ejemplo_uso.py`
4. **Issue del repo:** Abre GitHub Issues

---

## 🚀 Siguientes Pasos

```bash
# 1. Entender estructura
cat DOCUMENTACION_COMPLETA.md

# 2. Ver ejemplo en vivo
python Objective\ View/ejemplo_uso.py

# 3. Descargar primeras noticias
python scraper_cron_lv1.py

# 4. Analizar objetividad
cd Objective\ View
streamlit run app.py

# 5. Explorar API
python news_api_app.py
```

---

**¡Ya estás listo para usar ES-News-Topics!** 🎉

Próximo: Leer `DOCUMENTACION_COMPLETA.md` para aprender más.
