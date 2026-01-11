#!/usr/bin/env python3
"""
Analizador de Relaciones entre Tags de Noticias
Construye un grafo de co-ocurrencias basado en tags que aparecen juntos
"""


import json
import requests
from collections import defaultdict, Counter
import unicodedata



def normalize_tag(tag):
    """
    Normaliza un tag eliminando tildes y convirtiendo a minúsculas.
    """
    text = unicodedata.normalize('NFD', tag)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    return text.lower().strip()



def capitalize_tag(tag):
    """
    Capitaliza correctamente un tag.
    """
    lowercase_words = {'de', 'del', 'la', 'el', 'los', 'las', 'y', 'en', 'un', 'una', 
                       'con', 'por', 'para', 'al', 'a', 'o', 'u', 'e', "-", "vs", "vs."}


    words = tag.split()
    capitalized = []


    for i, word in enumerate(words):
        if i == 0:
            capitalized.append(word.capitalize())
        elif word.isdigit():
            capitalized.append(word)
        elif word.lower() in lowercase_words:
            capitalized.append(word.lower())
        else:
            capitalized.append(word.capitalize())


    return ' '.join(capitalized)



def fetch_news(url):
    """
    Descarga el JSON de noticias desde la URL.
    """
    try:
        print(f"📰 Descargando noticias desde: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        news_data = response.json()
        print(f"✅ {len(news_data)} noticias cargadas")
        return news_data
    except Exception as e:
        print(f"❌ Error descargando noticias: {str(e)}")
        return []



def build_tag_graph(news_articles):
    """
    Construye un grafo de relaciones entre tags.


    Retorna:
    - tag_relations: dict con tags como keys y set de tags relacionados como values
    - tag_stats: dict con estadísticas por tag (frecuencia, co-ocurrencias)
    """
    print("\n🔗 Construyendo grafo de relaciones entre tags...")


    # Diccionario: tag_normalized -> tag_original (con mayúsculas)
    tag_canonical = {}


    # Diccionario: tag -> set de tags relacionados
    tag_relations = defaultdict(set)


    # Contador de frecuencia de cada tag
    tag_frequency = Counter()


    # Contador de co-ocurrencias (pares de tags)
    cooccurrence_count = defaultdict(int)


    processed_articles = 0


    for article in news_articles:
        tags = article.get('tags', [])


        if not isinstance(tags, list) or len(tags) < 2:
            continue


        # Normalizar y filtrar tags vacíos
        normalized_tags = []
        for tag in tags:
            if tag and isinstance(tag, str) and tag.strip():
                norm_tag = normalize_tag(tag)


                # Mantener el tag con mejor capitalización (primera vez o más largo)
                if norm_tag not in tag_canonical or len(tag) > len(tag_canonical[norm_tag]):
                    tag_canonical[norm_tag] = capitalize_tag(tag)


                normalized_tags.append(norm_tag)
                tag_frequency[norm_tag] += 1


        # Eliminar duplicados en esta noticia
        unique_tags = list(set(normalized_tags))


        if len(unique_tags) < 2:
            continue


        # Crear relaciones entre todos los pares de tags en esta noticia
        for i, tag1 in enumerate(unique_tags):
            for tag2 in unique_tags[i+1:]:
                # Añadir relación bidireccional
                tag_relations[tag1].add(tag2)
                tag_relations[tag2].add(tag1)


                # Contar co-ocurrencia (ordenar alfabéticamente para consistencia)
                pair = tuple(sorted([tag1, tag2]))
                cooccurrence_count[pair] += 1


        processed_articles += 1


    print(f"✅ {len(tag_relations)} tags únicos encontrados")
    print(f"📊 {processed_articles} noticias procesadas")
    print(f"🔗 {sum(len(relations) for relations in tag_relations.values()) // 2} relaciones únicas")


    # Construir estadísticas por tag
    tag_stats = {}
    for norm_tag, related_tags in tag_relations.items():
        canonical_tag = tag_canonical[norm_tag]


        # Encontrar las relaciones más fuertes (más co-ocurrencias)
        related_with_strength = []
        for related_tag in related_tags:
            pair = tuple(sorted([norm_tag, related_tag]))
            strength = cooccurrence_count[pair]
            related_with_strength.append({
                'tag': tag_canonical[related_tag],
                'cooccurrence_count': strength
            })


        # Ordenar por fuerza de relación
        related_with_strength.sort(key=lambda x: x['cooccurrence_count'], reverse=True)


        tag_stats[canonical_tag] = {
            'frequency': tag_frequency[norm_tag],
            'related_count': len(related_tags),
            'related_tags': [r['tag'] for r in related_with_strength]
        }


    return tag_relations, tag_stats, tag_canonical



def find_tag_clusters(tag_relations, tag_canonical, min_cluster_size=3):
    """
    Encuentra clusters de tags altamente relacionados usando componentes conectados.
    """
    print("\n🎯 Identificando clusters de tags relacionados...")


    visited = set()
    clusters = []


    def dfs(tag, cluster):
        """Búsqueda en profundidad para encontrar componente conectado."""
        visited.add(tag)
        cluster.add(tag)


        for related_tag in tag_relations.get(tag, set()):
            if related_tag not in visited:
                dfs(related_tag, cluster)


    # Encontrar todos los componentes conectados
    for tag in tag_relations.keys():
        if tag not in visited:
            cluster = set()
            dfs(tag, cluster)
            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)


    # Convertir a formato legible con tags capitalizados
    clusters_formatted = []
    for cluster in sorted(clusters, key=len, reverse=True):
        cluster_tags = sorted([tag_canonical[tag] for tag in cluster])
        clusters_formatted.append({
            'size': len(cluster_tags),
            'tags': cluster_tags
        })


    print(f"✅ {len(clusters_formatted)} clusters identificados")
    return clusters_formatted



