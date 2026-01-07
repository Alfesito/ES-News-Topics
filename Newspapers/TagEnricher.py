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
        print(f"🔧 TagEnricher inicializado con {len(self.tag_relations)} tags cargados")
    
    def _load_tag_relations(self) -> Dict[str, List[str]]:
        """
        Carga las relaciones de tags desde el JSON remoto.
        Convierte a formato: {'tag1': ['related1', 'related2'], 'tag2': [...]}
        
        Returns:
            Diccionario con tag -> lista de tags relacionados
        """
        try:
            response = requests.get(self.json_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"🔍 DEBUG: Claves principales del JSON: {list(data.keys())}")
            
            # Intentar diferentes estructuras
            tag_dict = {}
            
            # Opción 1: Usar direct_relations
            if 'direct_relations' in data and isinstance(data['direct_relations'], dict):
                print(f"✅ Usando 'direct_relations' con {len(data['direct_relations'])} tags")
                tag_dict = data['direct_relations']
                # Mostrar ejemplo
                first_key = list(tag_dict.keys())[0] if tag_dict else None
                if first_key:
                    print(f"   Ejemplo: '{first_key}' -> {tag_dict[first_key][:3]}...")
            
            # Opción 2: Usar transitive_relations
            elif 'transitive_relations' in data and isinstance(data['transitive_relations'], dict):
                print(f"✅ Usando 'transitive_relations' con {len(data['transitive_relations'])} tags")
                tag_dict = data['transitive_relations']
                first_key = list(tag_dict.keys())[0] if tag_dict else None
                if first_key:
                    print(f"   Ejemplo: '{first_key}' -> {tag_dict[first_key][:3]}...")
            
            # Opción 3: Convertir tag_stats si tiene related_tags
            elif 'tag_stats' in data and isinstance(data['tag_stats'], list):
                print(f"✅ Convirtiendo 'tag_stats' ({len(data['tag_stats'])} elementos)")
                for item in data['tag_stats']:
                    if isinstance(item, dict) and 'tag' in item and 'related_tags' in item:
                        tag_dict[item['tag']] = item['related_tags']
                
                if tag_dict:
                    first_key = list(tag_dict.keys())[0]
                    print(f"   Ejemplo: '{first_key}' -> {tag_dict[first_key][:3]}...")
            
            else:
                print(f"⚠️ No se encontró estructura de relaciones reconocida")
                print(f"   Estructuras disponibles: {list(data.keys())}")
                # Mostrar muestra de cada estructura
                for key in list(data.keys())[:3]:
                    val = data[key]
                    if isinstance(val, dict):
                        print(f"   '{key}' (dict): {list(val.keys())[:5] if val else 'vacío'}")
                    elif isinstance(val, list):
                        print(f"   '{key}' (list): {len(val)} elementos, primer elemento: {val[0] if val else 'vacío'}")
                    else:
                        print(f"   '{key}': {type(val)}")
            
            return tag_dict
            
        except Exception as e:
            print(f"❌ Error cargando tag_relations.json: {e}")
            import traceback
            print(traceback.format_exc())
            return {}
    
    def enrich_tags(self, existing_tags: List[str], title: str, 
                    subtitle: str, body: str) -> List[str]:
        """
        Enriquece la lista de tags basándose en el contenido de la noticia.
        Busca automáticamente tags relevantes aunque no haya tags iniciales.
        
        Args:
            existing_tags: Tags ya identificados en la noticia (puede estar vacío)
            title: Título de la noticia
            subtitle: Subtítulo de la noticia
            body: Cuerpo de la noticia
        
        Returns:
            Lista de tags encontrados (sin duplicados)
        """
        try:
            # Validar que existing_tags sea una lista
            if not isinstance(existing_tags, list):
                existing_tags = []
            
            # Normalizar textos a minúsculas para comparación
            full_text = f"{title} {subtitle} {body}".lower()
            
            # Usar set para evitar duplicados
            enriched_tags = set(existing_tags)
            
            # Verificar que tag_relations no esté vacío
            if not self.tag_relations:
                print(f"⚠️ No hay relaciones cargadas para enriquecer")
                return list(enriched_tags)
            
            tags_found = 0
            
            # Iterar sobre TODOS los tags principales
            for main_tag, related_tags in self.tag_relations.items():
                # Normalizar el tag principal
                main_tag_lower = main_tag.lower()
                
                # Buscar el tag principal en el texto
                if main_tag_lower in full_text:
                    # Añadir el tag principal
                    if main_tag not in enriched_tags:
                        enriched_tags.add(main_tag)
                        tags_found += 1
                    
                    # Validar que related_tags sea una lista
                    if not isinstance(related_tags, list):
                        continue
                    
                    # Para cada tag relacionado, verificar si aparece en el texto
                    for related_tag in related_tags:
                        if not isinstance(related_tag, str):
                            continue
                        
                        related_tag_lower = related_tag.lower()
                        
                        # Buscar el tag relacionado en el texto completo
                        if related_tag_lower in full_text:
                            if related_tag not in enriched_tags:
                                enriched_tags.add(related_tag)
                                tags_found += 1
            
            result = list(enriched_tags)
            
            # Mostrar resultado si se encontraron tags
            if tags_found > 0:
                print(f"   📌 '{title[:40]}...' → +{tags_found} tags: {result[:5]}")
            
            return result
            
        except Exception as e:
            print(f"❌ TagEnricher.enrich_tags error: {str(e)[:100]}")
            import traceback
            print(traceback.format_exc()[:300])
            # Retornar los tags originales si hay error
            return existing_tags if isinstance(existing_tags, list) else []
    
    def reload_relations(self):
        """
        Recarga las relaciones de tags desde el JSON remoto.
        """
        self.tag_relations = self._load_tag_relations()
