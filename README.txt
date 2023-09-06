relevant parameters:
- auth_server_streaming:BATCH_SIZE
    determines the number of auth tokens that are sent to the loadbalancer, which are then used to verify model prompt requests that are sent to this model server, will depend on how many requests the loadbalancer is handling per unit time
- streaming_server_auth:CHECK_QUEUE_SLEEP
    how often the model server checks for new auth tokens that have been produced by the auth server, will depend on how frequently these are being generated
- streaming_server_auth:MSG_END
    string that model server looks for in client request to signal end of authentication token portion and end of prompt portion of request
- streaming_server_auth:MAX_TOKENS
    max number of tokens for the vllm model to generate in response to prompt