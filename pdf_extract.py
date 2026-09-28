import pdfplumber


def extract_text(file) -> str:
    """Extract all text from a bank statement PDF, page by page."""
    pages = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return "\n".join(pages)
