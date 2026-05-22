"""
PDF Search System — Aplicación Flask principal
Desarrollo 4 · 2026
"""

import os
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

from extensions import db
from models     import SourceURL, Document, Chunk
from indexer    import scrape_and_index, get_global_stats
from searcher   import search as doc_search


BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
MARKDOWN_PATH = os.path.join(BASE_DIR, "markdown_files")

app = Flask(__name__)
app.config["SECRET_KEY"]                  = "pdf-search-dev-secret-2026"
app.config["SQLALCHEMY_DATABASE_URI"]     = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'pdf_search.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs(DOWNLOAD_PATH,              exist_ok=True)
os.makedirs(MARKDOWN_PATH,             exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

db.init_app(app)

_scrape_status: dict[int, dict] = {}

def init_db():
    db.create_all()
    if SourceURL.query.count() == 0:
        default = SourceURL(
            address="https://fi-ing.unison.mx/acuerdos-de-sesiones-del-h-colegio-de-la-facultad-interdisciplinaria-de-ingenieria-2026/",
            scraped=False,
        )
        db.session.add(default)
        db.session.commit()
        print("BD inicializada con URL de ejemplo.")

@app.route("/")
def home():
    stats = get_global_stats()
    return render_template("home.html", stats=stats)


@app.route("/api/stats")
def api_stats():
    return jsonify(get_global_stats())

@app.route("/scrapper")
def scrapper():
    sources = SourceURL.query.order_by(SourceURL.added_at.desc()).all()
    data = []
    for s in sources:
        docs   = s.documents.all()
        status = _scrape_status.get(s.id, {"running": False, "progress": ""})
        data.append({"source": s, "documents": docs, "status": status})
    return render_template("scrapper.html", data=data)


@app.route("/scrapper/start/<int:sid>", methods=["POST"])
def scrapper_start(sid):
    source = SourceURL.query.get_or_404(sid)

    if _scrape_status.get(sid, {}).get("running"):
        return jsonify({"error": "Ya está corriendo"}), 409

    _scrape_status[sid] = {"running": True, "progress": "Iniciando…"}

    def run():
        def cb(msg):
            _scrape_status[sid]["progress"] = msg

        with app.app_context():
            try:
                n = scrape_and_index(source, DOWNLOAD_PATH, MARKDOWN_PATH,
                                     progress_callback=cb)
                src = SourceURL.query.get(sid)
                if src:
                    src.scraped = True
                    db.session.commit()
                _scrape_status[sid] = {"running": False,
                                       "progress": f"✓ Listo — {n} documentos nuevos indexados."}
            except Exception as e:
                _scrape_status[sid] = {"running": False, "progress": f"✗ Error: {e}"}

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/scrapper/status/<int:sid>")
def scrapper_status(sid):
    status = _scrape_status.get(sid, {"running": False, "progress": ""})
    source = SourceURL.query.get(sid)
    docs   = []
    if source:
        docs = [
            {"filename": d.filename, "year": d.year, "ocr": d.ocr_used}
            for d in source.documents.all()
        ]
    return jsonify({"running": status["running"],
                    "progress": status["progress"],
                    "docs": docs,
                    "scraped": source.scraped if source else False})

@app.route("/configuration", methods=["GET", "POST"])
def configuration():
    if request.method == "POST":
        address = request.form.get("url", "").strip()
        if address:
            if not address.startswith(("http://", "https://")):
                address = "https://" + address
            if SourceURL.query.filter_by(address=address).first():
                flash("Esa URL ya existe.", "warning")
            else:
                db.session.add(SourceURL(address=address, scraped=False))
                db.session.commit()
                flash("URL agregada correctamente.", "success")
        else:
            flash("Ingresa una URL válida.", "danger")
        return redirect(url_for("configuration"))

    sources = SourceURL.query.order_by(SourceURL.added_at.desc()).all()
    return render_template("configuration.html", sources=sources)


@app.route("/configuration/delete/<int:sid>", methods=["POST"])
def configuration_delete(sid):
    source = SourceURL.query.get_or_404(sid)
    db.session.delete(source)
    db.session.commit()
    flash("URL eliminada.", "info")
    return redirect(url_for("configuration"))

@app.route("/search")
def search():
    query     = request.args.get("q", "").strip()
    threshold = float(request.args.get("threshold", 0.50))
    threshold = max(0.0, min(1.0, threshold))
    results   = doc_search(query, threshold) if query else []
    return render_template("search.html", query=query,
                           results=results, threshold=threshold)

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000)
