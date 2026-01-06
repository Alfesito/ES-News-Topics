#!/usr/bin/env python3
"""
Google Trends + X Trends + Tags de Noticias España
IDs: 1-99=Google (24h/4h) | 100+=X Trends | 200+=Tags Noticias
Campos: id, title, source, volume, timeframe, news_count
"""

import json
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright
import re
import requests
from difflib import SequenceMatcher
from collections import Counter
import unicodedata


def similar(a, b):
    """Calcula similitud entre dos strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def fetch_news_24h(url):
    """Descarga y parsea el JSON de noticias 24h"""
    try:
        print(f"📰 Descargando noticias desde: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        news_data = response.json()
        print(f"✅ {len(news_data)} noticias cargadas")
        return news_data
    except Exception as e:
        print(f"❌ Error descargando noticias: {str(e)}")
        return []


def normalize_for_comparison(text):
    """
    Normaliza texto para comparación eliminando tildes y diacríticos.
    'Nicolás' -> 'nicolas' (para comparación)
    """
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    return text.lower()


def normalize_title(title):
    """
    Normaliza título eliminando tildes y convirtiendo a minúsculas para comparación.
    """
    text = unicodedata.normalize('NFD', title)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    return text.lower().strip()


def capitalize_title(title):
    """
    Capitaliza correctamente un título:
    - Primera letra de cada palabra en mayúscula
    - Excepto preposiciones/artículos (a menos que sean primera palabra)
    """
    lowercase_words = {'de', 'del', 'la', 'el', 'los', 'las', 'y', 'en', 'un', 'una', 
                       'con', 'por', 'para', 'al', 'a', 'o', 'u', 'e'}

    words = title.split()
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


def extract_keywords(title):
    """
    Extrae palabras clave significativas de un título.
    """
    stopwords = {'el', 'la', 'los', 'las', 'de', 'del', 'y', 'en', 'un', 'una', 
                 'es', 'por', 'con', 'para', 'al', 'a', 'o', 'que', 'se', 'su'}

    normalized = normalize_title(title)
    words = re.findall(r'\b\w+\b', normalized)
    keywords = {w for w in words if w not in stopwords and len(w) > 2}

    return keywords


def should_merge_trends(trend1, trend2, threshold=0.75):
    """
    Determina si dos trends deben fusionarse basándose en múltiples criterios.

    Criterios de fusión:
    1. Similitud de texto > threshold (75%)
    2. Uno contiene al otro (normalizado)
    3. Comparten >= 70% de palabras clave significativas
    """
    title1 = trend1['title']
    title2 = trend2['title']

    norm1 = normalize_title(title1)
    norm2 = normalize_title(title2)

    # Criterio 1: Similitud alta
    similarity = similar(norm1, norm2)
    if similarity >= threshold:
        return True, similarity

    # Criterio 2: Contención (uno contiene al otro)
    if norm1 in norm2 or norm2 in norm1:
        shorter = min(len(norm1), len(norm2))
        longer = max(len(norm1), len(norm2))
        containment_ratio = shorter / longer if longer > 0 else 0

        if containment_ratio >= 0.6:
            return True, containment_ratio

    # Criterio 3: Palabras clave compartidas
    keywords1 = extract_keywords(title1)
    keywords2 = extract_keywords(title2)

    if keywords1 and keywords2:
        shared = keywords1 & keywords2
        total = keywords1 | keywords2
        jaccard = len(shared) / len(total) if total else 0

        if jaccard >= 0.7:
            return True, jaccard

    return False, 0.0


def unify_related_trends(trends):
    """
    Unifica trends relacionados manteniendo el más relevante.

    Reglas de selección:
    - Mantener el trend con menor ID (más prioritario)
    - Sumar news_count de todos los trends fusionados
    - Combinar sources si son diferentes
    - Preferir título más corto y descriptivo
    """
    print("\n🔗 Unificando trends relacionados...")

    unified_groups = []
    processed = set()

    for i, trend1 in enumerate(trends):
        if i in processed:
            continue

        group = {
            'trends': [trend1],
            'indices': [i]
        }

        for j, trend2 in enumerate(trends[i+1:], start=i+1):
            if j in processed:
                continue

            should_merge, score = should_merge_trends(trend1, trend2)

            if should_merge:
                group['trends'].append(trend2)
                group['indices'].append(j)
                processed.add(j)
                print(f"  🔗 Fusionando: '{trend1['title'][:30]}' + '{trend2['title'][:30]}' (score: {score:.2f})")

        unified_groups.append(group)
        processed.add(i)

    unified_trends = []

    for group in unified_groups:
        group_trends = group['trends']

        if len(group_trends) == 1:
            trend = group_trends[0].copy()
            trend['title'] = capitalize_title(trend['title'])
            unified_trends.append(trend)
        else:
            main_trend = min(group_trends, key=lambda t: t['id'])
            total_news = sum(t.get('news_count', 0) for t in group_trends)
            sources = list(set(t['source'] for t in group_trends))

            best_title = max(group_trends, 
                           key=lambda t: (len(extract_keywords(t['title'])), -len(t['title'])))['title']

            unified_trend = main_trend.copy()
            unified_trend['title'] = capitalize_title(best_title)
            unified_trend['news_count'] = total_news

            if len(sources) > 1:
                unified_trend['merged_sources'] = sources

            unified_trends.append(unified_trend)

    print(f"✅ {len(trends)} trends → {len(unified_trends)} después de unificación")
    print(f"📊 Fusionados: {len(trends) - len(unified_trends)} grupos")

    return unified_trends


def unify_tags(tag_counter):
    """
    Unifica tags donde uno contiene a otro, considerando tildes.
    Ejemplos: 
    - 'Nicolas Maduro' y 'Nicolás Maduro' -> mantiene 'Nicolás Maduro' (con tilde)
    - 'Trump' y 'Donald Trump' -> mantiene 'Trump'
    - 'Venezuela' y 'Venezue' -> mantiene 'Venezuela' (el más completo)
    """
    print("\n🔗 Unificando tags similares...")

    tags_sorted = sorted(tag_counter.items(), key=lambda x: len(x[0]))

    unified = {}
    merged_count = 0

    for tag, count in tags_sorted:
        tag_normalized = normalize_for_comparison(tag)

        found_parent = None
        for unified_tag in list(unified.keys()):
            unified_normalized = normalize_for_comparison(unified_tag)

            if tag_normalized == unified_normalized:
                if tag != tag.encode('ascii', 'ignore').decode('ascii'):
                    unified[tag] = unified.pop(unified_tag) + count
                    found_parent = tag
                else:
                    unified[unified_tag] += count
                    found_parent = unified_tag
                merged_count += 1
                break

            if tag_normalized in unified_normalized or unified_normalized in tag_normalized:
                if unified_normalized.startswith(tag_normalized):
                    unified[unified_tag] += count
                    found_parent = unified_tag
                elif tag_normalized.startswith(unified_normalized):
                    unified[tag] = unified.pop(unified_tag) + count
                    found_parent = tag
                else:
                    if len(tag_normalized) < len(unified_normalized):
                        unified[tag] = unified.pop(unified_tag) + count
                        found_parent = tag
                    else:
                        unified[unified_tag] += count
                        found_parent = unified_tag
                merged_count += 1
                break

        if not found_parent:
            unified[tag] = count

    print(f"✅ {len(tag_counter)} tags → {len(unified)} unificados ({merged_count} fusionados)")
    return unified


def extract_tags_as_trends(news_articles, base_id=200):
    """
    Extrae tags de las noticias y los convierte en trends.
    Cuenta cuántas noticias tiene cada tag y unifica tags similares.
    """
    print("\n🏷️ Extrayendo tags de noticias como trends...")

    tag_counter = Counter()

    for article in news_articles:
        tags = article.get('tags', [])
        if isinstance(tags, list):
            for tag in tags:
                if tag and isinstance(tag, str) and tag.strip():
                    normalized_tag = tag.strip().lower()
                    tag_counter[normalized_tag] += 1

    unified_tags = unify_tags(tag_counter)

    tag_trends = []
    for idx, (tag, count) in enumerate(sorted(unified_tags.items(), key=lambda x: x[1], reverse=True)[:50]):
        trend = {
            'id': base_id + idx,
            'title': tag.title(),
            'source': 'news_tags',
            'volume': f'{count} artículos',
            'timeframe': '24h noticias',
            'news_count': count
        }
        tag_trends.append(trend)

    print(f"✅ {len(tag_trends)} tags extraídos como trends")
    return tag_trends


def count_news_by_trend(trends, news_articles):
    """
    Cuenta cuántas noticias tratan sobre cada trend.
    Usa coincidencia fuzzy para detectar trends en títulos/subtítulos/tags.
    """
    print("\n🔍 Analizando coincidencias trends-noticias...")

    for trend in trends:
        if trend.get('source') == 'news_tags':
            continue

        trend_title = trend['title'].lower()
        trend_keywords = set(re.findall(r'\w+', trend_title))
        stopwords = {'el', 'la', 'los', 'las', 'de', 'del', 'y', 'en', 'un', 'una', 'es', 'por', 'con', 'para', 'al'}
        trend_keywords = trend_keywords - stopwords

        count = 0

        for article in news_articles:
            title = article.get('title', '').lower()
            subtitle = article.get('subtitle', '').lower()
            tags = [t.lower() for t in article.get('tags', []) if isinstance(t, str)]
            combined_text = f"{title} {subtitle} {' '.join(tags)}"

            if similar(trend_title, title) > 0.7:
                count += 1
                continue

            if trend_title in tags:
                count += 1
                continue

            if trend_keywords:
                matched_keywords = sum(1 for kw in trend_keywords if kw in combined_text)
                if matched_keywords >= len(trend_keywords) * 0.6:
                    count += 1

        trend['news_count'] = count
        if count > 0:
            print(f"  🔗 '{trend['title'][:40]}': {count} noticias")

    return trends


def merge_and_deduplicate_trends(all_trends):
    """
    Fusiona trends duplicados, manteniendo el de menor ID y sumando news_count.
    """
    print("\n🔄 Eliminando duplicados y fusionando trends...")

    merged = {}

    for trend in all_trends:
        title_key = re.sub(r'[^\w\s]', '', trend['title'].lower()).strip()

        if title_key in merged:
            existing = merged[title_key]
            if trend['id'] < existing['id']:
                trend['news_count'] = existing.get('news_count', 0) + trend.get('news_count', 0)
                merged[title_key] = trend
            else:
                existing['news_count'] = existing.get('news_count', 0) + trend.get('news_count', 0)
        else:
            merged[title_key] = trend

    unique_trends = list(merged.values())
    print(f"✅ {len(all_trends)} trends → {len(unique_trends)} únicos")
    return unique_trends


def get_sort_priority(trend):
    """
    Asigna prioridad de ordenación basada en los criterios especificados.
    Retorna tupla: (prioridad, -news_count, id)
    """
    news_count = trend.get('news_count', 0)
    source = trend.get('source', '')
    volume = trend.get('volume', '').lower()

    has_mm = 'mm' in volume or bool(re.search(r'\d+[.,]?\d*\s*m\b', volume))
    has_k = 'mil+' in volume or 'k' in volume

    if news_count >= 75:
        return (1, -news_count, trend['id'])
    elif source == 'x_trends' and has_mm:
        return (2, -news_count, trend['id'])
    elif 30 <= news_count < 75:
        return (3, -news_count, trend['id'])
    elif source == 'google' and has_k:
        return (4, -news_count, trend['id'])
    elif source == 'google' and not has_mm and not has_k:
        return (5, -news_count, trend['id'])
    else:
        return (6, -news_count, trend['id'])


def sort_trends_custom(trends):
    """Ordena trends según los criterios personalizados."""
    return sorted(trends, key=get_sort_priority)


async def scrape_trends(hours):
    """Scrapea Google Trends"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()

        url = f"https://trends.google.com/trending?geo=ES&hl=es&sort=search-volume&hours={hours}"
        await page.goto(url, wait_until='networkidle', timeout=45000)

        await page.wait_for_selector('table.enOdEe-wZVHld-zg7Cn', timeout=30000)
        await page.wait_for_selector('tr[data-row-id]', timeout=20000)

        rows = await page.query_selector_all('tr[data-row-id]')
        trends = []

        base_id = 1 if hours == '24' else 20

        for i, row in enumerate(rows[:15]):
            try:
                title_elem = await row.query_selector('div.mZ3RIc')
                title = await title_elem.inner_text() if title_elem else ''

                if not title.strip():
                    continue

                volume_elem = await row.query_selector('div.lqv0Cb, div.qNpYPd')
                volume = await volume_elem.inner_text() if volume_elem else '0'

                time_elem = await row.query_selector('div.A7jE4')
                time = await time_elem.inner_text() if time_elem else ''

                trend = {
                    'id': base_id + i,
                    'title': title.strip(),
                    'source': 'google',
                    'volume': volume.strip(),
                    'timeframe': f"{time.strip()} ({hours}h)",
                    'news_count': 0
                }
                trends.append(trend)
            except:
                continue

        await browser.close()
        print(f"Google {hours}h: {len(trends)} trends")
        return trends


