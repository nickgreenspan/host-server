from vllm_model import VLLmModel

model_path = "/src/models/meta-llama_Llama-2-13b-hf"
model = VLLmModel(model_name=model_path)

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]

outputs = model.generate(prompts * 4)
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")