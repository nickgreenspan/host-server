from flask import Flask, request, abort
import os
import secrets
import requests
import logging
import multiprocessing

from streaming_server_auth import start_server

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

mtoken = os.environ['MASTER_TOKEN']
OOBA_SERVER = '127.0.0.1:5001'
BATCH_SIZE = 1000

token_queue = multiprocessing.Queue()
model_process = multiprocessing.Process(target=start_server, args=(token_queue))




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
    for i in range(BATCH_SIZE):
        token = secrets.token_hex(32)
        token_batch.append(token)
    return token_batch

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
