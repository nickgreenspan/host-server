import asyncio
import websockets
from vllm import EngineArgs, SamplingParams
from threading import Thread, Event
from queue import Queue
import os

from vllm_engine_streaming import StreamingVLLMEngine

num_gpus = int(os.environ["NUM_GPUS"])
model_path = os.environ["MODEL_PATH"]

engine_args = EngineArgs(model=model_path, tensor_parallel_size=num_gpus)
engine = StreamingVLLMEngine(engine_args=engine_args)
engine_thread = Thread(target=engine.run)
engine_thread.start()

prompt_end  = '?'

async def update_tokens():
    async with aiofiles.open('filename', mode='r') as f:
        contents = await f.read()


async def generate(websocket):
    prompt = ""
    async for message in websocket:
        prompt += message
        if prompt_end in message:
            break

    msg_queue = Queue()
    event = Event()
    params = SamplingParams(temperature=0.8, top_p=0.95, frequency_penalty=0.1, max_tokens=50)
    engine.prompt_queue.put((prompt, params, msg_queue, event))
    while not event.is_set():
        while msg_queue.empty() and not event.is_set():
            await asyncio.sleep(1)
        while not(msg_queue.empty()):
            await websocket.send(msg_queue.get())

async def model_main():
    async with websockets.serve(generate, '127.0.0.1', 5001):
        await asyncio.Future()  # run forever

async def tokens_main(queue):

    await update_tokens(queue)

def start_server():
    asyncio.run(model_main())