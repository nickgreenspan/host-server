#!/bin/bash

export SERVER_DIR="/usr/src/host-server" #want a better system, but necessary for ssh

export PATH="/opt/conda/bin:$PATH"
export MASTER_TOKEN="mtoken" #hack for this instance
export REPORT_ADDR=$1
echo $REPORT_ADDR

source "$SERVER_DIR/start_watch.sh"
source "$SERVER_DIR/launch_model.sh"
source "$SERVER_DIR/start_auth.sh"