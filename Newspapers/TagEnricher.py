import requests
import re
from typing import List, Dict


class TagEnricher:
    """
    Enriquece tags de noticias usando búsqueda por PALABRAS completas.
    - Regex con límites de palabra para TODOS los casos
    - Soporte para acentos y caracteres españoles
    """

    def __init__(self, json_url: str = None):
        if json_url is None:
            json_url = (
                "https://raw.githubusercontent.com/Alfesito/ES-News-Topics/"
                "refs/heads/main/tags_json/tag_relations.json"
            )

        self.json_url = json_url
        self.tag_relations = self._load_tag_relations()
        print(f"🔧 TagEnricher inicializado con {len(self.tag_relations)} tags")

    def _load_tag_relations(self) -> Dict[str, List[str]]:
        try:
            response = requests.get(self.json_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "direct_relations" in data and isinstance(data["direct_relations"], dict):
                return data["direct_relations"]

            if "tag_stats" in data and isinstance(data["tag_stats"], list):
                return {
                    item["tag"]: item["related_tags"]
                    for item in data
                    if isinstance(item, dict)
                    and "tag" in item
                    and "related_tags" in item
                }

            print("⚠️ Estructura de tag_relations no reconocida")
            return {}

        except Exception as e:
            print(f"❌ Error cargando tag_relations.json: {e}")
            return {}

    def _is_word_in_text(self, word: str, text: str) -> bool:
        """
        Busca una palabra completa (con límites de palabra \b).
        Maneja correctamente acentos y caracteres españoles.
        """
        # Escapar caracteres especiales de regex
        escaped_word = re.escape(word)
        
        # Patrón con límites de palabra
        pattern = rf"\b{escaped_word}\b"
        
        # Búsqueda case-insensitive con soporte Unicode
        return re.search(pattern, text, re.IGNORECASE | re.UNICODE) is not None

    def enrich_tags(
        self,
        existing_tags: List[str],
        title: str,
        subtitle: str,
    ) -> List[str]:

        if not isinstance(existing_tags, list):
            existing_tags = []

        # Texto completo (mantener mayúsculas/minúsculas originales para regex)
        full_text = f"{title} {subtitle}"

        enriched_tags = set(existing_tags)

        if not self.tag_relations:
            return list(enriched_tags)

        tags_found = 0

        for main_tag, related_tags in self.tag_relations.items():
            if not isinstance(main_tag, str):
                continue

            # Ignorar tags excesivamente cortos (ruido)
            if len(main_tag) <= 2:
                continue

            # ---- MATCH PRINCIPAL (SIEMPRE con límites de palabra) ----
            if self._is_word_in_text(main_tag, full_text):
                if main_tag not in enriched_tags:
                    enriched_tags.add(main_tag.lower())
                    tags_found += 1

                # ---- TAGS RELACIONADOS ----
                if not isinstance(related_tags, list):
                    continue

                for related_tag in related_tags:
                    if not isinstance(related_tag, str):
                        continue

                    if len(related_tag) <= 2:
                        continue

                    if self._is_word_in_text(related_tag, full_text):
                        if related_tag not in enriched_tags:
                            enriched_tags.add(related_tag.lower())
                            tags_found += 1

        if tags_found > 0:
            print(
                f"📌 '{title[:40]}...' → +{tags_found} tags | "
                f"Total: {len(enriched_tags)}"
            )

        return list(enriched_tags)

    def reload_relations(self):
        self.tag_relations = self._load_tag_relations()
