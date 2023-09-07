
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


streaming parameters:
- auth_server_streaming:BATCH_SIZE
    determines the number of auth tokens that are sent to the loadbalancer, which are then used to verify model prompt requests that are sent to this model server, will depend on how many requests the loadbalancer is handling per unit time
- streaming_server_auth:CHECK_QUEUE_SLEEP
    how often the model server checks for new auth tokens that have been produced by the auth server, will depend on how frequently these are being generated
- streaming_server_auth:MSG_END
    string that model server looks for in client request to signal end of authentication token portion and end of prompt portion of request
- streaming_server_auth:MAX_TOKENS
    max number of tokens for the vllm model to generate in response to prompt