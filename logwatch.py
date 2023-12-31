import sys
import re
import requests
import argparse
import json

# def extract_token_details(log_line, data):
#     tokens_per_second_pattern = re.compile(r'Avg generation throughput: (\d+\.\d+) tokens/s')
#     tokens_per_second_match = tokens_per_second_pattern.search(log_line)
#     tokens_per_second = float(tokens_per_second_match.group(1)) if tokens_per_second_match else None
#     data["tokens/s"] = tokens_per_second

# #Can add pending too
# def extract_running_details(log_line, data):
#     running_pattern = re.compile(r'Running: (\d+) reqs')
#     running_match = running_pattern.search(log_line)
#     num_running = int(running_match.group(1)) if running_match else None
#     data["num_running"] = num_running

def extract(log_line, pattern_str, pattern_expression, data):
    match = pattern_expression.search(log_line)
    if match:
        value = float(match.group(1))
        data[pattern_str] = value
        return True
    
    return False

def forward_server_data(line, extract_pattern_dict, data_dict, control_server_url):
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
        if ready_pattern.search(line.strip()):
            notify_server_ready(args.data_dict, args.control_server_url)

        forward_server_data(line.strip(), extract_pattern_dict, args.data_dict, args.control_server_url)


if __name__ == "__main__":
    main()