async def scrape_xtrends():
    """Scrapea X Trends desde múltiples fuentes (fallback)"""
    sources = [
        ("https://trends24.in/spain/", 'h2', 'section.stat-card', scrape_trends24),
        ("https://getdaytrends.com/spain/", '[data-testid="trend"]', None, scrape_getdaytrends),
    ]

    xtrends = []
    base_id = 100

    for idx, (url, selector1, selector2, scraper) in enumerate(sources):
        try:
            print(f"🔄 Probando X Trends fuente {idx+1}: {url}")
            trends = await scraper(url, selector1, selector2, base_id + (idx * 50))
            if trends:
                print(f"✅ X Trends fuente {idx+1}: {len(trends)} trends")
                xtrends.extend(trends[:20])
                break
        except Exception as e:
            print(f"❌ X Trends fuente {idx+1} falló: {str(e)[:100]}")
            continue

    if not xtrends:
        print("⚠️ Todas las fuentes X Trends fallaron - usando fallback")
        xtrends = []

    print(f"X Trends total: {len(xtrends)}")
    return xtrends


async def scrape_trends24(url, selector1, selector2, base_id):
    """Scraping específico para trends24.in"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        await page.goto(url, wait_until='domcontentloaded', timeout=45000)
        await page.wait_for_selector(selector1, timeout=30000)

        trends = []
        sections = await page.query_selector_all(selector2)

        for sec_idx, section in enumerate(sections[:3]):
            try:
                list_elem = await section.query_selector('ol.stat-card-list')
                if not list_elem:
                    continue

                items = await list_elem.query_selector_all('li.stat-card-item')

                for i, item in enumerate(items[:10]):
                    try:
                        link_elem = await item.query_selector('a.trend-link')
                        title = await link_elem.inner_text() if link_elem else ''

                        if not title.strip():
                            continue

                        item_text = await item.inner_text()
                        volume = 'N/A'

                        match = re.search(r'with ([\d.]+[KMB]?) tweet', item_text, re.IGNORECASE)
                        if match:
                            volume = match.group(1) + 'M tweets'

                        timeframe = '24h trends'
                        if 'longest' in item_text.lower():
                            match_time = re.search(r'for (\d+) hrs?', item_text)
                            if match_time:
                                timeframe = f"{match_time.group(1)}h trending"

                        trend = {
                            'id': base_id + (sec_idx * 10) + i + 1,
                            'title': title.strip(),
                            'source': 'x_trends',
                            'volume': volume,
                            'timeframe': timeframe,
                            'news_count': 0
                        }
                        trends.append(trend)
                    except:
                        continue
            except:
                continue

        await browser.close()
        return trends


async def scrape_getdaytrends(url, selector1, selector2, base_id):
    """Scraping específico para getdaytrends.com"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        await page.goto(url, wait_until='domcontentloaded', timeout=45000)
        await page.wait_for_selector(selector1, timeout=30000)

        trends = []
        items = await page.query_selector_all(selector1)

        for i, item in enumerate(items[:25]):
            try:
                title_elem = await item.query_selector('div[data-testid="trend-name"]')
                title = await title_elem.inner_text() if title_elem else ''

                if not title.strip():
                    continue

                volume_elem = await item.query_selector('[data-testid="tweets"]')
                volume = await volume_elem.inner_text() if volume_elem else 'N/A'

                trend = {
                    'id': base_id + i,
                    'title': title.strip(),
                    'source': 'x_trends',
                    'volume': volume,
                    'timeframe': '24h trends',
                    'news_count': 0
                }
                trends.append(trend)
            except:
                continue

        await browser.close()
        return trends


