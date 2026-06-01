import fitz

def extract_text_from_pdf(pdf_path, document_id=None, filename=None):
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page": page_num + 1,
            "text": text,
            "document_id": document_id,
            "filename": filename,
        })

    return pages