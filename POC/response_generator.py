from transformers import T5ForConditionalGeneration, T5Tokenizer
from typing import List, Dict
import os

class ResponseGenerator:
    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        self.model = T5ForConditionalGeneration.from_pretrained('t5-base')
    
    def _generate_text(self, input_text: str, task: str) -> str:
        input_text = f"{task}: {input_text}"
        inputs = self.tokenizer.encode(input_text, return_tensors="pt")
        outputs = self.model.generate(inputs, max_length=512, num_beams=4, early_stopping=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def generate_response(self, contexts: List[Dict[str, str]], query: str) -> Dict[str, List[Dict[str, str]]]:
        responses = []
        documents = []

        for context in contexts:
            extractive_input = f"question: {query} context: {context['text']}"
            extractive_answer = self._generate_text(extractive_input, "extractive QA")
            
            document_info = {
                "file_name": os.path.basename(context['file_path']),
                "file_title": "Document Title",  # Replace with actual title if available
                "page_number": context['page_number'],
                "summary": extractive_answer
            }
            documents.append(document_info)

        all_texts = " ".join([context['text'] for context in contexts])
        summary_input = f"summarize: {all_texts}"
        summary = self._generate_text(summary_input, "summarization")

        return {
            "response": summary,
            "documents": documents
        }
