# 📄 DocSearch — Sistema Web de Búsqueda de PDFs

Sistema web desarrollado en **Python + Flask + Bootstrap** para indexar y buscar documentos PDF obtenidos mediante web scraping.

**Desarrollo 4 · 2026** — Proyecto en solitario :(

## 🚀 Características

| Módulo | Descripción |
 **Home**  Dashboard con total de documentos, palabras indexadas y documentos por año (con gráfica de barras y auto-refresh) 
 **Scrapper**  Lista de URLs configuradas con su estatus, botón de inicio de scraping y lista de archivos encontrados con polling en tiempo real 
 **Configuration**  Agregar / eliminar URLs a escrapear 
 **Search**  Búsqueda por similitud Levenshtein con slider de umbral (0–1) y visualización de porcentaje y bloque de texto encontrado 
 **OCR**  Fallback automático con PyMuPDF + pytesseract para PDFs basados en imágenes 


## ⚙️ Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/pdf-search.git
cd pdf-search
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate        

pip install -r requirements.txt
```

### 3. Dependencias del sistema (para OCR)
```bash
sudo apt install tesseract-ocr tesseract-ocr-spa

brew install tesseract tesseract-lang
```

### 4. Ejecutar la aplicación
```bash
python app.py
```

Abrir en el navegador: **http://localhost:5000**

---

## 🔍 Cómo usar

1. **Configuration** → Agrega las URLs que contienen enlaces a PDFs
2. **Scrapper** → Inicia el scraping de cada URL con el botón **Scrape**
   - Se descargan los PDFs, se convierten a Markdown y se indexan
   - Si un PDF no tiene texto digitalizado, se aplica OCR automáticamente
3. **Home** → Consulta las estadísticas actualizadas
4. **Barra de búsqueda / /search** → Busca texto usando similitud Levenshtein
   - Ajusta el umbral con el slider (0 = cualquier resultado, 1 = idéntico)

---

## 🧠 Lógica de búsqueda

Basada en el código del profesor (`pdf_functins.py`):

```python
chunks = [content[i:i+20] for i in range(0, len(content), 20)]

ratio = Levenshtein.ratio(chunk.lower(), query.lower())
if ratio >= umbral:
    resultados.append(chunk)
```

---

## 📦 Dependencias principales

- `Flask` + `Flask-SQLAlchemy` — Backend y ORM
- `markitdown` — Conversión PDF → Markdown
- `python-Levenshtein` — Similitud de texto
- `beautifulsoup4` + `requests` — Web scraping
- `PyMuPDF` + `pytesseract` — OCR para PDFs de imagen
- `Bootstrap 5` — Frontend

---

## 👥 Autor


|Diego Andres Garcia González|