from exllama.model import ExLlama, ExLlamaCache, ExLlamaConfig
from exllama.tokenizer import ExLlamaTokenizer
from exllama.generator import ExLlamaGenerator
import glob
import os

class ExllamaModel:
    def __init__(self, model_dir, batch_size):
        self.model_dir = model_dir
        tokenizer_path = os.path.join(model_dir, "tokenizer.model")
        model_config_path = os.path.join(model_dir, "config.json")
        st_pattern = os.path.join(model_dir, "*.safetensors")
        model_path = glob.glob(st_pattern)[0]

        config = ExLlamaConfig(model_config_path)
        config.model_path = model_path
        model = ExLlama(config)
        tokenizer = ExLlamaTokenizer(tokenizer_path)
        cache = ExLlamaCache(self.model, batch_size = batch_size)

        self.generator = ExLlamaGenerator(model, tokenizer, cache)
        self.configure_generator(self.generator)

        self.max_new_tokens = 200


    def configure_generator(self, generator):
        generator.disallow_tokens([self.tokenizer.eos_token_id])
        generator.settings.token_repetition_penalty_max = 1.2
        generator.settings.temperature = 0.95
        generator.settings.top_p = 0.65
        generator.settings.top_k = 100
        generator.settings.typical = 0.5

    def generate(self, prompts):
        return self.generator.generate_simple(prompts, max_new_tokens = self.max_new_tokens)


