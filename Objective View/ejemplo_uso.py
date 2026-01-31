#!/usr/bin/env python3
"""
Ejemplo de uso del módulo advanced_analysis.py
Demuestra cómo analizar artículos con el sistema avanzado de detección de sesgos
"""

from advanced_analysis import (
    analizar_lenguaje_sesgado,
    analizar_atribucion_fuentes,
    analizar_enfasis_colocacion,
    analizar_equilibrio_perspectivas,
    calcular_score_sesgo_total,
    generar_reporte_sesgo_detallado
)

# Ejemplo 1: Artículo muy objetivo
articulo_objetivo = {
    'id': '1',
    'source': 'El País',
    'title': 'La inflación cae a 3,2% en enero según datos del INE',
    'subtitle': 'Los precios moderan su subida tras seis meses de desaceleración',
    'body': '''
    Los precios al consumidor bajaron un 0,2% en enero respecto a diciembre, 
    mientras que la inflación interanual se sitúa en 3,2%, según datos publicados 
    hoy por el Instituto Nacional de Estadística (INE).
    
    "Esta cifra representa una desaceleración respecto a los meses anteriores", 
    señaló María García, directora del departamento de análisis macroeconómico del INE.
    
    Por otra parte, algunos economistas advierten que es necesario mantener la vigilancia 
    sobre la evolución de los costes energéticos. "Aunque la tendencia es positiva, 
    los precios de la energía siguen siendo un factor de riesgo", afirmó Juan López, 
    economista senior del banco de inversiones XYZ.
    
    En contraste, otras voces del sector señalan que la moderación de la inflación 
    refleja las medidas adoptadas por el Banco Central Europeo en los últimos meses.
    '''
}

# Ejemplo 2: Artículo muy sesgado
articulo_sesgado = {
    'id': '2',
    'source': 'Medio X',
    'title': 'Catastrófico fracaso: la inflación sigue destroyendo el poder adquisitivo',
    'subtitle': 'El gobierno claramente abandona a los ciudadanos en esta tragedia económica',
    'body': '''
    Mientras los ciudadanos sufren la devastadora crisis económica, el gobierno 
    parece completamente indiferente ante la catástrofe que viven las familias españolas.
    
    La llamada "moderación" de la inflación es sólo una farsa, según expertos independientes. 
    "Es absolutamente obvio que están manipulando los datos", denunció un supuesto 
    analista económico que prefirió mantener el anonimato.
    
    La realidad es que el poder adquisitivo ha colapsado de forma horrorosa. 
    Los ciudadanos, víctimas de esta terrible política económica, no tienen otra 
    opción que resignarse a vivir en la miseria.
    '''
}


def ejemplo_analisis_lenguaje():
    """Demuestra el análisis de lenguaje sesgado"""
    print("\n" + "="*60)
    print("EJEMPLO 1: ANÁLISIS DE LENGUAJE SESGADO")
    print("="*60)
    
    print("\n🔵 ARTÍCULO OBJETIVO:")
    print("-" * 60)
    analisis_obj = analizar_lenguaje_sesgado(articulo_objetivo['body'])
    print(f"Emotividad: {analisis_obj['emotividad']:.1f}/100")
    print(f"Score de Neutralidad: {analisis_obj['score_neutralidad']:.1f}/100")
    print(f"Palabras positivas: {len(analisis_obj['palabras_emotivas_positivas'])}")
    print(f"Palabras negativas: {len(analisis_obj['palabras_emotivas_negativas'])}")
    print(f"Intensificadores: {len(analisis_obj['intensificadores'])}")
    print(f"Patrones de sesgo: {len(analisis_obj['patrones_sesgo_detectados'])}")
    
    print("\n🔴 ARTÍCULO SESGADO:")
    print("-" * 60)
    analisis_sesg = analizar_lenguaje_sesgado(articulo_sesgado['body'])
    print(f"Emotividad: {analisis_sesg['emotividad']:.1f}/100")
    print(f"Score de Neutralidad: {analisis_sesg['score_neutralidad']:.1f}/100")
    print(f"Palabras positivas: {len(analisis_sesg['palabras_emotivas_positivas'])}")
    print(f"Palabras negativas: {len(analisis_sesg['palabras_emotivas_negativas'])}")
    print(f"Palabras negativas encontradas: {analisis_sesg['palabras_emotivas_negativas'][:5]}")
    print(f"Intensificadores: {len(analisis_sesg['intensificadores'])}")
    print(f"Intensificadores encontrados: {analisis_sesg['intensificadores'][:5]}")
    print(f"Patrones de sesgo: {len(analisis_sesg['patrones_sesgo_detectados'])}")


