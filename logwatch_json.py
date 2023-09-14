import sys
import re
import requests
import argparse
import json
import time

def format_metric_value(metric_str):
    if metric_str[-2:] == "ms":
        return (float(metric_str[:-2]) / 10.0e3)

    elif ord(metric_str[-2]) == 181: #mu
        return (float(metric_str[:-2]) / 10.0e6)

    elif metric_str[-1:] == "s":
        return (float(metric_str[:-1]))

    else:
        return metric_str

class LogWatch:
    def __init__(self, data_dict, control_server_url, metric_names, batch_pattern):
        self.data_dict = data_dict
        self.control_server_url = control_server_url
        self.start_time = time.time() #this could be made more precise
        self.metric_names = metric_names
        self.batch_pattern = batch_pattern

    def send_data(self, data):
        print(f'sending data to url: {self.control_server_url}, data: {data}')
        response = requests.post(self.control_server_url, json = data)
        print(f"Notification sent. Response: {response.status_code}")
        sys.stdout.flush()

    def forward_server_batch_capacity(self, batch_info_line):
        match = self.batch_pattern.search(batch_info_line)
        if match:
            value = int(match.group(1))
            data = json.loads(self.data_dict)
            data["max batch capacity"] = value
            self.send_data(data)

    def forward_server_data(self, line_metrics):
        data = json.loads(self.data_dict)

        found = False 
        for metric_name in self.metric_names:
            if metric_name in line_metrics.keys():
                data[metric_name] = format_metric_value(line_metrics[metric_name])
                found = True

        if found:
            self.send_data(data)

    def notify_server_ready(self):
        end_time = time.time()
        data = json.loads(self.data_dict)
        data["loaded"] = True
        data["load_time"] = end_time - self.start_time

        self.send_data(data)

def main():
    parser = argparse.ArgumentParser(description='Monitor a log file for a specific pattern and notify a control server when the pattern is matched.')
    parser.add_argument('--control_server_url', type=str, help='URL of the control server to notify.')
    parser.add_argument('--backend', type=str)
    parser.add_argument('--data_dict', type=str)

    args = parser.parse_args()

    metric_names = ["time_per_token", "inference_time", "queue_time", "validation_time"]
    batch_pattern = re.compile(r'Setting max batch total tokens to (\d+)')

    watch = LogWatch(args.data_dict, args.control_server_url, metric_names, batch_pattern)

    print("[logwatch] ready and waiting for input\n")
    for line in sys.stdin:
        line_json = json.loads(line)
        if "message" in line_json.keys():
            if line_json["message"] == "Connected" and line_json["target"] == "text_generation_router":
                watch.notify_server_ready()
            elif line_json["message"] == "Success" and line_json["target"] == "text_generation_router::server":
                watch.forward_server_data(line_json["span"])
            else:
                watch.forward_server_batch_capacity(line_json["message"])


if __name__ == "__main__":
    main()