async def main():
    print("🚀 GOOGLE TRENDS + X TRENDS + TAGS NOTICIAS ESPAÑA")

    print("🔄 Scraping Google Trends 24h...")
    google_24h = await scrape_trends('24')

    print("🔄 Scraping Google Trends 4h...")
    google_4h = await scrape_trends('4')

    print("🔄 Scraping X Trends...")
    xtrends = await scrape_xtrends()

    news_url = "https://raw.githubusercontent.com/Alfesito/ES-News-Topics/refs/heads/main/noticias_24h.json"
    news_articles = fetch_news_24h(news_url)

    tag_trends = []
    if news_articles:
        tag_trends = extract_tags_as_trends(news_articles)

    all_trends = google_24h + google_4h + xtrends + tag_trends

    unique_trends = merge_and_deduplicate_trends(all_trends)

    if news_articles:
        unique_trends = count_news_by_trend(unique_trends, news_articles)

    unified_trends = unify_related_trends(unique_trends)

    sorted_trends = sort_trends_custom(unified_trends)

    result = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'google_total': len(google_24h) + len(google_4h),
            'xtrends_total': len(xtrends),
            'tags_total': len(tag_trends),
            'unique_total': len(sorted_trends),
            'unified_count': len(unique_trends) - len(unified_trends),
            'with_news': sum(1 for t in sorted_trends if t.get('news_count', 0) > 0),
            'without_news': sum(1 for t in sorted_trends if t.get('news_count', 0) == 0)
        },
        'trends': sorted_trends
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

    with open('trends_google&x.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("\n✅ Guardado: trends_google&x.json")
    print(f"📊 Total: {len(sorted_trends)} trends")
    print(f"🔗 Trends unificados: {len(unique_trends) - len(unified_trends)}")
    print(f"🔝 Con noticias: {sum(1 for t in sorted_trends if t.get('news_count', 0) > 0)}")
    print(f"🏷️ Tags extraídos: {len(tag_trends)}")


if __name__ == "__main__":
    asyncio.run(main())
    