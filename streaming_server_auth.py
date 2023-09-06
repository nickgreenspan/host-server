import asyncio
import websockets
from vllm import EngineArgs, SamplingParams
from threading import Thread, Event
from queue import Queue
import os
import time

from vllm_engine_streaming import StreamingVLLMEngine

num_gpus = int(os.environ["NUM_GPUS"])
model_path = os.environ["MODEL_PATH"]
mtoken = os.environ['MASTER_TOKEN']

MSG_END = "$$$"
CHECK_QUEUE_SLEEP = 2
MAX_TOKENS = 50

curr_tokens = None
engine = None

async def generate(websocket):
    global curr_tokens, engine
    token = ""
    async for message in websocket:
        if MSG_END in message:
            break
        token += message

    if (token in curr_tokens):
        curr_tokens.remove(token)
    elif token != mtoken:
        await websocket.close()
        return

    prompt = ""
    async for message in websocket:
        if MSG_END in message:
            break
        prompt += message

    msg_queue = Queue()
    event = Event()
    params = SamplingParams(temperature=0.8, top_p=0.95, frequency_penalty=0.1, max_tokens=MAX_TOKENS)
    engine.prompt_queue.put((prompt, params, msg_queue, event))
    while not event.is_set():
        while msg_queue.empty() and not event.is_set():
            await asyncio.sleep(1)
        while not(msg_queue.empty()):
            await websocket.send(msg_queue.get())

async def serve_model():
    async with websockets.serve(generate, '0.0.0.0', 5005):
        await asyncio.Future()  # run forever

async def get_tokens(token_queue, token_event):
    global curr_tokens
    while True:
        await token_event.wait()
        while not(token_queue.empty()):
            curr_tokens.add(token_queue.get())
        token_event.clear()

async def main(token_queue, token_event):
    task1 = asyncio.create_task(serve_model())
    task2 = asyncio.create_task(get_tokens(token_queue, token_event))
    await task1
    await task2

def check_queue(token_queue, token_event):
    while True:
        if not(token_event.is_set()) and not(token_queue.empty()):
            token_event.set()
        time.sleep(CHECK_QUEUE_SLEEP)

def start_server(token_queue):
    global engine, curr_tokens
    curr_tokens = set()
    engine_args = EngineArgs(model=model_path, tensor_parallel_size=num_gpus)
    engine = StreamingVLLMEngine(engine_args=engine_args)
    engine_thread = Thread(target=engine.run)
    engine_thread.start()

    token_event = asyncio.Event()
    queue_check_thread = Thread(target=check_queue, args=(token_queue, token_event,))
    queue_check_thread.start()

    asyncio.run(main(token_queue, token_event))

