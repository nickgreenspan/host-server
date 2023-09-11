touch infer.log
tail -Fn0 infer.log | python3 /src/host-server/logwatch.py --control_server_url $REPORT_ADDR --patterns 'blocks' 'tokens/s' 'Running' --data_dict '{"id":'$CONTAINER_ID'}' &
python3 /src/host-server/auth_server_streaming.py > infer.log 2>&1 &