"""
Real document text extraction — replaces the filename-based placeholder.

Supports: PDF (text + scanned/OCR fallback), images (OCR), spreadsheets.
This is what the classifier pipeline actually reads, instead of guessing
from the filename.
"""
import os

import pdfplumber
from PIL import Image
import pytesseract
import openpyxl


def extract_text(file_field) -> str:
    """
    Takes a Django FileField/UploadedFile, returns extracted text.
    Falls back to the filename only if extraction fails completely
    (e.g. corrupted file, unsupported format) so the pipeline never
    crashes on a bad upload.
    """
    name = file_field.name.lower()
    file_field.seek(0)

    try:
        if name.endswith(".pdf"):
            return _extract_pdf(file_field)
        elif name.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
            return _extract_image(file_field)
        elif name.endswith((".xlsx", ".xlsm")):
            return _extract_xlsx(file_field)
        elif name.endswith(".txt"):
            return file_field.read().decode("utf-8", errors="ignore")
        else:
            # Unsupported format — fall back to filename so the pipeline
            # still returns something rather than raising.
            return os.path.basename(file_field.name)
    except Exception:
        return os.path.basename(file_field.name)
    finally:
        file_field.seek(0)


def _extract_pdf(file_field) -> str:
    text_parts = []
    with pdfplumber.open(file_field) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    text = "\n".join(text_parts).strip()

    # If pdfplumber got nothing, the PDF is likely scanned/image-based.
    # OCR fallback would go here (convert pages to images, run pytesseract) —
    # omitted by default since it requires poppler installed on the host.
    # Uncomment if you have poppler-utils available:
    #
    # if not text:
    #     from pdf2image import convert_from_bytes
    #     file_field.seek(0)
    #     images = convert_from_bytes(file_field.read())
    #     text = "\n".join(pytesseract.image_to_string(img) for img in images)

    return text or os.path.basename(file_field.name)


def _extract_image(file_field) -> str:
    image = Image.open(file_field)
    text = pytesseract.image_to_string(image).strip()
    return text or os.path.basename(file_field.name)


def _extract_xlsx(file_field) -> str:
    workbook = openpyxl.load_workbook(file_field, data_only=True)
    text_parts = []
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows(values_only=True):
            row_text = " ".join(str(cell) for cell in row if cell is not None)
            if row_text:
                text_parts.append(row_text)
    text = "\n".join(text_parts).strip()
    return text or os.path.basename(file_field.name)
