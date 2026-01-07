import json
import requests
from typing import List, Dict, Set


class TagEnricher:
    """
    Clase para enriquecer tags de noticias basándose en relaciones
    definidas en el archivo tag_relations.json
    """
    
    def __init__(self, json_url: str = None):
        """
        Inicializa el enriquecedor de tags.
        
        Args:
            json_url: URL del JSON con las relaciones de tags.
                     Por defecto usa el repositorio ES-News-Topics.
        """
        if json_url is None:
            json_url = "https://raw.githubusercontent.com/Alfesito/ES-News-Topics/refs/heads/main/tags_json/tag_relations.json"
        
        self.json_url = json_url
        self.tag_relations = self._load_tag_relations()
    
    def _load_tag_relations(self) -> List[Dict]:
        """
        Carga las relaciones de tags desde el JSON remoto.
        
        Returns:
            Lista con las relaciones de tags o lista vacía si falla.
        """
        try:
            response = requests.get(self.json_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error cargando tag_relations.json: {e}")
            return []
    
    def enrich_tags(self, existing_tags: List[str], title: str, 
                    subtitle: str, body: str) -> List[str]:
        """
        Enriquece la lista de tags existentes basándose en el contenido
        de la noticia y las relaciones definidas en el JSON.
        
        Args:
            existing_tags: Tags ya identificados en la noticia
            title: Título de la noticia
            subtitle: Subtítulo de la noticia
            body: Cuerpo de la noticia
        
        Returns:
            Lista de tags enriquecida (sin duplicados)
        """
        # Normalizar textos a minúsculas para comparación
        full_text = f"{title} {subtitle} {body}".lower()
        
        # Usar set para evitar duplicados
        enriched_tags = set(existing_tags)
        
        # Iterar sobre cada tag principal y sus relaciones
        for tag_stat in self.tag_relations:
            main_tag = tag_stat.get('tag', '')
            if not main_tag:
                continue
            
            # Dividir el tag principal en palabras y buscar en el texto
            main_tag_words = main_tag.lower()
            
            # Verificar si alguna palabra del tag principal aparece en el texto
            if any(word in full_text for word in main_tag_words if len(word) > 3):
                # Obtener tags relacionados
                related_tags = tag_stat.get('related_tags', [])
                
                # Para cada tag relacionado, verificar si aparece en el texto
                for related_tag in related_tags:
                    related_tag_lower = related_tag.lower()
                    
                    # Buscar el tag relacionado en el texto completo
                    if related_tag_lower in full_text:
                        enriched_tags.add(related_tag)
                break
        
        return list(enriched_tags)
    
    def reload_relations(self):
        """
        Recarga las relaciones de tags desde el JSON remoto.
        Útil si el JSON se actualiza durante la ejecución.
        """
        self.tag_relations = self._load_tag_relations()
