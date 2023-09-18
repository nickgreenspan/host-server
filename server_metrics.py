import sys

class ServerMetrics:
    def __init__(self):
        self.num_requests_recieved = 0
        self.num_requests_finished = 0
        self.num_requests_working = 0
        self.num_tokens_working = 0
        self.curr_queue_time = 0.0

        self.tokens_per_second = 0.0


    def start_req(self, text_prompt, parameters):
        self.num_requests_recieved += 1
        self.num_requests_working += 1

        self.num_tokens_working += (len(text_prompt.split()) + parameters["max_new_tokens"] // 2) #estimate, and could switch to faster option if necessary 
    
    def report_req_done(self, data):
        print(data)
        sys.stdout.flush()

        if "loaded" in data.keys() or "max_batch_capacity" in data.keys():
            return
        
        self.curr_queue_time = data["queue_time"]
        self.num_requests_finished += 1
        self.num_requests_working -= 1

        tokens_per_second = 1 / data["time_per_token"]
        self.num_tokens_working -= int(data["inference_time"] * tokens_per_second)

        #calculate "work ratio" and report this when a new request starts, and when a request finishes







