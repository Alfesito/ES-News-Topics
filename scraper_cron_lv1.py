from Newspapers.api_eldiario import ElDiarioScraper
from Newspapers.api_elpais import ElPaisScraper
from Newspapers.api_larazon import LaRazonScraper
from Newspapers.api_publico import PublicoScraper
from Newspapers.api_elespanol import ElEspanolScraper
from Newspapers.api_lavozdegalicia import LaVozDeGaliciaScraper


import json
import hashlib
from datetime import datetime, timedelta
import time


SCRAPERS = {
    'El Diario': ElDiarioScraper(),
    'El País': ElPaisScraper(),
    'La Razón': LaRazonScraper(),
    'Público': PublicoScraper(),
    'El Español': ElEspanolScraper(),
    'La Voz De Galicia': LaVozDeGaliciaScraper()
}


URLS = {
    'El Diario': 'https://www.eldiario.es',
    'El País': 'https://elpais.com',
    'La Razón': 'https://www.larazon.es',
    'Público': 'https://www.publico.es',
    'El Español': 'https://www.elespanol.com',
    'La Voz De Galicia': 'https://www.lavozdegalicia.es'
}


def scrape_all():
    """10 periódicos → dedup → histórico 7 días → JSON único"""
    print("🚀 INICIO SCRAPING - 10 PERIÓDICOS")
    all_articles = []
    
    # 🔍 Scraping por periódico
    for domain, scraper in SCRAPERS.items():
        url = URLS.get(domain, f'https://www.{domain}')
        print(f"\n🔍 [{len(all_articles)} total] {domain}: {url}")
        
        try:
            time.sleep(2)  # Anti-ban
            
            results = scraper.scrape_list_page(url)
            
            # Fallback artículo individual
            if not results:
                try:
                    details = scraper.scrape_article_details(url)
                    date_str = getattr(scraper, 'date', type('Date', (), {'normalizedatetime': lambda: ''})()).normalizedatetime()
                    article_id = getattr(scraper, 'idgen', type('IDGen', (), {'generate_id_from_url': lambda x: 'id'})()).generate_id_from_url(url)
                    ordered = getattr(scraper, 'article', type('Article', (), {'create_ordered_article': lambda *a: {}})()).create_ordered_article(
                        scraper.name, article_id, date_str,
                        details.get('tags', []), details.get('title', ''),
                        details.get('subtitle', ''), url,
                        details.get('author', 'Redacción'),
                        details.get('image', {'url': '', 'credits': ''}),
                        details.get('body', '')
                    )
                    results = [ordered]
                except:
                    print(f"   ❌ Fallback falló")
                    continue
            
            # Enriquecer (tu lógica original)
            enriched = []
            for art in results:
                try:
                    enriched.append(scraper.enrich_article(art))
                except:
                    enriched.append(art)
            
            # Metadatos + hash dedup
            for art in enriched:
                content_hash = hashlib.md5(
                    f"{art.get('title', '')}{art.get('url', '')}".encode('utf-8')
                ).hexdigest()
                
                art['hash'] = content_hash
                art['newspaper'] = domain
                art['scraped_at'] = datetime.now().isoformat()
            
            all_articles.extend(enriched)
            print(f"   ✅ +{len(enriched)} → {len(all_articles)} total")
            
        except Exception as e:
            print(f"   ❌ {str(e)[:80]}")
    
    print(f"\n📊 BRUTO: {len(all_articles)} artículos")
    
    # 📂 CARGAR HISTÓRICO ANTERIOR
    try:
        with open('./news_json/noticias_completas.json', 'r', encoding='utf-8') as f:
            old_articles = json.load(f)
        print(f"📂 Histórico: {len(old_articles)} artículos")
    except:
        old_articles = []
    
    # 🔄 DEDUP: nuevos vs histórico
    old_hashes = {art.get('hash') for art in old_articles}
    new_articles = [art for art in all_articles if art['hash'] not in old_hashes]
    print(f"➕ Nuevos únicos: {len(new_articles)}")
    
    all_articles = old_articles + new_articles
    
    # 🧹 LIMPIAR >7 DÍAS
    cutoff_date = datetime.now() - timedelta(days=7)
    recent_articles = []
    deleted = 0
    
    for art in all_articles:
        try:
            art_date = datetime.fromisoformat(art['scraped_at'].replace('Z', '+00:00'))
            if art_date >= cutoff_date:
                recent_articles.append(art)
            else:
                deleted += 1
        except:
            recent_articles.append(art)  # Fecha inválida → mantener
    
    print(f"🗑️ Eliminados: {deleted} (>7 días)")
    
    # 📊 ORDENAR RECIENTES PRIMERO
    recent_articles.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)
    
    # 💾 JSON FINAL (7 días)
    with open('./news_json/noticias_completas.json', 'w', encoding='utf-8') as f:
        json.dump(recent_articles, f, ensure_ascii=False, indent=2)
    
    # 🆕 FILTRAR ÚLTIMAS 24H Y CREAR JSON ADICIONAL
    cutoff_24h = datetime.now() - timedelta(hours=24)
    articles_24h = []
    
    for art in recent_articles:
        try:
            art_date = datetime.fromisoformat(art['scraped_at'].replace('Z', '+00:00'))
            if art_date >= cutoff_24h:
                articles_24h.append(art)
        except:
            pass  # Ignorar artículos sin fecha válida
    
    # 💾 JSON ÚLTIMAS 24H
    with open('./news_json/noticias_24h.json', 'w', encoding='utf-8') as f:
        json.dump(articles_24h, f, ensure_ascii=False, indent=2)
    
    print(f"\n⏰ ÚLTIMAS 24H: {len(articles_24h)} noticias")
    print(f"   📁 noticias_24h.json → {len(articles_24h)*0.8/1000:.1f}KB")
    
    # STATS
    print(f"\n🎉 FINAL: {len(recent_articles)} noticias (7 días)")
    print(f"   📁 noticias_completas.json → {len(recent_articles)*0.8/1000:.1f}KB")
    
    domains = {}
    for art in recent_articles[:100]:
        domains[art.get('domain', '?')] = domains.get(art.get('domain', '?'), 0) + 1
    print(f"   🏆 Top: {dict(sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5])}")
    
    # STATS 24H
    domains_24h = {}
    for art in articles_24h:
        domains_24h[art.get('domain', '?')] = domains_24h.get(art.get('domain', '?'), 0) + 1
    if domains_24h:
        print(f"   🏆 Top 24h: {dict(sorted(domains_24h.items(), key=lambda x: x[1], reverse=True)[:5])}")
    
    return recent_articles


if __name__ == '__main__':
    scrape_all()
