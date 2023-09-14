import sys
import re
import requests
import argparse
import json

def format_metric_value(metric_str):
    if metric_str[-2:] == "ms":
        return (float(metric_str[:-2]) / 10.0e3)

    elif ord(metric_str[-2]) == 181: #mu
        return (float(metric_str[:-2]) / 10.0e6)

    elif metric_str[-1:] == "s":
        return (float(metric_str[:-1]))

    else:
        return metric_str

def forward_server_batch_capacity(batch_pattern, batch_info_line, data_dict, control_server_url):
    match = batch_pattern.search(batch_info_line)
    if match:
        value = int(match.group(1))
        data = json.loads(data_dict)
        data["max batch capacity"] = value

        print(f'sending data to url: {control_server_url}, data: {data}')
        response = requests.post(control_server_url, json = data)
        print(f"Notification sent. Response: {response.status_code}")
        sys.stdout.flush()

def forward_server_data(line_metrics, metric_names, data_dict, control_server_url):
    data = json.loads(data_dict)

    found = False
   
    for metric_name in metric_names:
        if metric_name in line_metrics.keys():
            data[metric_name] = format_metric_value(line_metrics[metric_name])
            found = True

    if found:
        print(f'sending data to url: {control_server_url}, data: {data}')
        response = requests.post(control_server_url, json = data)
        print(f"Notification sent. Response: {response.status_code}")
        sys.stdout.flush()

def notify_server_ready(data_dict, control_server_url):
    data = json.loads(data_dict)
    data["loaded"] = True

    print(f'sending data to url: {control_server_url}, data: {data}')
    response = requests.post(control_server_url, json = data)
    print(f"Notification sent. Response: {response.status_code}")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description='Monitor a log file for a specific pattern and notify a control server when the pattern is matched.')
    parser.add_argument('--control_server_url', type=str, help='URL of the control server to notify.')
    parser.add_argument('--backend', type=str)
    parser.add_argument('--data_dict', type=str)

    args = parser.parse_args()

    metric_names = ["time_per_token", "inference_time", "queue_time", "validation_time"]
    batch_pattern = re.compile(r'Setting max batch total tokens to (\d+)')

    print("[logwatch] ready and waiting for input\n")
    for line in sys.stdin:
        line_json = json.loads(line)
        if "message" in line_json.keys():
            if line_json["message"] == "Connected" and line_json["target"] == "text_generation_router":
                notify_server_ready(args.data_dict, args.control_server_url)
            elif line_json["message"] == "Success" and line_json["target"] == "text_generation_router::server":
                forward_server_data(line_json["span"], metric_names, args.data_dict, args.control_server_url)
            else:
                forward_server_batch_capacity(batch_pattern, line_json["message"], args.data_dict, args.control_server_url)


if __name__ == "__main__":
    main()
