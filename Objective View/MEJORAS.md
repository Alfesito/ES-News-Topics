# 🚀 MEJORAS A "OBJECTIVE VIEW" - ANÁLISIS AVANZADO DE OBJETIVIDAD

## 📋 Resumen de Cambios

Se ha mejorado significativamente el análisis de objetividad de noticias con un sistema mucho más sofisticado que va más allá del análisis básico anterior.

---

## 🎯 NUEVAS CARACTERÍSTICAS

### 1. **Análisis Avanzado de Lenguaje** 
Archivo: `advanced_analysis.py`

**¿Qué detecta?**
- ✅ Palabras emotivas y cargadas (positivas/negativas)
- ✅ Intensificadores ("claramente", "obviamente") que fuerzan opinión
- ✅ Patrones de lenguaje sesgado:
  - Personalización negativa
  - Generalización de grupos
  - Victimización
  - Dehumanización
- ✅ Score de neutralidad (0-100)

**Ejemplo:**
```
Frase sesgada: "Claramente el corrupto ex-ministro fue el culpable"
Score: 85/100 (muy sesgado)
- Intensificador: "claramente"
- Personalización negativa: "corrupto"
- Palabras cargadas: 2
```

### 2. **Análisis de Atribución de Fuentes**
**¿Qué detecta?**
- ✅ Citas directas vs indirectas
- ✅ Afirmaciones sin fuente (amarillismo)
- ✅ Tipos de fuentes usadas:
  - Oficial (gobierno, autoridades)
  - Experto (investigadores, académicos)
  - Testigo (víctimas, presentes)
  - Anónima (problemático)
- ✅ Score de calidad de fuentes

**Impacto:**
- Articulo con pocas citas = menos confiable
- Artículo sin fuentes = información no verificada

### 3. **Análisis de Énfasis y Colocación**
**¿Qué detecta?**
- ✅ Qué información va en el titular (más visible)
- ✅ Qué va en los primeros párrafos (relevancia percibida)
- ✅ Información que se deja al final (menos vista)
- ✅ Proporción de contexto histórico
- ✅ Score de énfasis equilibrado

**Ejemplo:**
```
Titular enfatiza: "Crítica al gobierno" (opinión)
Hecho real va al final: "Datos muestran lo opuesto"
Score: 35/100 (muy sesgado)
```

### 4. **Análisis de Balance de Perspectivas**
**¿Qué detecta?**
- ✅ ¿Solo presenta una perspectiva? (unilateral)
- ✅ ¿Menciona críticas? (construcción de balance)
- ✅ ¿Presenta posiciones opuestas? (equidad)
- ✅ Palabras de contraste: "sin embargo", "por otra parte"
- ✅ Score de balance (0-100)

**Clasificación:**
- 0-30: Unilateral ❌
- 30-60: Parcial ⚠️
- 60-100: Equilibrado ✅

---

## 📊 NUEVO PROMPT PARA LAS IA (Groq/Gemini)

El prompt ahora **obliga** a la IA a proporcionar:

### Scores Numéricos Granulares (0-100):
```json
{
  "score_sesgo_0_100": 45,
  "score_neutralidad": 75,
  "score_atribucion": 80,
  "score_balance": 70,
  "score_enfasis": 65
}
```

### Análisis Detallado por Medio:
```json
"analisis_detallado_sesgo": {
  "El País": {
    "score_sesgo_0_100": 35,
    "clasificacion": "Mayormente objetivo",
    "lenguaje": {
      "nivel_emotividad_0_100": 25,
      "palabras_cargadas": ["análisis", "perspectiva"],
      "intensificadores": []
    },
    "atribucion_fuentes": {
      "citas_directas": 8,
      "citas_indirectas": 12,
      "score_calidad_fuentes_0_100": 85
    },
    "indicadores_clave_de_sesgo": [],
    "puntos_fuertes": ["Buen uso de fuentes", "Contexto histórico"],
    "areas_mejora": ["Más perspectivas opuestas"]
  }
}
```

### Matriz Comparativa:
```json
"matriz_comparativa": {
  "medio_mas_objetivo": "El País",
  "score_mas_objetivo": 35,
  "medio_mas_sesgado": "Medio X",
  "score_mas_sesgado": 70,
  "diferencia_maxima_score": 35,
  "consensus_nivel": "Bajo - Divergencias significativas"
}
```

### Palabras Frecuentes por Medio:
```json
"palabras_mas_frecuentes_por_medio": {
  "El País": {
    "positivas": ["progreso", "logro", "avance"],
    "negativas": ["crisis", "problemático"],
    "neutras": ["afirma", "según", "datos"]
  }
}
```

---

## 🎨 NUEVAS VISUALIZACIONES EN APP

### 1. **Gráfico de Barras Horizontal**
- Muestra el score de sesgo de cada medio
- Colores: Verde (objetivo) → Amarillo (parcial) → Rojo (sesgado)
- Valores exactos sobre cada barra

### 2. **Matriz Comparativa (Clustered Bar Chart)**
- Compara 4 dimensiones de cada medio:
  - Objetividad
  - Calidad de Fuentes
  - Balance de Perspectivas
  - Énfasis Equilibrado

