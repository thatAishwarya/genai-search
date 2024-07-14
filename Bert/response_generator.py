from transformers import BertTokenizer, BertForSequenceClassification
import torch

class ResponseGenerator:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.model = BertForSequenceClassification.from_pretrained("bert-base-uncased")

    def generate_summary(self, context):
        # Here we can just return a simple snippet instead of actual summarization
        return context[:512]  # Truncate for simplicity
