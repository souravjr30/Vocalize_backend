from transformers import pipeline

class TextSummarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    def summarize(self, text, max_length=130, min_length=30):
        # Split the text into chunks that the model can handle
        max_input_length = 1024  # BART model's maximum input length
        chunks = [text[i:i + max_input_length] for i in range(0, len(text), max_input_length)]
        
        # Summarize each chunk and combine the results
        summaries = [self.summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text'] for chunk in chunks]
        return " ".join(summaries)