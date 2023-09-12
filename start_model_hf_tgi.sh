touch infer.log
tail -Fn0 infer.log | python3 /root/host-server/logwatch.py --control_server_url $REPORT_ADDR --backend 'hf_tgi' --data_dict '{"id":'$CONTAINER_ID'}' > watch.log 2>&1 &
echo "started logwatch"
text-generation-launcher --model-id meta-llama/Llama-2-70b-chat-hf --json_output True > infer.log 2>&1 &