from PyPDF2 import PdfReader
import os
import re

class DocumentProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def clean_text(self, text):
        # Remove special characters (keeping only alphanumeric and basic punctuation)
        text = re.sub(r'[^\w\s.,!?\'"]', '', text)
        # Normalize whitespace
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
                        text = ''
                        for page_num, page in enumerate(reader.pages):
                            # Extract text from each page
                            page_text = page.extract_text() or ''
                            # Check for empty pages
                            if not page_text.strip():
                                print(f"Warning: No text extracted from page {page_num + 1} of {filename}")
                            else:
                                # Clean the extracted text
                                page_text = self.clean_text(page_text)
                                text += page_text
                        if text.strip():  # Ensure there is some text before adding
                            documents.append((filename, text))
                        else:
                            print(f"Warning: No valid text extracted from {filename}")
                except Exception as e:
                    print(f"Error processing file {filename}: {e}")
        return documents
