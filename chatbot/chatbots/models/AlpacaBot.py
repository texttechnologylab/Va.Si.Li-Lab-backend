from transformers import pipeline
import torch

class AlpacaBot:
    def __init__(self, model_path: str = "declare-lab/flan-alpaca-large"):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = pipeline(model=model_path, device=device)

    def get_response(self, question: str):
        output = self.model(question, max_length=512, do_sample=True)
        res = output[0]["generated_text"]
        return f"{res}"


if __name__ == "__main__":
    chatbot = AlpacaBot()
    output_chat = chatbot.get_response("What is a Chatbot?")
    print(output_chat)
