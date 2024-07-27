import os
import PyPDF2
from logging_config import setup_logging

# Initialize logging
logger = setup_logging()

def extract_text_from_pdfs(pdf_dir):
    logger.info(f"Extracting text from PDFs in directory: {pdf_dir}")
    page_texts = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_dir, filename)
            logger.debug(f"Processing file: {filepath}")
            try:
                with open(filepath, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            # Include metadata with the document name and page number
                            page_texts.append({
                                "filename": filename,
                                "page_num": page_num + 1,
                                "content": page_text
                            })
                            logger.debug(f"Extracted text from page {page_num + 1} of file {filename}")
            except Exception as e:
                logger.error(f"Error processing file {filepath}: {e}")
    return page_texts
