import pymupdf


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF resume.

    Parameters:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """

    try:
        pdf_document = pymupdf.open(pdf_path)

        text = ""

        for page in pdf_document:
            page_text = page.get_text()
            text += page_text + "\n"

        pdf_document.close()

        return text.strip()

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""