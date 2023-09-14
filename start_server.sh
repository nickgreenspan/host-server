#!/bin/bash

if [ -z "$SERVER_DIR" ]
then
    current_cwd=$(pwd)
    export SERVER_DIR="$current_cwd"
fi

export PATH="/opt/conda/bin:$PATH"
export MASTER_TOKEN="mtoken" #hack for this instance
export REPORT_ADDR=$1

source "$SERVER_DIR/start_watch.sh"
source "$SERVER_DIR/launch_model.sh"
source "$SERVER_DIR/start_auth.sh"