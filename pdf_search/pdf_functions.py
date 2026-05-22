"""
PDF functions for searching and processing PDF files from a webpage.
Basado en el código original del profesor, extendido para integración con Flask/BD.
"""

import os
import re
import requests
import Levenshtein
from bs4 import BeautifulSoup
from markitdown import MarkItDown


class pdf_document:
    """Representa un documento PDF con su URL, ruta local y contenido markdown."""

    def __init__(self, url, pdf_path, markdown_path):
        self.url          = url
        self.pdf_path     = pdf_path
        self.markdown_path = markdown_path
        self.content      = None
        self.ocr_used     = False
        self.convert_pdf_to_markdown()

    def convert_pdf_to_markdown(self):
        """Convierte PDF a Markdown usando MarkItDown; recurre a OCR si el texto es escaso."""
        try:
            converter = MarkItDown()
            result    = converter.convert(self.pdf_path)
            markdown_content = result.text_content or ""

            if len(markdown_content.strip()) < 100:
                markdown_content = self._ocr_fallback()
                self.ocr_used = True

            with open(self.markdown_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.content = markdown_content
        except Exception as e:
            print(f"Error converting PDF to Markdown: {e}")
            try:
                self.content  = self._ocr_fallback()
                self.ocr_used = True
                with open(self.markdown_path, "w", encoding="utf-8") as f:
                    f.write(self.content)
            except Exception as ocr_err:
                print(f"OCR también falló: {ocr_err}")
                self.content = ""

    def _ocr_fallback(self):
        """OCR usando PyMuPDF + pytesseract para PDFs basados en imágenes."""
        import fitz          
        import pytesseract
        from PIL import Image

        text_pages = []
        try:
            doc = fitz.open(self.pdf_path)
            for page_num in range(min(len(doc), 15)):   
                page = doc[page_num]
                mat  = fitz.Matrix(2, 2)                
                pix  = page.get_pixmap(matrix=mat)
                img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                page_text = pytesseract.image_to_string(img, lang="spa+eng")
                text_pages.append(page_text)
            doc.close()
        except Exception as e:
            print(f"OCR error en {self.pdf_path}: {e}")
        return "\n".join(text_pages)

def get_webpage(url):
    """Descarga el HTML de una URL."""
    try:
        response = requests.get(url, timeout=15,
                                headers={"User-Agent": "Mozilla/5.0 (PDFSearchBot/2.0)"})
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_pdf_links(html, base_url=""):
    """Extrae todos los enlaces a PDFs del HTML."""
    soup      = BeautifulSoup(html, "html.parser")
    pdf_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.lower().endswith(".pdf"):
            if href.startswith("http"):
                pdf_links.append(href)
            elif base_url:
                from urllib.parse import urljoin
                pdf_links.append(urljoin(base_url, href))
            else:
                pdf_links.append(href)
    return pdf_links


def download_pdf(url, filename):
    """Descarga un PDF desde una URL y lo guarda en disco."""
    try:
        response = requests.get(url, timeout=20,
                                headers={"User-Agent": "Mozilla/5.0 (PDFSearchBot/2.0)"})
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF {url}: {e}")
        return False


def get_pdfs(url, download_path="downloads", markdown_path="markdown_files",
             progress_callback=None):
    """
    Orquesta la descarga e indexación de PDFs desde una URL.
    Retorna un dict {filename: pdf_document}.
    """
    os.makedirs(download_path,  exist_ok=True)
    os.makedirs(markdown_path,  exist_ok=True)

    def log(msg):
        print(f"[Scraper] {msg}")
        if progress_callback:
            progress_callback(msg)

    log(f"Fetching: {url}")
    html = get_webpage(url)
    if not html:
        log(f"No se pudo obtener la página: {url}")
        return {}

    pdf_links = extract_pdf_links(html, base_url=url)
    log(f"PDFs encontrados: {len(pdf_links)}")

    pdf_dict = {}
    for i, link in enumerate(pdf_links[:50]):         
        filename = link.split("/")[-1] or f"document_{i}.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        log(f"({i+1}/{len(pdf_links)}) Descargando: {filename}")

        downloaded_file = os.path.join(download_path, filename)
        ok = download_pdf(link, downloaded_file)
        if not ok:
            continue

        markdown_file = os.path.join(markdown_path,
                                     f"{os.path.splitext(filename)[0]}.md")
        log(f"Convirtiendo a Markdown: {filename}")
        pdf_doc = pdf_document(link, downloaded_file, markdown_file)
        pdf_dict[filename] = pdf_doc
        log(f"Listo: {filename} | OCR: {pdf_doc.ocr_used}")

    return pdf_dict

class Frase:
    """Contenedor de un fragmento de texto con su ratio de similitud."""
    def __init__(self, frase, source_filename="", source_url=""):
        self.frase           = frase
        self.ratio           = 0.0
        self.source_filename = source_filename
        self.source_url      = source_url


def buscar_palabras_ratio(frases: list, frase_a_buscar: str,
                          umbral: float = 0.50) -> list:
    """
    Busca una frase en una lista de objetos Frase usando similitud Levenshtein.
    Retorna los que superen el umbral, ordenados por ratio descendente.
    """
    frase_a_buscar = frase_a_buscar.lower()
    encontradas    = []
    for frase in frases:
        frase_lower = frase.frase.lower()
        ratio = Levenshtein.ratio(frase_lower, frase_a_buscar)
        if ratio >= umbral:
            frase.ratio = ratio
            encontradas.append(frase)
    encontradas.sort(key=lambda f: f.ratio, reverse=True)
    return encontradas


def extract_year_from_text(text: str, filename: str = "") -> int | None:
    """Intenta extraer el año de publicación del texto o nombre de archivo."""
    pattern = r"\b(19[6-9]\d|20[0-2]\d)\b"
    years   = re.findall(pattern, text[:3000])
    if not years:
        years = re.findall(pattern, filename)
    if years:
        from collections import Counter
        return int(Counter(years).most_common(1)[0][0])
    return None


def build_chunks(content: str, chunk_length: int = 20) -> list:
    """
    Divide el contenido en fragmentos de `chunk_length` caracteres,
    exactamente como lo hace el código del profesor.
    """
    return [content[i:i + chunk_length]
            for i in range(0, len(content), chunk_length)]