def ejemplo_analisis_fuentes():
    """Demuestra el análisis de atribución de fuentes"""
    print("\n" + "="*60)
    print("EJEMPLO 2: ANÁLISIS DE ATRIBUCIÓN DE FUENTES")
    print("="*60)
    
    print("\n🔵 ARTÍCULO OBJETIVO:")
    print("-" * 60)
    fuentes_obj = analizar_atribucion_fuentes(articulo_objetivo['body'])
    print(f"Citas directas: {fuentes_obj['numero_citas_directas']}")
    print(f"Citas indirectas: {fuentes_obj['numero_citas_indirectas']}")
    print(f"Calidad de fuentes: {fuentes_obj['calidad_fuentes']}")
    print(f"Score de atribución: {fuentes_obj['score_atribucion']:.1f}/100")
    print(f"Tipos de fuentes: {', '.join(fuentes_obj['tipos_fuentes'])}")
    
    print("\n🔴 ARTÍCULO SESGADO:")
    print("-" * 60)
    fuentes_sesg = analizar_atribucion_fuentes(articulo_sesgado['body'])
    print(f"Citas directas: {fuentes_sesg['numero_citas_directas']}")
    print(f"Citas indirectas: {fuentes_sesg['numero_citas_indirectas']}")
    print(f"Calidad de fuentes: {fuentes_sesg['calidad_fuentes']}")
    print(f"Score de atribución: {fuentes_sesg['score_atribucion']:.1f}/100")
    print(f"Tipos de fuentes: {', '.join(fuentes_sesg['tipos_fuentes'])}")


def ejemplo_analisis_perspectivas():
    """Demuestra el análisis de balance de perspectivas"""
    print("\n" + "="*60)
    print("EJEMPLO 3: ANÁLISIS DE BALANCE DE PERSPECTIVAS")
    print("="*60)
    
    print("\n🔵 ARTÍCULO OBJETIVO:")
    print("-" * 60)
    persp_obj = analizar_equilibrio_perspectivas(articulo_objetivo['body'])
    print(f"Balance: {persp_obj['balance']}")
    print(f"Score de balance: {persp_obj['score_balance']:.1f}/100")
    print(f"Menciona contrapuntos: {persp_obj['menciona_contrapuntos']}")
    print(f"Menciona críticas: {persp_obj['menciona_criticas']}")
    print(f"Menciona posiciones opuestas: {persp_obj['menciona_posiciones_opuestas']}")
    
    print("\n🔴 ARTÍCULO SESGADO:")
    print("-" * 60)
    persp_sesg = analizar_equilibrio_perspectivas(articulo_sesgado['body'])
    print(f"Balance: {persp_sesg['balance']}")
    print(f"Score de balance: {persp_sesg['score_balance']:.1f}/100")
    print(f"Menciona contrapuntos: {persp_sesg['menciona_contrapuntos']}")
    print(f"Menciona críticas: {persp_sesg['menciona_criticas']}")
    print(f"Menciona posiciones opuestas: {persp_sesg['menciona_posiciones_opuestas']}")


