from flask import Flask, request
from vllm import EngineArgs, SamplingParams
from vllm_engine import VLLMEngine
from threading import Thread, Event
import logging

TIMEOUT = 100

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

model_path = "/src/models/meta-llama_Llama-2-13b-hf"
tokenizer = "hf-internal-testing/llama-tokenizer"

engine = None

engine_args = EngineArgs(model=model_path, tokenizer=tokenizer)
engine = VLLMEngine(engine_args=engine_args)
engine_thread = Thread(target=engine.run)
engine_thread.start()

@app.route('/generate', methods=['POST'])
def generate():
    global engine
    prompt = request.json['prompt']
    params = SamplingParams(temperature=0.8, top_p=0.95, frequency_penalty=0.1)
    event = Event()
    ret_list = []
    engine.prompt_queue.put((prompt, params, event, ret_list))
    event.wait(timeout=100)
    if event.is_set():
        out = ret_list.pop().pop()
        return {"response" : out.text, "error" : None, "num_tokens" : len(out.token_ids)}
    else:
        return {"response" : None, "error" : "timeout", "num_tokens" : None}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)