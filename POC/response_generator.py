from transformers import T5Tokenizer, T5ForConditionalGeneration

class ResponseGenerator:
    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.model = T5ForConditionalGeneration.from_pretrained('t5-small')
    
    def generate_response(self, context: str, query: str) -> str:
        input_text = f"question: {query} context: {context}"
        inputs = self.tokenizer(input_text, return_tensors='pt', max_length=512, truncation=True)
        outputs = self.model.generate(inputs['input_ids'], max_length=150)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
