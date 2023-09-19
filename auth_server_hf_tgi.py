from flask import Flask, Response, request, abort
import os
import secrets
import requests
import logging
import time
import sys
import argparse

from server_metrics import ServerMetrics

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description='Flask server to serve client requests and requests from autoscaler for tokens')
parser.add_argument('--control_server_url', type=str, help='URL of the control server to notify.')
args = parser.parse_args()

mtoken = os.environ['MASTER_TOKEN']
HF_SERVER = '127.0.0.1:5001'
NUM_AUTH_TOKENS = 1000
curr_tokens = set()

metrics = ServerMetrics(os.environ['CONTAINER_ID'], args.control_server_url)

@app.route('/tokens', methods=['GET'])
def get_tokens():
    global mtoken, curr_tokens
    if request.json['mtoken'] != mtoken:
        abort(401)
    new_tokens = gen_tokens()
    curr_tokens |= set(new_tokens)
    return {"tokens" : new_tokens}

def gen_tokens():
    token_batch = []
    for _ in range(NUM_AUTH_TOKENS):
        token = secrets.token_hex(32)
        token_batch.append(token)
    return token_batch

def hf_tgi_wrapper(inputs, parameters):
    hf_prompt = {"inputs" : inputs, "parameters" : parameters}
    response = requests.post(f"http://{HF_SERVER}/generate_stream", json=hf_prompt, stream=True)
    if response.status_code == 200:
        for byte_payload in response.iter_lines():
            yield byte_payload
            yield "\n"

@app.route('/generate', methods=['POST'])
def generate():
    global mtoken, curr_tokens, tgi_client, metrics
    token = request.json['token']
    if token in curr_tokens:
        curr_tokens.remove(token)
    elif token != mtoken:
        abort(401)

    print(request.headers.get('User-Agent'))
    metrics.start_req(request.json['inputs'], request.json["parameters"])

    hf_prompt = {"inputs" : request.json['inputs'], "parameters" : request.json["parameters"]}
    response = requests.post(f"http://{HF_SERVER}/generate", json=hf_prompt)
   
    if response.status_code == 200:
        return response.text
    else:
        return "Failed communication with model"
    

@app.route('/generate_stream', methods=['POST'])
def generate_stream():
    global mtoken, curr_tokens, tgi_client, metrics
    token = request.json['token']
    if token in curr_tokens:
        curr_tokens.remove(token)
    elif token != mtoken:
        abort(401)

    metrics.start_req(request.json['inputs'], request.json["parameters"])

    return Response(hf_tgi_wrapper(request.json['inputs'], request.json["parameters"]))


@app.route('/report_capacity', methods=['POST'])
def report_capacity():
    global metrtics
    metrics.report_batch_capacity(request.json)
    return "Reported capacity"

@app.route('/report_done', methods=['POST'])
def report_done():
    global metrics
    log_data = request.json
    metrics.finish_req(log_data)
    return "Updated Metrics"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, threaded=True)