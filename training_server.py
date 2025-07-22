from flask import Flask, render_template, request
from datetime import datetime

import os

import datetime
import time

FILE_NAME = "Training.csv"

FILE_LOC = __file__.replace("\\", "/") # This is the way to make sure it goes wherever the script is
FILE_LOC = FILE_LOC.split("/")
FILE_LOC = "/".join(FILE_LOC[:-1])

FILE_PATH = FILE_LOC + "/" + FILE_NAME

def ensureExists():
	if not os.path.exists(FILE_PATH):
		with open(FILE_PATH, "w") as f:
			f.write("DATE,TIME,MTO,PERCENT,MIL,LUX,IR,VIS\n")

ensureExists()

def writeReading(mto_str, val, unit):
	global response
	
	try:
		mto = float(mto_str)
		v = float(val)
		if unit == "Mils":
			mils = val
			per = (val / 10.2) * 100
		elif unit == "Percentage":
			per = val
			mils = (per / 100) * 10.2
		else:
			print(f"Got unexpected unit: {unit}")
			return False
	except:
		return False
	
	
	### GET THE LIGHT VALUES ###
	
	response = None
	
	req_id = str(uuid.uuid4())
	client.user_data_set({"req_id": req_id})
	
	cmd = {"cmd": "read_data", "request_id": req_id}
	client.publish(CMD_TOPIC, json.dumps(cmd))
	print(f"Sent request {req_id}, waiting for reply…")
	
	timeout = time.time() + 5
	while time.time() < timeout:
		if response is not None:
			break
		time.sleep(0.1)
	
	client.loop_stop()
	
	if response is not None:
		lux, ir, vis = response
		print("Received:", num1, num2)
	else:
		print("No response received within timeout.")
		return False
	
	
	### GET TIME AND WRITE DATA ###
	
	dT = datetime.datetime.now().strftime("%Y-%m-%d")
	tM = datetime.datetime.now().strftime("%H:%M:%S")
	
	with open(FILE_PATH, "a") as f:
		f.write(f"{dT},{tM},{mto},{per},{mil},{lux},{ir},{vis}\n")

def getDataForHTMX():
	ensureExists()
	
	data = []
	
	with open(FILE_PATH, "r") as f:
		for line in f.readlines():
			if line.strip() == "":
				continue
			
			if "DATE,TIME,MTO" in line:
				continue
			
			data.append(line.split(","))
	
	data.append("DATE,TIME,MTO,PERCENT,MIL,LUX,IR,VIS".split(','))
	
	return data

########################################### MQTT ###########################################

import json
import uuid
import time
import paho.mqtt.client as mqtt

BROKER   = "192.168.0.247"
PORT     = 1883
DEVICEID = "pi-1"

CMD_TOPIC  = f"devices/{DEVICEID}/commands"
RESP_TOPIC = f"devices/{DEVICEID}/responses"

# Global to hold the incoming response
response = None

def on_connect(client, userdata, flags, rc):
	print("Connected to broker, subscribing to responses…")
	client.subscribe(RESP_TOPIC)

def on_message(client, userdata, msg):
	global response
	payload = json.loads(msg.payload)
	# Match the request_id
	if payload.get("request_id") == userdata["req_id"]:
		response = payload["data"]

client = mqtt.Client(userdata={"req_id": None})
client.reconnect_delay_set(min_delay=1, max_delay=120)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

########################################### FLASK ###########################################

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('training.html')

@app.route('/submit_titration', methods=['POST'])
def submit_titration():
	mto = request.form.get('mto_value', '').strip()
	value = request.form.get('input_value', '').strip()
	unit = request.form.get('unit', '')
	
	if not value or not unit or not mto:
		return "<p style='color: red;'>All fields are required.</p>", 400
	
	worked = writeReading(mto, value, unit)
	
	if not worked:
		print("[ERROR] TrainingDataset.writeEntry failed")
		return "<p style='color: red;'>Dataset did not accept data.</p>", 400
	
	return "<p>Submitted!</p>"

@app.route('/titration_data')
def titration_data():
	data = getDataForHTMX() #format is: [ [ values ], [ values ], [ names ] ]
	data.reverse() # we want the newest at the top
	
	out = "<table>"
	style = "th"
	
	for d in data:
		out += "\n<tr>"
		for el in d:
			out += "\n<"+style+">" + str(el) + "</"+style+">"
		
		out += "\n</tr>"
		style = "td"
	
	out += "\n</table>"
	
	return out

if __name__ == '__main__':
	app.run(port=9000, host="0.0.0.0", debug=True)