from flask import Flask, Response, request, abort
import os
import secrets
import requests
import logging
import time

app = Flask(__name__)

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

mtoken = os.environ['MASTER_TOKEN']
HF_SERVER = '127.0.0.1:5001'
BATCH_SIZE = 1000
curr_tokens = set()

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
    for _ in range(BATCH_SIZE):
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

@app.route('/connect', methods=['POST'])
def auth():
    global mtoken, curr_tokens, tgi_client
    token = request.json['token']
    if token in curr_tokens:
        curr_tokens.remove(token)
    elif token != mtoken:
        abort(401)

    return Response(hf_tgi_wrapper(request.json['inputs'], request.json["parameters"]))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, threaded=True)