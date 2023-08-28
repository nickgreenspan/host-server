from vllm import LLM, SamplingParams

class VLLmModel:
    def __init__(self, model_name):
        self.params = SamplingParams(temperature=0.8, top_p=0.95)
        self.llm = LLM(model=model_name)

    def generate(self, prompts):
        return self.llm.generate(prompts, self.params)
