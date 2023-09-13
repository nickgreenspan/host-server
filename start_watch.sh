#!/bin/bash

WATCH_CMD="python3 /root/host-server/logwatch_json.py"
WATCH_PID=$(ps aux | grep "$WATCH_CMD" | grep -v grep | awk '{print $2}')

while ! [ -z "$WATCH_PID" ]
do
    echo "Killing process $WATCH_PID running: $WATCH_CMD"
    kill "$WATCH_PID"
    sleep 2
    WATCH_PID=$(ps aux | grep "$WATCH_CMD" | grep -v grep | awk '{print $2}')
done

touch /root/host-server/infer.log
tail -f -n +1 /root/host-server/infer.log | python3 /root/host-server/logwatch_json.py --control_server_url $REPORT_ADDR --backend 'hf_tgi' --data_dict '{"id":'$CONTAINER_ID'}' > /root/host-server/watch.log 2>&1 &
echo "started logwatch"