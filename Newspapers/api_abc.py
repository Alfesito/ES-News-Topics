from Scraper.Base_Scraper import NewsScraperBase
from urllib.parse import urljoin
from .TagEnricher import TagEnricher


class ABCScraper(NewsScraperBase):
    def __init__(self):
        super().__init__('abc.es')
        self.tag_enricher = TagEnricher()
    
    def _scrape_list_articles(self, soup, base_url):
        results = []
        mainwrapper = soup.find('div', class_='voc-wrapper')
        if not mainwrapper:
            return []  # Cambiado de error dict a lista vacía
        
        articles = mainwrapper.find_all('article')[:25]
        for article in articles:
            h2tag = article.find('h2')
            if not h2tag: continue
            atag = h2tag.find('a')
            if not atag: continue
            
            title = self.text.cleantext(atag.get('title') or atag.text)
            if len(title) < 10: continue
            
            link = atag.get('href', '')
            if link.startswith('/'): 
                link = urljoin('https://www.abc.es', link)
            elif not link.startswith('http'):
                continue
            
            authortag = article.find('span', class_='voc-onplus__author')
            listauthor = self.text.cleantext(authortag) if authortag else 'Redacción'
            
            timetag = article.find('time')
            dateraw = timetag.get('datetime') if timetag else None
            datetimestr = self.date.normalizedatetime(dateraw)
            
            details = self.scrape_article_details(link)
            finaltitle = details.get('title', title) or title
            finalauthor = details.get('author', listauthor)
            
            articleid = self.idgen.generate_id_from_url(link) if link else self.idgen.generateshortid('ABC', datetimestr, finaltitle)
            
            orderedarticle = self.article.create_ordered_article(
                'abc.es', articleid, datetimestr, details.get('tags', []),
                finaltitle, details.get('subtitle', ''), link, 
                finalauthor, details.get('image', {'url': '', 'credits': ''}),
                details.get('body', '')
            )
            results.append(orderedarticle)
        return results[:25]
    
    def _scrape_article_details(self, soup):
        # TITLE
        title_elem = soup.find('h1', class_='voc-title')
        title = self.text.cleantext(title_elem) if title_elem else ''
        
        # SUBTITLE
        subtitle_elem = soup.find('h2', class_='voc-subtitle')
        subtitle = self.text.cleantext(subtitle_elem) if subtitle_elem else ''
        
        # AUTHOR
        authorsection = soup.find('section', class_='voc-author')
        author = ''
        if authorsection:
            authorlink = authorsection.select_one('p.voc-author__name a')
            author = self.text.cleantext(authorlink) if authorlink else ''
        
        # TAGS
        tags = []
        #navtopics = soup.find('nav', class_='voc-topics__header')
        navtopics = False
        if navtopics:
            taglinks = navtopics.find_all('a', class_='voc-topics__link')
            for a in taglinks:
                tag_text = a.get('title') or a.get_text(strip=True)
                tag_clean = self.text.cleantext(tag_text)
                if tag_clean and tag_clean.lower() != 'más temas':
                    tags.append(tag_clean)
        
        # BODY
        bodyparagraphs = soup.find_all('p', class_='voc-p')[:12]
        body_parts = []
        for p in bodyparagraphs:
            ptext = self.text.cleantext(p)
            if len(ptext) > 30:
                body_parts.append(ptext)
        body = ' '.join(body_parts)[:3000]
        
        # ENRIQUECER TAGS con el TagEnricher
        enriched_tags = self.tag_enricher.enrich_tags(tags, title, subtitle)
        
        # IMAGE
        image = self.image.extract_image(soup, [
            'figure.voc-img-figure img.voc-img[src]',
            'img.voc-img[src]',
            'meta[property="og:image"]'
        ])

        # Completar credits
        if not image.get('credits'):
            caption_text = ''
            caption_author = ''
            fig = soup.find('figure', class_='voc-img-figure')
            figcap = None
            if fig:
                figcap = fig.find_next_sibling('figcaption') or fig.find('figcaption')
            if not figcap:
                figcap = soup.find('figcaption', class_='voc-figcaption-container')

            if figcap:
                text_span = figcap.find('span', class_='voc-figcaption--text')
                author_span = figcap.find('span', class_='voc-figcaption--author')
                if text_span:
                    caption_text = self.text.cleantext(text_span)
                if author_span:
                    caption_author = self.text.cleantext(author_span)

            if not caption_text:
                img_elem = soup.select_one('figure.voc-img-figure img.voc-img') or soup.select_one('img.voc-img')
                if img_elem:
                    caption_text = (img_elem.get('alt') or '').strip()

            image['credits'] = self.image.format_credits(caption_text, caption_author)

        return {
            'title': title, 
            'subtitle': subtitle, 
            'author': author,
            'tags': enriched_tags,  # ✅ CORREGIDO: usar enriched_tags
            'body': body, 
            'image': image
        }


# Flask 
if __name__ == '__main__':
    try:
        from Flask_App.Flask_App import NewsFlaskApp
    except Exception:
        from Flask_App import NewsFlaskApp
    abc = ABCScraper()
    app = NewsFlaskApp(abc, "ABC", 5002, ["abc.es"])
    app.run()
