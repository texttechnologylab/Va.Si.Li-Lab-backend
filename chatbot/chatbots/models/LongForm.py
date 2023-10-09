import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

class LongForm:
    def __init__(self, model_name: str, device_name: str = "cpu", max_new_tokens: int = 512):
        print("Loading model")
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.generation_config = GenerationConfig.from_pretrained (model_name)
        self.generation_config.top_p = 0.9
        self.generation_config.do_sample = True
        self.generation_config.max_new_tokens = max_new_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.device = device_name
        self.max_new_tokens = max_new_tokens
        if device_name != "cpu": self.model.to(device_name)
        print("Model Loaded")

    def get_response(self, question: str):
        torch.manual_seed(42)
        input_ids = self.tokenizer(f"{question}\n [EOI]", return_tensors="pt").input_ids.to(self.device)
        # if torch.cuda.is_available():
        #     input_ids = self.tokenizer(f"{question}\n [EOI]", return_tensors="pt").input_ids.to(self.device)
        # else:
        #     input_ids = self.tokenizer(f"{question}\n [EOI]", return_tensors="pt").input_ids
        target_ids = self.model.generate(input_ids, generation_config=self.generation_config)
        output = self.tokenizer.decode(target_ids[0], skip_special_tokens=True)
        output = output.replace(f"{question}\n", "")
        return f"{output}"


if __name__ == '__main__':
    name = f"akoksal/LongForm-OPT-2.7B"
    chatter = LongForm(name, "cuda:0", 1024)
    print(chatter.get_response("What is a Chatbot?"))