from PyPDF2 import PdfReader
import os
import re

class DocumentProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def clean_text(self, text):
        text = re.sub(r'[^\w\s.,!?\'"]', '', text)
        text = ' '.join(text.split())
        return text

    def load_pdfs(self):
        documents = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.pdf'):
                path = os.path.join(self.folder_path, filename)
                try:
                    with open(path, 'rb') as file:
                        reader = PdfReader(file)
                        for page_num, page in enumerate(reader.pages):
                            page_text = page.extract_text() or ''
                            if not page_text.strip():
                                print(f"Warning: No text extracted from page {page_num + 1} of {filename}")
                            else:
                                page_text = self.clean_text(page_text)
                                documents.append((filename, page_num + 1, page_text))
                except Exception as e:
                    print(f"Error processing file {filename}: {e}")
        return documents
