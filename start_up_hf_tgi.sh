source /root/host-server/kill_model_hf_tgi.sh
echo "killed model"
export REPORT_ADDR="test/go"
source /root/host-server/start_model_hf_tgi.sh
echo "started model"