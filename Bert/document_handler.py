import os
import fitz  # PyMuPDF

class DocumentHandler:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.documents = self._load_documents()

    def _read_pdf_file(self, file_path):
        doc = fitz.open(file_path)
        pages_text = {}
        for page in range(len(doc)):
            pages_text[page] = doc[page].get_text()
        return pages_text

    def _load_documents(self):
        documents = {}
        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)
            if filename.endswith('.pdf'):
                documents[filename] = self._read_pdf_file(file_path)
        return documents

    def get_documents(self):
        return self.documents
