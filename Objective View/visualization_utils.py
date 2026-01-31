"""
Visualización Avanzada para Análisis de Objetividad
Gráficos y métricas sofisticadas
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import streamlit as st

def crear_matriz_comparativa(medios: Dict) -> plt.Figure:
    """
    Crea una matriz de comparación entre medios en múltiples dimensiones.
    
    Dimensiones:
    - Objetividad (0-100)
    - Calidad de Fuentes (0-100)
    - Balance de Perspectivas (0-100)
    - Claridad/Contexto (0-100)
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    medios_nombres = list(medios.keys())
    
    # Extraer scores
    scores_objetividad = []
    scores_fuentes = []
    scores_balance = []
    scores_enfasis = []
    
    for medio_data in medios.values():
        scores_objetividad.append(100 - medio_data.get('score_sesgo_0_100', 50))
        scores_fuentes.append(medio_data.get('atribucion_fuentes', {}).get('score_calidad_fuentes_0_100', 50))
        scores_balance.append(medio_data.get('balance_perspectivas', {}).get('score_balance_0_100', 50))
        scores_enfasis.append(medio_data.get('enfasis_colocacion', {}).get('score_enfasis_equilibrado_0_100', 50))
    
    x = np.arange(len(medios_nombres))
    width = 0.2
    
    ax.bar(x - 1.5*width, scores_objetividad, width, label='Objetividad', color='#2ecc71')
    ax.bar(x - 0.5*width, scores_fuentes, width, label='Fuentes', color='#3498db')
    ax.bar(x + 0.5*width, scores_balance, width, label='Perspectivas', color='#e74c3c')
    ax.bar(x + 1.5*width, scores_enfasis, width, label='Énfasis', color='#f39c12')
    
    ax.set_ylabel('Score (0-100)', fontsize=12, fontweight='bold')
    ax.set_title('Matriz Comparativa de Objetividad por Medio', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(medios_nombres, rotation=45, ha='right')
    ax.legend(loc='upper left')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig


def crear_radar_objetividad(medios: Dict) -> plt.Figure:
    """
    Crea un gráfico radar mostrando múltiples dimensiones de sesgo.
    """
    from math import pi
    
    categorias = ['Neutralidad', 'Fuentes', 'Balance', 'Contexto', 'Claridad']
    N = len(categorias)
    
    fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
    
    # Calcular ángulos
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    colores = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6']
    
    for idx, (medio_nombre, medio_data) in enumerate(medios.items()):
        valores = [
            100 - medio_data.get('lenguaje', {}).get('nivel_emotividad_0_100', 50),
            medio_data.get('atribucion_fuentes', {}).get('score_calidad_fuentes_0_100', 50),
            medio_data.get('balance_perspectivas', {}).get('score_balance_0_100', 50),
            70 if medio_data.get('enfasis_colocacion', {}).get('proporciona_contexto') else 30,
            80
        ]
        valores += valores[:1]
        
        ax.plot(angles, valores, 'o-', linewidth=2, label=medio_nombre, color=colores[idx % len(colores)])
        ax.fill(angles, valores, alpha=0.15, color=colores[idx % len(colores)])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias, size=11)
    ax.set_ylim(0, 100)
    ax.set_title('Análisis Multidimensional de Objetividad', size=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    plt.tight_layout()
    return fig


def crear_tabla_divergencias(divergencias: List) -> str:
    """
    Crea una tabla HTML con las divergencias principales.
    """
    if not divergencias:
        return "No hay divergencias"
    
    html = """
    <table style="width:100%; border-collapse: collapse;">
        <tr style="background-color: #3498db; color: white; font-weight: bold;">
            <th style="border: 1px solid #ddd; padding: 8px;">Aspecto</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Divergencia</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Medios Afectados</th>
        </tr>
    """
    
    for div in divergencias:
        aspecto = div.get('aspecto', 'N/A')
        diferencia = div.get('diferencia', 'N/A')[:80]
        perspectivas = div.get('perspectivas_medios', {})
        num_medios = len(perspectivas)
        
        html += f"""
        <tr style="background-color: {'#ecf0f1' if div.get('impacto_percepcion') else '#ffffff'};">
            <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">{aspecto}</td>
            <td style="border: 1px solid #ddd; padding: 8px;">{diferencia}...</td>
            <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{num_medios}</td>
        </tr>
        """
    
    html += "</table>"
    return html


def crear_scorecard_medio(medio_nombre: str, datos: Dict) -> None:
    """
    Crea una tarjeta visual con los scores de un medio.
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = datos.get('score_sesgo_0_100', 50)
        color = '🟢' if score < 30 else '🟡' if score < 50 else '🔴'
        st.metric(
            "Sesgo Total",
            f"{score:.0f}/100",
            f"{score:.0f}",
            delta_color="inverse"
        )
    
    with col2:
        neutralidad = 100 - datos.get('lenguaje', {}).get('nivel_emotividad_0_100', 50)
        st.metric(
            "Neutralidad",
            f"{neutralidad:.0f}%",
            "Lenguaje"
        )
    
    with col3:
        fuentes = datos.get('atribucion_fuentes', {}).get('score_calidad_fuentes_0_100', 50)
        st.metric(
            "Calidad Fuentes",
            f"{fuentes:.0f}%",
            "Atribución"
        )
    
    with col4:
        balance = datos.get('balance_perspectivas', {}).get('score_balance_0_100', 50)
        st.metric(
            "Balance",
            f"{balance:.0f}%",
            "Perspectivas"
        )


def generar_resumen_ejecutivo(analisis: Dict) -> str:
    """
    Genera un resumen ejecutivo del análisis.
    """
    matriz = analisis.get('matriz_comparativa', {})
    
    resumen = f"""
    ## 📊 RESUMEN EJECUTIVO
    
    **Tema analizado:** {analisis.get('tema', 'N/A')}
    
    **Total de artículos:** {analisis.get('total_articulos', 0)}
    
    **Hallazgo principal:**
    - Medio más objetivo: {matriz.get('medio_mas_objetivo', 'N/A')} (Score: {matriz.get('score_mas_objetivo', 0):.0f}/100)
    - Medio más sesgado: {matriz.get('medio_mas_sesgado', 'N/A')} (Score: {matriz.get('score_mas_sesgado', 0):.0f}/100)
    - Diferencia máxima: {matriz.get('diferencia_maxima_score', 0):.0f} puntos
    
    **Nivel de consenso:** {matriz.get('consensus_nivel', 'N/A')}
    
    **Interpretación de scores:**
    - 0-30: Muy objetivo ✅
    - 30-50: Mayormente objetivo 👍
    - 50-70: Parcialmente sesgado ⚠️
    - 70-100: Muy sesgado 🚩
    """
    
    return resumen
