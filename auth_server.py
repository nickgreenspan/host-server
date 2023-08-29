from flask import Flask, request, abort
import os
import secrets
import requests
import time
import logging

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

mtoken = os.environ['MTOKEN']
OOBA_SERVER = '127.0.0.1:5001'
BATCH_SIZE = 1000
curr_tokens = set()

@app.route('/tokens', methods=['GET'])
def get_tokens():
    global mtoken, curr_tokens
    if request.json['mtoken'] != mtoken:
        abort(401)
    t1 = time.time()
    new_tokens = gen_tokens()
    t2 = time.time()
    curr_tokens |= set(new_tokens)
    return {"tokens" : new_tokens}

def gen_tokens():
    token_batch = []
    for i in range(BATCH_SIZE):
        token = secrets.token_hex(32)
        token_batch.append(token)
    return token_batch

@app.route('/auth', methods=['POST'])
def auth():
    global mtoken, curr_tokens
    token = request.json['token']
    if token in curr_tokens:
        curr_tokens.remove(token)
    elif token != mtoken:
        abort(401)

    URI = f'http://{OOBA_SERVER}/generate'
    response = requests.post(URI, json=request.json['model'])
    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