def ejemplo_score_total():
    """Demuestra el cálculo del score de sesgo total"""
    print("\n" + "="*60)
    print("EJEMPLO 4: SCORE TOTAL DE SESGO")
    print("="*60)
    
    print("\n🔵 ARTÍCULO OBJETIVO:")
    print("-" * 60)
    score_obj = calcular_score_sesgo_total(
        articulo_objetivo['body'],
        articulo_objetivo['title'],
        articulo_objetivo['subtitle'],
        articulo_objetivo['body'][:500]
    )
    print(f"Score de sesgo total: {score_obj['score_sesgo_total']:.1f}/100")
    print(f"Interpretación: {'Muy objetivo ✅' if score_obj['score_sesgo_total'] < 30 else 'Mayormente objetivo 👍' if score_obj['score_sesgo_total'] < 50 else 'Parcialmente sesgado ⚠️' if score_obj['score_sesgo_total'] < 70 else 'Muy sesgado 🚩'}")
    print(f"  - Neutralidad: {score_obj['score_neutralidad']:.0f}/100")
    print(f"  - Atribución: {score_obj['score_atribucion']:.0f}/100")
    print(f"  - Balance: {score_obj['score_balance']:.0f}/100")
    print(f"  - Énfasis: {score_obj['score_enfasis']:.0f}/100")
    
    print("\n🔴 ARTÍCULO SESGADO:")
    print("-" * 60)
    score_sesg = calcular_score_sesgo_total(
        articulo_sesgado['body'],
        articulo_sesgado['title'],
        articulo_sesgado['subtitle'],
        articulo_sesgado['body'][:500]
    )
    print(f"Score de sesgo total: {score_sesg['score_sesgo_total']:.1f}/100")
    print(f"Interpretación: {'Muy objetivo ✅' if score_sesg['score_sesgo_total'] < 30 else 'Mayormente objetivo 👍' if score_sesg['score_sesgo_total'] < 50 else 'Parcialmente sesgado ⚠️' if score_sesg['score_sesgo_total'] < 70 else 'Muy sesgado 🚩'}")
    print(f"  - Neutralidad: {score_sesg['score_neutralidad']:.0f}/100")
    print(f"  - Atribución: {score_sesg['score_atribucion']:.0f}/100")
    print(f"  - Balance: {score_sesg['score_balance']:.0f}/100")
    print(f"  - Énfasis: {score_sesg['score_enfasis']:.0f}/100")


def ejemplo_reporte_completo():
    """Demuestra el reporte completo por artículo"""
    print("\n" + "="*60)
    print("EJEMPLO 5: REPORTE COMPLETO POR ARTÍCULO")
    print("="*60)
    
    print("\n🔵 ARTÍCULO OBJETIVO:")
    print("-" * 60)
    reporte_obj = generar_reporte_sesgo_detallado(articulo_objetivo)
    print(f"Score de sesgo: {reporte_obj['score_sesgo']:.1f}/100")
    print(f"Indicadores clave: {len(reporte_obj['indicadores_clave'])} detectados")
    if reporte_obj['indicadores_clave']:
        for ind in reporte_obj['indicadores_clave']:
            print(f"  - {ind}")
    
    print("\n🔴 ARTÍCULO SESGADO:")
    print("-" * 60)
    reporte_sesg = generar_reporte_sesgo_detallado(articulo_sesgado)
    print(f"Score de sesgo: {reporte_sesg['score_sesgo']:.1f}/100")
    print(f"Indicadores clave: {len(reporte_sesg['indicadores_clave'])} detectados")
    if reporte_sesg['indicadores_clave']:
        for ind in reporte_sesg['indicadores_clave']:
            print(f"  - {ind}")


def comparativa_final():
    """Muestra una comparativa final entre ambos artículos"""
    print("\n" + "="*60)
    print("COMPARATIVA FINAL")
    print("="*60)
    
    reporte_obj = generar_reporte_sesgo_detallado(articulo_objetivo)
    reporte_sesg = generar_reporte_sesgo_detallado(articulo_sesgado)
    
    print("\n" + "MÉTRICA".ljust(30) + "OBJETIVO".ljust(15) + "SESGADO".ljust(15))
    print("-" * 60)
    
    print("Score de sesgo".ljust(30) + f"{reporte_obj['score_sesgo']:.1f}/100".ljust(15) + f"{reporte_sesg['score_sesgo']:.1f}/100")
    print("Diferencia".ljust(30) + f"{abs(reporte_obj['score_sesgo'] - reporte_sesg['score_sesgo']):.1f} puntos")
    print("Ratio de sesgo".ljust(30) + f"1x".ljust(15) + f"{reporte_sesg['score_sesgo']/max(reporte_obj['score_sesgo'], 1):.1f}x")
    print("Indicadores de sesgo".ljust(30) + f"{len(reporte_obj['indicadores_clave'])}".ljust(15) + f"{len(reporte_sesg['indicadores_clave'])}")


if __name__ == "__main__":
    print("\n" + "🔍 DEMOSTRACIÓN DEL ANÁLISIS AVANZADO DE SESGOS ".center(60, "="))
    print("Comparando artículos objetivo vs sesgado sobre inflación")
    
    ejemplo_analisis_lenguaje()
    ejemplo_analisis_fuentes()
    ejemplo_analisis_perspectivas()
    ejemplo_score_total()
    ejemplo_reporte_completo()
    comparativa_final()
    
    print("\n" + "="*60)
    print("✅ Demostración completada exitosamente")
    print("="*60 + "\n")
