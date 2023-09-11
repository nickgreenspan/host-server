source /venv/bin/activate
source /src/host-server/kill_model.sh
echo "killed model"
export REPORT_ADDR=$1
source /src/host-server/start_model.sh
echo "started model"