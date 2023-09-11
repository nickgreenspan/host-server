#!/bin/bash

# Define the target command
TARGET_CMD="python3 /src/host-server/auth_server_streaming.py"

# Get the process IDs (PIDs) of processes matching the target command
PIDS=$(ps aux | grep "$TARGET_CMD" | grep -v grep | awk '{print $2}')

# Check if any processes were found
while ! [ -z "$PIDS" ]
do
  # Loop through the PIDs and kill each process
  for PID in $PIDS; do
    echo "Killing process $PID running: $TARGET_CMD"
    kill "$PID"
  done
  sleep 2
  PIDS=$(ps aux | grep "$TARGET_CMD" | grep -v grep | awk '{print $2}')
done
