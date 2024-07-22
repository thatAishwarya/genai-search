from azure.ai.formrecognizer import FormRecognizerClient
from azure.storage.blob import BlobServiceClient
from docx import Document
import os
from config import FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, BLOB_SERVICE_ENDPOINT

# Set the directory where documents are located
DATA_DIR = "../Data/TCA"

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file using Azure Form Recognizer.
    """
    form_recognizer_client = FormRecognizerClient(endpoint=FORM_RECOGNIZER_ENDPOINT, credential=DefaultAzureCredential())
    
    with open(file_path, "rb") as file:
        poller = form_recognizer_client.begin_read_in_stream(file, content_type="application/pdf")
        result = poller.result()
    text = ""
    for page_result in result.analyze_result.read_results:
        for line in page_result.lines:
            text += line.text + "\n"
    return text

def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file.
    """
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_text_from_txt(file_path):
    """
    Extract text from a TXT file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text_from_file(file_path):
    """
    Extract text from a file based on its extension.
    """
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

def process_documents():
    """
    Process all documents from the DATA_DIR directory.
    """
    documents = []
    file_names = []
    for file_name in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file_name)
        if os.path.isfile(file_path):
            content = extract_text_from_file(file_path)
            documents.append(content)
            file_names.append(file_name)
    return documents, file_names
