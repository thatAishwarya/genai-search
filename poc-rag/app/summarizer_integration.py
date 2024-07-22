from transformers import BartTokenizer, BartForConditionalGeneration

class SummarizerModel:
    def __init__(self, model_name='facebook/bart-large-cnn'):
        # Load the BART tokenizer and model for summarization
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)

    def summarize_text(self, text):
        # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors='pt', max_length=1024, truncation=True)
        # Generate the summary
        outputs = self.model.generate(
            inputs['input_ids'],
            max_length=150,  # Adjust max_length as needed
            min_length=50,   # Adjust min_length as needed
            length_penalty=2.0,
            num_beams=4
        )
        # Decode and return the summary
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
