import sys
import requests

class ServerMetrics:
    def __init__(self, id, control_server_url):
        self.id = int(id)
        self.control_server_url = control_server_url
        
        self.num_requests_recieved = 0
        self.num_requests_finished = 0
        self.num_requests_working = 0
        self.num_tokens_working = 0
        self.curr_queue_time = 0.0
        self.tokens_per_second = 0.0

    def send_data(self, data):
        print(f'[server_metrics] sending data to url: {self.control_server_url}, data: {data}')
        response = requests.post(self.control_server_url, json = data)
        print(f"[server_metrics] Notification sent. Response: {response.status_code}")    
    
    def fill_data(self, data):
        data["num_requests_recieved"] = self.num_requests_recieved
        data["num_requests_finished"] = self.num_requests_finished
        data["num_requests_working"] = self.num_requests_working
        data["num_tokens_working"] = self.num_tokens_working
        data["curr_queue_time"] = self.curr_queue_time
        data["tokens_per_second"] = self.tokens_per_second

    
    def start_req(self, text_prompt, parameters):
        self.num_requests_recieved += 1
        self.num_requests_working += 1

        self.num_tokens_working += (len(text_prompt.split()) + parameters["max_new_tokens"] // 2) #estimate, and could switch to faster option if necessary
        data = {"id" : self.id, "message" : "started req"}
        self.fill_data(data)
        self.send_data(data)
    
    def finish_req(self, log_data):
        print(log_data)
        sys.stdout.flush()

        if "loaded" in log_data.keys() or "max_batch_capacity" in log_data.keys():
            return
        
        self.curr_queue_time = log_data["queue_time"]
        self.num_requests_finished += 1
        self.num_requests_working -= 1

        tokens_per_second = 1 / log_data["time_per_token"]
        self.num_tokens_working -= int(log_data["inference_time"] * tokens_per_second)

        #calculate "work ratio" and report this when a new request starts, and when a request finishes

        data = {"id" : self.id, "message" : "finished req"}
        self.fill_data(data)
        self.send_data(data)









