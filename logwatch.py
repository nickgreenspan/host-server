import sys
import re
import requests
import argparse
import json


import re

def extract_token_details(log_line):
    # Regular expression to match tokens/s and total tokens
    tokens_per_second_pattern = re.compile(r'(\d+\.\d+) tokens/s')
    total_tokens_pattern = re.compile(r'(\d+) tokens,')

    # Find matches using the patterns
    tokens_per_second_match = tokens_per_second_pattern.search(log_line)
    total_tokens_match = total_tokens_pattern.search(log_line)

    # Extract values from the matches if found
    tokens_per_second = float(tokens_per_second_match.group(1)) if tokens_per_second_match else None
    total_tokens = int(total_tokens_match.group(1)) if total_tokens_match else None

    return tokens_per_second, total_tokens

def extract_seconds(log_line):
    # Regular expression pattern to match the number of seconds
    seconds_pattern = re.compile(r'in (\d+\.\d+) seconds\.')

    # Find the match using the pattern
    match = seconds_pattern.search(log_line)

    # Extract and return the value if found
    if match:
        return float(match.group(1))
    return None

def notify_control_server(line, message, control_server_url):
    data = json.loads(message)
    data["line"] = line
    if ("token/s" in line):
        tokens_per_second, total_tokens = extract_token_details(line)
        data["token/s"] = tokens_per_second
        data["tokens"]  = total_tokens
    # if ("Loaded the model" in line):
    #     data["loadtime"] = extract_seconds(line)
    if "GPU blocks" in line:
        data["loaded"] = True

    print(f'sending data, model loaded: {data["loaded"]}')
    response = requests.post(control_server_url, json = data)
    print(f"Notification sent. Response: {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description='Monitor a log file for a specific pattern and notify a control server when the pattern is matched.')
    parser.add_argument('control_server_url', type=str, help='URL of the control server to notify.')
    parser.add_argument('pattern', type=str, help='Regex pattern to search for in the log.')
    parser.add_argument('message', type=str, help='Extra  message')

    args = parser.parse_args()

    for line in sys.stdin:
        if re.search(args.pattern, line):
            notify_control_server(line.strip(), args.message, args.control_server_url)

if __name__ == "__main__":
    main()
