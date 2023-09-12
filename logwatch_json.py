import sys
import re
import requests
import argparse
import json

def extract(line_json, pattern_str, pattern_expression, data):
    match = pattern_expression.search(log_line)
    if match:
        value = float(match.group(1))
        data[pattern_str] = value
        return True
    
    return False

def forward_server_data(line_json, extract_pattern_dict, data_dict, control_server_url):
    data = json.loads(data_dict)

    found = False
    for pattern_str, pattern_expression in extract_pattern_dict.items():
        found |= extract(line, pattern_str, pattern_expression, data)

    if found:
        print(f'sending data to url: {control_server_url}, data: {data}')
        response = requests.post(control_server_url, json = data)
        # print(f"Notification sent. Response: {response.status_code}")
        print(f"Notification sent.") #response.status_code

def notify_server_ready(data_dict, control_server_url):
    data = json.loads(data_dict)
    data["loaded"] = True

    print(f'sending data to url: {control_server_url}, data: {data}')
    # response = requests.post(control_server_url, json = data)
    print(f"Notification sent.") #response.status_code


def main():
    parser = argparse.ArgumentParser(description='Monitor a log file for a specific pattern and notify a control server when the pattern is matched.')
    parser.add_argument('--control_server_url', type=str, help='URL of the control server to notify.')
    # parser.add_argument('--patterns', nargs='+', type=str, help='Regex patterns to search for in the log.')
    parser.add_argument('--backend', type=str)
    parser.add_argument('--data_dict', type=str)

    args = parser.parse_args()

    print("[logwatch] starting compiling")
 
    # if args.backend == "hf_tgi":
    ready_pattern = re.compile(r"Connected") # INFO text_generation_router: router/src/main\.rs:247: 
    extract_pattern_dict = {"inference_time": re.compile(r'inference_time="(\d+\.\d+)s"'), "queue_time" : re.compile(r'queue_time="(\d+\.\d+)ms"'), "time_per_token" : re.compile(r'time_per_token="(\d+\.\d+)ms"')}

    print("[logwatch] ready and waiting for input")
    for line in sys.stdin:
        line_json = json.loads(line)
        if line_json["message"] == "Connected" and line_json["target"] == "text_generation_router":
            notify_server_ready(args.data_dict, args.control_server_url)
        elif line_json["message"] == "Success" and line_json["target"] == "text_generation_router::server":
            forward_server_data(line_json, extract_pattern_dict, args.data_dict, args.control_server_url)


if __name__ == "__main__":
    main()
