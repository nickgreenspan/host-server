#!/bin/bash
export PATH="/opt/conda/bin:$PATH"
export MASTER_TOKEN="mtoken" #hack for this instance
export REPORT_ADDR=$1
source /root/host-server/start_watch.sh
source /root/host-server/launch_model.sh
source /root/host-server/start_auth.sh