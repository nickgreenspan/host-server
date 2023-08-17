from threading import Thread
import subprocess
import re
import requests
import time
import os

TIME_INTERVAL_SECONDS = 10

class Instance:
	def __init__(self, token, address):
		self.token = token
		self.serverless_address = address
		self.state = {"tps" : None, "state": "loading"} # "loading" || "ready" || "error"
		self.changed = False

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

	def report_state(self):
		URI = f'http://{self.serverless_address}/report'
		request_dict = {"token": self.token, "state": self.state}
		response = requests.post(URI, json=request_dict)
		if response.status_code == 200:
			print("[gpuserver] reported state to serverless server")
		else:
			print("[gpuserver] failed reporting state to serverless server")

	def start(self):
		print(f"starting server, token:{self.token}, serv addr: {self.serverless_address}")
		while True:
			if self.state["state"] == "loading":
				self.check_ready()
			if self.state["state"] == "ready":
				self.update_metrics()
			# if self.changed:
			# 	self.report_state()
			# 	self.changed = False
			time.sleep(TIME_INTERVAL_SECONDS)

def main():
	token = os.environ.get("TOKEN")
	addr = os.environ.get("SERVERLESS_ADDR")
	me = Instance(token, addr)
	me.start()

if __name__ == "__main__":
	main()




