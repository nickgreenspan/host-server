from queue import Queue
from vllm import LLMEngine

class StreamingVLLMEngine:
    def __init__(self, engine_args):
        self.prompt_queue = Queue()
        self.engine = LLMEngine.from_engine_args(engine_args)
        self.req_map = {}

    def run(self):
        request_id = 0
        while True:
            while not (self.prompt_queue.empty()):
                (prompt, sampling_params, msg_queue, event) = self.prompt_queue.get()
                self.req_map[str(request_id)] = (msg_queue, 0, event)
                self.engine.add_request(str(request_id), prompt, sampling_params)
                request_id += 1

            request_outputs = self.engine.step()
            for req_output in request_outputs:
                id = req_output.request_id
                msg_queue, txt_len, event = self.req_map[id]
                txt_output = req_output.outputs[-1]
                if req_output.finished:
                    event.set()
                if len(txt_output) > txt_len:
                    msg_queue.put(txt_output[txt_len:])
                    txt_len = len(txt_output)
                if req_output.finished:
                    del self.req_map[id]
                else:
                    self.req_map[id] = (msg_queue, txt_len)






