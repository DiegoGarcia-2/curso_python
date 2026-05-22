"""
Indexador: conecta pdf_functions.py con la base de datos SQLAlchemy.
"""

import re
from collections import Counter
from extensions import db
from models import Document, Chunk
from pdf_functions import get_pdfs, extract_year_from_text, build_chunks


def count_words(text: str) -> int:
    """Cuenta palabras (tokens alfabéticos) en un texto."""
    return len(re.findall(r"[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]+", text))


def scrape_and_index(source_url_obj, download_path: str, markdown_path: str,
                     progress_callback=None) -> int:
    """
    Descarga e indexa todos los PDFs de `source_url_obj.address`.
    Retorna el número de documentos nuevos indexados.
    """
    def log(msg):
        if progress_callback:
            progress_callback(msg)

    pdf_dict = get_pdfs(
        url=source_url_obj.address,
        download_path=download_path,
        markdown_path=markdown_path,
        progress_callback=log,
    )

    indexed = 0
    for filename, pdf_doc in pdf_dict.items():

        existing = Document.query.filter_by(original_url=pdf_doc.url).first()
        if existing:
            log(f"Ya indexado: {filename}")
            continue

        content = pdf_doc.content or ""
        year    = extract_year_from_text(content, filename)
        wcount  = count_words(content)

        doc = Document(
            filename=filename,
            source_url_id=source_url_obj.id,
            original_url=pdf_doc.url,
            year=year,
            word_count=wcount,
            ocr_used=pdf_doc.ocr_used,
        )
        db.session.add(doc)
        db.session.flush()   

        chunks = build_chunks(content, chunk_length=20)
        for chunk_text in chunks:
            if chunk_text.strip():
                db.session.add(Chunk(document_id=doc.id, text=chunk_text))

        db.session.commit()
        indexed += 1
        log(f"Indexado: {filename} | año={year} | palabras={wcount} | OCR={pdf_doc.ocr_used}")

    return indexed


def get_global_stats() -> dict:
    """Estadísticas globales para la página Home."""
    from sqlalchemy import func

    total_docs  = Document.query.count()
    total_words = db.session.query(func.sum(Document.word_count)).scalar() or 0

    rows = (
        db.session.query(Document.year, func.count(Document.id))
        .filter(Document.year.isnot(None))
        .group_by(Document.year)
        .order_by(Document.year.desc())
        .all()
    )
    docs_by_year = {str(year): count for year, count in rows}

    return {
        "total_docs":  total_docs,
        "total_words": int(total_words),
        "docs_by_year": docs_by_year,
    }
