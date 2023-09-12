#!/bin/bash

# Define the target command
WATCH_CMD="python3 /root/host-server/logwatch.py"
MODEL_CMD="text-generation-launcher"

# Get the process IDs (PIDs) of processes matching the target command
PIDS1=$(ps aux | grep "$WATCH_CMD" | grep -v grep | awk '{print $2}')
PIDS2=$(ps aux | grep "$MODEL_CMD" | grep -v grep | awk '{print $2}')

# Check if any processes were found
while ! ([ -z "$PIDS1" ] && [ -z "$PIDS2" ])
do
  # Loop through the PIDs and kill each process
  for PID in $PIDS1; do
    echo "Killing process $PID running: $WATCH_CMD"
    kill "$PID"
  done
  for PID in $PIDS2; do
    echo "Killing process $PID running: $MODEL_CMD"
    kill "$PID"
  done
  sleep 2
  PIDS1=$(ps aux | grep "$WATCH_CMD" | grep -v grep | awk '{print $2}')
  PIDS2=$(ps aux | grep "$MODEL_CMD" | grep -v grep | awk '{print $2}')
done
