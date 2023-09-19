import sys
import requests

class ServerMetrics:
    def __init__(self, id, control_server_url):
        self.id = int(id)
        self.control_server_url = control_server_url
        
        self.batch_capacity = None
        self.total_prompt_tokens = 0.0
        self.avg_prompt_tokens = None #needs to be set by a start_req call
        self.overloaded = False

        self.num_requests_recieved = 0
        self.num_requests_finished = 0
        self.num_requests_working = 0
        self.num_tokens_working = 0
        self.curr_queue_time = 0.0
        self.curr_tokens_per_second = 0.0

    def report_batch_capacity(self, json_data):
        # self.batch_capacity = min(json_data["max_batch_prefill_tokens"], json_data["max_batch_tokens"])
        self.batch_capacity = json_data["max_batch_tokens"]
    
    def send_data(self, data):
        print(f'[server_metrics] sending data to url: {self.control_server_url}, data: {data}')
        # response = requests.post(self.control_server_url, json = data)
        # print(f"[server_metrics] Notification sent. Response: {response.status_code}")
        sys.stdout.flush()
    
    def fill_data(self, data):
        data["num_requests_recieved"] = self.num_requests_recieved
        data["num_requests_finished"] = self.num_requests_finished
        data["num_requests_working"] = self.num_requests_working
        data["num_tokens_working"] = self.num_tokens_working
        data["curr_queue_time"] = self.curr_queue_time
        data["curr_tokens_per_second"] = self.curr_tokens_per_second
        data["overloaded"] = self.overloaded

    #calculate "work ratio" in terms of tokens and report this when a new request starts, and when a request finishes
    def calc_work_ratio(self):
        if self.batch_capacity is not None:
            return self.num_tokens_working / self.batch_capacity
    
    def start_req(self, text_prompt, parameters):
        self.num_requests_recieved += 1
        self.num_requests_working += 1

        num_prompt_tokens = len(text_prompt.split()) #estimate, and could switch to faster option if necessary
        self.total_prompt_tokens += num_prompt_tokens
        self.avg_prompt_tokens = self.total_prompt_tokens / self.num_requests_recieved
        self.num_tokens_working += (self.avg_prompt_tokens + parameters["max_new_tokens"]) 
        work_ratio = self.calc_work_ratio()

        data = {"id" : self.id, "message" : "started req", "busy_ratio" : work_ratio}
        self.fill_data(data)
        self.send_data(data)
    
    def finish_req(self, log_data):
        self.curr_queue_time = log_data["queue_time"]
        self.num_requests_finished += 1
        self.num_requests_working -= 1

        tokens_per_second = 1 / log_data["time_per_token"]
        self.curr_tokens_per_second = tokens_per_second #could use a moving average system
        tokens_generated = int(log_data["inference_time"] * tokens_per_second)
        print(log_data)
        print(f"tokens_generated: {tokens_generated}")
        self.num_tokens_working -= (tokens_generated + self.avg_prompt_tokens)
        work_ratio = self.calc_work_ratio()

        if (log_data["queue_time"] > log_data["inference_time"]):
            self.overloaded = True
        else:
            self.overloaded = False

        data = {"id" : self.id, "message" : "finished req", "busy_ratio" : work_ratio}
        self.fill_data(data)
        self.send_data(data)