def analyze_tag_network(news_url):
    """
    Función principal que analiza la red de tags.
    """
    # Descargar noticias
    news_articles = fetch_news(news_url)


    if not news_articles:
        print("❌ No se pudieron cargar las noticias")
        return


    # Construir grafo de relaciones
    tag_relations, tag_stats, tag_canonical = build_tag_graph(news_articles)


    # Encontrar clusters
    clusters = find_tag_clusters(tag_relations, tag_canonical)


    # Preparar resultado (SIN transitive_relations)
    result = {
        'metadata': {
            'total_tags': len(tag_relations),
            'total_articles': len(news_articles),
            'total_relations': sum(len(relations) for relations in tag_relations.values()) // 2,
            'total_clusters': len(clusters)
        },
        'tag_stats': tag_stats,
        'clusters': clusters,
        'direct_relations': {
            tag_canonical[tag]: sorted([tag_canonical[r] for r in relations])
            for tag, relations in sorted(tag_relations.items(), key=lambda x: len(x[1]), reverse=True)
        }
    }


    # Guardar resultados
    with open('./tags_json/tag_relations.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


    print("\n✅ Resultados guardados en: tag_relations.json")
    print(f"📊 Estructura del JSON:")
    print(f"   - metadata: información general")
    print(f"   - tag_stats: estadísticas de {len(tag_stats)} tags")
    print(f"   - clusters: {len(clusters)} grupos identificados")
    print(f"   - direct_relations: relaciones directas entre tags")


    return result



def query_tag_relations(tag_name, relation_file='tag_relations.json'):
    """
    Consulta las relaciones de un tag específico.
    """
    try:
        with open(relation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)


        # Buscar el tag (normalizado)
        tag_normalized = normalize_tag(tag_name)


        # Buscar coincidencia
        matched_tag = None
        for tag in data['tag_stats'].keys():
            if normalize_tag(tag) == tag_normalized:
                matched_tag = tag
                break


        if not matched_tag:
            print(f"❌ Tag '{tag_name}' no encontrado")
            return


        stats = data['tag_stats'][matched_tag]


        print(f"\n📌 Tag: {matched_tag}")
        print(f"🔢 Frecuencia: {stats['frequency']} apariciones")
        print(f"🔗 Relaciones directas: {stats['related_count']}")
        print(f"\n🔝 Top 10 tags más relacionados:")
        for i, related_tag in enumerate(stats['related_tags'][:10], 1):
            print(f"   {i}. {related_tag}")
        
        # Buscar cluster al que pertenece
        for cluster in data['clusters']:
            if matched_tag in cluster['tags']:
                print(f"\n🎯 Pertenece a un cluster de {cluster['size']} tags:")
                print(f"   {', '.join(cluster['tags'][:15])}")
                if len(cluster['tags']) > 15:
                    print(f"   ... y {len(cluster['tags']) - 15} más")
                break


    except FileNotFoundError:
        print(f"❌ Archivo '{relation_file}' no encontrado. Ejecuta primero el análisis.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")



if __name__ == "__main__":
    import sys

    # URL del JSON de noticias
    NEWS_URL = "https://raw.githubusercontent.com/Alfesito/ES-News-Topics/refs/heads/main/news_json/noticias_24h.json"

    # Si se pasa un argumento, consultar ese tag
    if len(sys.argv) > 1:
        tag_name = ' '.join(sys.argv[1:])
        query_tag_relations(tag_name, './tags_json/tag_relations.json')
    else:
        # Modo análisis completo
        print("🚀 ANALIZADOR DE RELACIONES ENTRE TAGS")
        analyze_tag_network(NEWS_URL)
        print("\n💡 Usa: python script.py \"nombre_tag\" para consultar relaciones de un tag específico")
