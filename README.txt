
README for huggingface TGI serving code backend

The server consists of three main parts: the log watcher, the huggingface text-generation-launcher, and the auth server.

The log watch code is in logwatch_json.py, and it looks through the output of the huggingface TGI model, and sends relevant reports to the autoscaler server as it
recieves the information in the logs.

The huggingface text-generation-launcher is built in as part of the huggingface TGI image, and it launches the code the serves the model requests.

The auth server code is in auth_server_hf_tgi.py and it is what is responsible for serving requests from the autoscaler server for authentication tokens, and from clients
to generate output from a model. The two client facing endpoints are "/generate" and "/generate_stream", which match the names of the huggingface TGI endpoints, and are responsible
for calling the huggingface model server, and forwarding the outputs back to the client. 

relevant parameters:
- auth_server_hf_tgi:NUM_AUTH_TOKENS
    determines the number of auth tokens that are sent to the loadbalancer, which are then used to verify
    model prompt requests that are sent to this model server, will depend on how many requests the loadbalancer
    is handling per unit time.
- auth_server_hf_tgi:HF_SERVER
    The local address that the huggingface model is listening on

To launch all three components of the server, run ./start_server.sh REPORT_ADDR MODEL_NAME AUTH_PORT

REPORT_ADDR = address of the endpoint on the autoscaler that the log watcher will report to
MODEL_NAME = the name of the model to load with the huggingface text-generation-launcher
AUTH_PORT = the internal port that the auth server listens on for requests from the autoscaler server and clients

To kill all thre components of the server, run ./kill_server.sh