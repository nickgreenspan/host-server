from exllama_model import ExllamaModel
import time

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]
many_prompts = prompts * 2


model_dir = "/src/models/TheBloke_Llama-2-13B-chat-GPTQ_gptq-4bit-32g-actorder_True"
model = ExllamaModel(model_dir, batch_size=8)

out = model.generate(many_prompts)
print(out)






