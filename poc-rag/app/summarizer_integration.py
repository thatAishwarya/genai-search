from transformers import BartTokenizer, BartForConditionalGeneration
import re

class SummarizerModel:
    def __init__(self, model_name='facebook/bart-large-cnn'):
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)

    def preprocess_text(self, text):
        # Preprocess text to remove unwanted characters and ensure proper formatting
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\[.*?\]', '', text)  # Remove bracketed text often found in legal documents
        return text.strip()

    def summarize_text(self, text):
        text = self.preprocess_text(text)
        inputs = self.tokenizer(text, return_tensors='pt', max_length=1024, truncation=True)
        outputs = self.model.generate(
            inputs['input_ids'],
            max_length=2000,
            min_length=50,
            length_penalty=2.0,
            num_beams=4
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
