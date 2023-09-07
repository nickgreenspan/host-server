
The "host-server" is the code that runs on the remote GPU instance to authenticate and serve client
prompt requests. There are two modes, "streaming", and "non-streaming". The "non-streaming" option
is implemented by the files auth_server.py and inference_server.py. The "streaming" option is implemented
by the files auth_server_streaming.py and inference_server_streaming.py. Note that the entrypoint for each
of these two options differs slightly, as auth_server.py and inference_server.py must be called separately,
but for "streaming", all you have to do is call "python auth_server_streaming.py", and inference_server_streaming
will be automatically called in a subprocess. Note that the output of inference_server.py or inference_server_streaming.py
should be piped into a file called infer.log, which is used by the autoscaler to detect when the model is
fully loaded on a server. Also note that for instances started using "create_instances" from autoscaler.py,
all of the above is done automatically.

One high level difference between the architecture of the "streaming" and "non-streaming" servers is that
both the auth_server and the inference_server are flask HTTP servers for the "non-streaming" case, and all
requests to the inference_server are first handled by the auth server for authentication, and then forwarded to
the inference_server, which is just running on a local address, and not directly accessable by clients.

For "streaming", only the auth_server is an http server, and the inference_server is listening on a websocket.
This websocket is at an externally available address, and it interacts directly with clients. To provide
authentication, this requires the auth_server to periodically send auth_tokens to the inference_server
through an interprocess queue, which the inference_server will then use to check against the token that
clients provide when they create a websocket connection to send a prompt to the model.

relevant parameters:
- auth_server(streaming):BATCH_SIZE
    determines the number of auth tokens that are sent to the loadbalancer, which are then used to verify
    model prompt requests that are sent to this model server, will depend on how many requests the loadbalancer
    is handling per unit time.
- inference_server:TIMEOUT
    how long the inference_server will wait for the model to generate a response to a client prompt.
- inference_server(streaming):MAX_TOKENS
    max number of tokens for the vllm model to generate in response to prompt.
- inference_server_streaming:CHECK_QUEUE_SLEEP
    how often the model server checks for new auth tokens that have been produced by the auth server,
    will depend on how frequently these are being generated.
- inference_server_streaming:MSG_END
    string that model server looks for in client request through websocket
    to signal end of authentication token portion and end of prompt portion of request.
