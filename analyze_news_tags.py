97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
230
231
232
233
234
235
236
237
238
239
240
241
242
243
244
245
246
247
248
249
250
251
252
253
254
255
256
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
    Encuentra componentes conectados de tags relacionados mediante DFS iterativa.

    Usa una pila explícita para evitar RecursionError en grafos grandes.
    """
    print("\n🎯 Identificando clusters de tags relacionados...")

    visited = set()
    clusters = []

    # Encontrar todos los componentes conectados sin recursión.
    for start_tag in tag_relations:
        if start_tag in visited:
            continue

        cluster = set()
        stack = [start_tag]
        visited.add(start_tag)

        while stack:
            tag = stack.pop()
            cluster.add(tag)

            for related_tag in tag_relations.get(tag, set()):
                if related_tag not in visited:
                    # Marcar al añadirlo a la pila para no insertarlo varias veces.
                    visited.add(related_tag)
                    stack.append(related_tag)

        if len(cluster) >= min_cluster_size:
            clusters.append(cluster)

    # Convertir a formato legible con tags capitalizados.
    clusters_formatted = []
    for cluster in sorted(clusters, key=len, reverse=True):
        cluster_tags = sorted(tag_canonical[tag] for tag in cluster)
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