### 3. **Gráfico Radar (Spider Chart)**
- Análisis multidimensional de cada medio
- 5 ejes: Neutralidad, Fuentes, Balance, Contexto, Claridad
- Permite ver fortalezas y debilidades de un vistazo

### 4. **Tarjetas de Metrics Mejoradas**
```
🏆 Más Objetivo: El País (Score: 35)
⚠️ Más Sesgado: Medio X (Score: 70)
📊 Diferencia: 35 puntos
🤝 Consenso: Bajo
```

### 5. **Tabla de Divergencias Interactiva**
- Aspecto principal de divergencia
- Diferencia detectada
- Número de medios afectados
- Perspectiva de cada medio

---

## 🔢 ESCALA DE INTERPRETATION

### Score de Sesgo (0-100):
```
0-30:   Muy objetivo ✅ (Excelente)
30-50:  Mayormente objetivo 👍 (Bueno)
50-70:  Parcialmente sesgado ⚠️ (Mejorable)
70-100: Muy sesgado 🚩 (Problemático)
```

### Tabla de Dimensiones:
| Dimensión | 0-30 | 30-50 | 50-70 | 70-100 |
|-----------|------|-------|-------|--------|
| **Neutralidad** | Muy neutral | Neutral | Algo emotivo | Muy emotivo |
| **Fuentes** | Excelentes | Buenas | Déficit | Pobres |
| **Balance** | Equilibrado | Mayormente | Unilateral | Muy sesgado |
| **Contexto** | Completo | Adecuado | Insuficiente | Falta |

---

## 📁 NUEVOS ARCHIVOS CREADOS

1. **`advanced_analysis.py`** (250+ líneas)
   - Análisis de lenguaje sesgado
   - Análisis de fuentes
   - Análisis de énfasis
   - Análisis de perspectivas
   - Scoring granular

2. **`visualization_utils.py`** (250+ líneas)
   - Gráfico de matriz comparativa
   - Gráfico radar
   - Scorecard de medios
   - Resumen ejecutivo

3. **Actualizaciones en `app.py`**
   - Importación de nuevas funciones
   - Visualizaciones mejoradas en tab2 y tab3
   - Mejor organización de resultados

4. **Actualización en `utils_groq.py`**
   - Nuevo prompt más detallado
   - Estructura JSON mejorada
   - Scores granulares por defecto

---

## 🚀 CÓMO USAR LAS NUEVAS MEJORAS

### En la UI (Streamlit):

**Tab 1 - Resumen:**
- Ves un resumen ejecutivo con puntos clave
- Matriz comparativa de medios
- Análisis 5W+1H detallado

**Tab 2 - Estadísticas:**
- Gráfico de barras horizontal (scores por medio)
- Gráfico radar (multidimensional)
- Matriz comparativa

**Tab 3 - Sesgos Detectados:**
- Tabla comparativa de 4 dimensiones
- Análisis detallado por medio con:
  - Lenguaje (emotividad, palabras cargadas)
  - Fuentes (citas directas, calidad)
  - Énfasis (info. principal, contexto)
  - Perspectivas (balance, menciones de críticas)
- Indicadores de sesgo específicos
- Puntos fuertes y áreas de mejora

**Tab 4 - Divergencias:**
- Divergencias principales con contexto
- Impacto en percepción del lector
- Perspectiva de cada medio
- Recomendación para obtener visión completa

---

## 💡 VENTAJAS DEL NUEVO SISTEMA

✅ **Más objetivo**: Análisis basado en métricas, no en opinión
✅ **Más detallado**: 50+ indicadores vs 3-5 anteriores
✅ **Más visual**: 4 tipos de gráficos + tablas interactivas
✅ **Más accionable**: Recomendaciones específicas por medio
✅ **Más comparable**: Scores numéricos facilitan comparación
✅ **Más educativo**: Explica qué es sesgo, cómo detectarlo
✅ **Más reproducible**: Otros pueden verificar el análisis

---

## 🔄 INTEGRACIÓN CON ADVANCED_ANALYSIS.PY

Aunque el archivo `advanced_analysis.py` está listo para usar, el prompt actual de Groq ya implementa todos estos análisis internamente. Si quieres usar las funciones de `advanced_analysis.py` para pre-procesar artículos antes de enviar a la IA, puedes:

```python
from advanced_analysis import generar_reporte_sesgo_detallado

for articulo in articulos:
    reporte = generar_reporte_sesgo_detallado(articulo)
    # Usar datos locales + datos de Groq
```

---

## 📝 PRÓXIMAS MEJORAS POSIBLES

- [ ] Análisis de imágenes usadas (sesgo visual)
- [ ] Seguimiento histórico de sesgo por medio
- [ ] Comparación temporal (¿Cambió el sesgo con el tiempo?)
- [ ] Análisis de comentarios de lectores
- [ ] Scoring de clickbait en títulos
- [ ] Detección de desinformación específica
- [ ] Exportar análisis en PDF con gráficos

---

## 🎓 REFERENCIAS Y METODOLOGÍA

Los análisis se basan en:
- **Análisis de lenguaje**: Estudios de Lakoff sobre marcos narrativos
- **Atribución de fuentes**: Estándares de periodismo verificable
- **Énfasis**: Teoría de agenda-setting
- **Perspectivas**: Principio de equidad editorial

---

**Versión:** 2.0 - Enero 2026
**Última actualización:** 31 de enero de 2026
