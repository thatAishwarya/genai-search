import os
import pdfplumber
from docx import Document
from typing import List, Dict

def extract_text_from_pdf(file_path: str) -> List[Dict[str, str]]:
    text_data = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text_data.append({
                "text": page.extract_text(),
                "file_path": file_path,
                "page_number": i + 1
            })
    return text_data

def extract_text_from_docx(file_path: str) -> List[Dict[str, str]]:
    doc = Document(file_path)
    text_data = []
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    text_data.append({
        "text": text,
        "file_path": file_path,
        "page_number": 1
    })
    return text_data

def extract_text_from_txt(file_path: str) -> List[Dict[str, str]]:
    with open(file_path, 'r') as file:
        return [{
            "text": file.read(),
            "file_path": file_path,
            "page_number": 1
        }]

def extract_text(file_path: str) -> List[Dict[str, str]]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def extract_text_from_directory(directory_path: str) -> List[Dict[str, str]]:
    texts = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            texts.extend(extract_text(file_path))
    return texts
