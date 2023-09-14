#!/bin/bash

if [ -z "$SERVER_DIR"]
then
    current_cwd=$(pwd)
    export SERVER_DIR="$current_cwd"
fi

AUTH_CMD="$SERVER_DIR/auth_server_hf_tgi.py" 
AUTH_PID=$(ps aux | grep "$AUTH_CMD" | grep -v grep | awk '{print $2}')

while ! [ -z "$AUTH_PID" ]
do
    echo "Killing process $AUTH_PID running: $AUTH_CMD"
    kill "$AUTH_PID"
    sleep 2
    AUTH_PID=$(ps aux | grep "$AUTH_CMD" | grep -v grep | awk '{print $2}')
done

python3 $SERVER_DIR/auth_server_hf_tgi.py > $SERVER_DIR/auth.log 2>&1 &
echo "started auth server"