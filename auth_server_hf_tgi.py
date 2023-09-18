from flask import Flask, Response, request, abort
import os
import secrets
import requests
import logging
import time
import sys

from server_metrics import ServerMetrics

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)

mtoken = os.environ['MASTER_TOKEN']
HF_SERVER = '127.0.0.1:5001'
NUM_AUTH_TOKENS = 1000
curr_tokens = set()
metrics = ServerMetrics()

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

    metrics.start_req()

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

    metrics.start_req()

    return Response(hf_tgi_wrapper(request.json['inputs'], request.json["parameters"]))

@app.route('/report_done', methods=['POST'])
def report():
    global metrics
    data = request.json
    metrics.report_req_done(data)

    return "Updated Metrics"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, threaded=True)