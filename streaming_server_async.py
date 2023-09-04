import os
from vllm import AsyncLLMEngine, EngineArgs, SamplingParams
import uuid

prompt_end  = '?'

num_gpus = int(os.environ["NUM_GPUS"])
model_path = os.environ["MODEL_PATH"]
engine_args = EngineArgs(model=model_path, tensor_parallel_size=num_gpus)
engine = AsyncLLMEngine(engine_args=engine_args)

async def generate(websocket):
    prompt = ""
    async for message in websocket:
        prompt += message
        if prompt_end in message:
            break

    params = SamplingParams(temperature=0.8, top_p=0.95, frequency_penalty=0.1, max_tokens=50)
    generator = engine.generate(prompt, params, request_id=uuid.uuid4())
    txt_len = 0
    async for result in generator:
        txt = result.outputs[-1].text
        await websocket.send(txt[txt_len:])
        txt_len = len(txt)
