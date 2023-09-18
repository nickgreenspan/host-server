class ServerMetrics:
    def __init__(self):
        self.num_requests_recieved = 0
        self.num_requests_finished = 0
        self.num_requests_working = 0
        self.num_tokens_working = 0


    def start_req(self):
        self.num_requests_recieved += 1
        self.num_requests_working += 1
    
    def report_req_done(self, data):
        print(data)





