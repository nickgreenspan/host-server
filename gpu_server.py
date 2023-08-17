from threading import Thread
import subprocess
import argparse
import re
import json
import time

TIME_INTERVAL_SECONDS = 10

parser = argparse.ArgumentParser()
parser.add_argument('--id', help='Instance ID of this GPU server')
parser.add_argument('-a', '--address', help='Address of the serverless server')
args = parser.parse_args()


class Instance:
	def __init__(self, id, address):
		self.id = id
		self.serverless_address = address
		self.state = {"tps" : None, "state": "loading"} # "loading" || "ready" || "error"
		self.changed = False

		self.t = Thread(target=self.tick)
		self.t.start()

	def check_error(self):
		pass

	def check_ready(self):
		result = subprocess.run(["grep 'Starting API at http://0.0.0.0:5000/api' /app/onstart.log | tail -n 1"], capture_output=True)
		out = result.stdout
		if out is not None and "Starting API at http://0.0.0.0:5000/api" in out.decode('utf-8'):
			if self.state["state"] == "loading":
				self.state["state"] = "ready"
				self.changed = True

	def update_metrics(self):
		result = subprocess.run(["grep 'Output generated' /app/onstart.log | tail -n 1"], capture_output=True)
		out = result.stdout
		if out is not None:
			line = out.decode('utf-8')
			pattern = r"()\d+\.\d+(?=\stokens\/s)"
			match = re.search(pattern, line)
			if match is not None:
				tps = float(match.group())
				if tps != self.state["tps"]:
					self.state["tps"] = tps
					self.changed = True


	def log_state(self):
		with open("{self.id}_state.json", 'w') as file:
			json.dump(self.state, file)

	def send_state(self):
		result = subprocess.run(["scp {self.id}_state.json {self.serverless_address}:instance_info/"])

	def tick(self):
		while True:
			self.check_error()
			if self.state["state"] == "loading":
				self.check_ready()
			if self.state["state"] == "ready":
				self.update_metrics()
			if self.changed:
				self.log_state()
				self.send_state()
			time.sleep(TIME_INTERVAL_SECONDS)




def main():
	for _ in range(5):
		print("gpu_server running")
		time.sleep(5)
	# me = Instance(args.id, args.address)




