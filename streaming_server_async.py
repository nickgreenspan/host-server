import os
import asyncio
import websockets
import threading
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
import uuid

prompt_end  = '?'

num_gpus = int(os.environ["NUM_GPUS"])
model_path = os.environ["MODEL_PATH"]

engine_args = AsyncEngineArgs(model=model_path, tensor_parallel_size=num_gpus, worker_use_ray=True, engine_use_ray=True, disable_log_requests=True)
engine = AsyncLLMEngine.from_engine_args(engine_args=engine_args)

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

async def main():
    async with websockets.serve(generate, '0.0.0.0', 5000):
        await asyncio.Future()  # run forever

asyncio.run(main())
