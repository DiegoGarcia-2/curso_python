"""
Modelos de base de datos para el sistema PDF Search.
"""

from datetime import datetime
from extensions import db


class SourceURL(db.Model):
    """URL de origen desde donde se scrapean PDFs."""
    __tablename__ = "source_urls"

    id       = db.Column(db.Integer, primary_key=True)
    address  = db.Column(db.String(2048), unique=True, nullable=False)
    scraped  = db.Column(db.Boolean, default=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship("Document", backref="source", lazy="dynamic",
                                 cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SourceURL {self.address}>"


class Document(db.Model):
    """Documento PDF indexado."""
    __tablename__ = "documents"

    id           = db.Column(db.Integer, primary_key=True)
    filename     = db.Column(db.String(512), nullable=False)
    source_url_id = db.Column(db.Integer, db.ForeignKey("source_urls.id"))
    original_url = db.Column(db.String(2048))   # URL directa al PDF
    year         = db.Column(db.Integer)
    word_count   = db.Column(db.Integer, default=0)
    ocr_used     = db.Column(db.Boolean, default=False)
    indexed_at   = db.Column(db.DateTime, default=datetime.utcnow)

    chunks = db.relationship("Chunk", backref="document", lazy="dynamic",
                              cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.filename}>"


class Chunk(db.Model):
    """
    Fragmento de 20 caracteres de un documento (estructura del profesor).
    Permite búsqueda con similitud Levenshtein.
    """
    __tablename__ = "chunks"

    id          = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False)
    text        = db.Column(db.String(64), nullable=False)

    __table_args__ = (db.Index("idx_chunk_text", "text"),)

    def __repr__(self):
        return f"<Chunk '{self.text[:15]}…'>"
