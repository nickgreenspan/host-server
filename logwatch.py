import sys
import re
import requests
import argparse
import json

def extract_token_details(log_line):
    tokens_per_second_pattern = re.compile(r'Avg generation throughput: (\d+\.\d+) tokens/s')
    tokens_per_second_match = tokens_per_second_pattern.search(log_line)
    tokens_per_second = float(tokens_per_second_match.group(1)) if tokens_per_second_match else None
    return tokens_per_second

#Can add pending too
def extract_running_details(log_line):
    running_pattern = re.compile(r'Running: (\d+) reqs')
    running_match = running_pattern.search(log_line)
    num_running = int(running_match.group(1)) if running_match else None
    return num_running

def notify_control_server(line, data_dict, control_server_url):
    data = json.loads(data_dict)

    if ("Avg generation throughput:" in line):
        tokens_per_second = extract_token_details(line)
        data["tokens/s"] = tokens_per_second

    if "Running:" in line:
        num_running = extract_running_details(line)
        data["num_running"] = num_running

    if "GPU blocks" in line:
        data["loaded"] = True

    print(f'sending data to url: {control_server_url}, data: {data}')
    response = requests.post(control_server_url, json = data)
    print(f"Notification sent. Response: {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description='Monitor a log file for a specific pattern and notify a control server when the pattern is matched.')
    parser.add_argument('--control_server_url', type=str, help='URL of the control server to notify.')
    parser.add_argument('--patterns', nargs='+', type=str, help='Regex patterns to search for in the log.')
    parser.add_argument('--data_dict', type=str)

    args = parser.parse_args()

    print(f"watching for patterns: {args.patterns}")
    for line in sys.stdin:
        print(line)
        for pattern in args.patterns:
            if re.search(pattern, line):
                notify_control_server(line.strip(), args.data_dict, args.control_server_url)
                break
    print("done iterating through stdin")

if __name__ == "__main__":
    print("starting")
    main()
