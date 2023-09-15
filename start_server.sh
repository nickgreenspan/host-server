#!/bin/bash

export SERVER_DIR="/usr/src/host-server" #will be /home/workspace/host-server on new instances

export PATH="/opt/conda/bin:$PATH"
export REPORT_ADDR=$1
echo $REPORT_ADDR
export MODEL_NAME=$2
echo $MODEL_NAME
export AUTH_PORT=$3
echo $AUTH_PORT

source "$SERVER_DIR/start_watch.sh"
source "$SERVER_DIR/launch_model.sh"
source "$SERVER_DIR/start_auth.sh"