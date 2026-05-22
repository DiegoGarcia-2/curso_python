"""
Motor de búsqueda: usa similitud Levenshtein (exactamente como el profesor)
sobre los chunks almacenados en la base de datos.
"""

import Levenshtein
from models import Chunk, Document
from pdf_functions import Frase, buscar_palabras_ratio


def search(query: str, threshold: float = 0.50, max_results: int = 30) -> list[dict]:
    """
    Busca `query` en todos los chunks de la BD usando Levenshtein.ratio.
    Retorna lista de dicts con: filename, original_url, block, similarity (%).
    """
    if not query:
        return []

    all_chunks_db = Chunk.query.all()

    frases = []
    for c in all_chunks_db:
        doc   = Document.query.get(c.document_id)
        fname = doc.filename     if doc else ""
        furl  = doc.original_url if doc else ""
        frases.append(Frase(c.text, source_filename=fname, source_url=furl))

    encontradas = buscar_palabras_ratio(frases, query, umbral=threshold)

    best_per_doc: dict[str, dict] = {}
    for f in encontradas:
        key = f.source_url or f.source_filename
        if key not in best_per_doc or f.ratio > best_per_doc[key]["similarity_raw"]:
            best_per_doc[key] = {
                "filename":       f.source_filename,
                "original_url":   f.source_url,
                "block":          f.frase,
                "similarity":     round(f.ratio * 100, 1),
                "similarity_raw": f.ratio,
            }

    results = sorted(best_per_doc.values(),
                     key=lambda x: x["similarity_raw"], reverse=True)
    return results[:max_results]
