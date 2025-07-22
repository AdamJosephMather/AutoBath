from flask import Flask, render_template, request
from datetime import datetime

import os

import datetime
import time

import threading

response = None



FILE_NAME = "Training.csv"

FILE_LOC = __file__.replace("\\", "/") # This is the way to make sure it goes wherever the script is
FILE_LOC = FILE_LOC.split("/")
FILE_LOC = "/".join(FILE_LOC[:-1])

FILE_PATH = FILE_LOC + "/" + FILE_NAME


FILE_NAME_TWO = "ConstantData.csv"
FILE_PATH_TWO = FILE_LOC + "/" + FILE_NAME_TWO

def ensureExists():
	if not os.path.exists(FILE_PATH):
		with open(FILE_PATH, "w") as f:
			f.write("DATE,TIME,SAMPLE_TIME,MTO,PERCENT,MIL,LUX,IR,VIS,PH,TEMP\n")

ensureExists()

def getData():
	global response
	
	response = None
	
	req_id = str(uuid.uuid4())
	client.user_data_set({"req_id": req_id})
	
	cmd = {"cmd": "read_data", "request_id": req_id}
	client.publish(CMD_TOPIC, json.dumps(cmd))
	print(f"Sent request {req_id}, waiting for reply…")
	
	timeout = time.time() + 10 # the ph and temp reads take longer
	while time.time() < timeout:
		if response is not None:
			break
		time.sleep(0.1)
	
	if response is not None:
		lux, ir, vis, ph, temp = response
		print("Received:", lux, ir, vis, ph, temp)
		return lux, ir, vis, ph, temp
	else:
		print("No response received within timeout.")
		raise RuntimeError("Data was not received in timeout (0_0)")

def constantRead():
	while True:
		try:
			lux, ir, vis, ph, temp = getData()
		except RuntimeError:
			continue
		
		t = time.time()
		
		if not os.path.exists(FILE_PATH_TWO):
			with open(FILE_PATH_TWO, "w") as f:
				f.write("UNIX_TIME,LUX,IR,VIS,PH,TEMP\n")
		
		with open(FILE_PATH_TWO, "a") as f:
			f.write(f"{t},{lux},{ir},{vis},{ph},{temp}\n")
		
		time.sleep(60)

#def getReadForTime():
#	

def writeReading(mto_str: str, val: str, unit: str):
	unit = unit.lower()
	
	try:
		mto = float(mto_str)
		v = float(val)
		if unit == "mils":
			mils = v
			per = (v / 10.2) * 100
		elif unit == "percentage":
			per = v
			mils = (v / 100) * 10.2
		else:
			print(f"Got unexpected unit: {unit}")
			return False
	except:
		return False
	
	
	### GET THE LIGHT VALUES ###
	
	try:
		lux, ir, vis, ph, temp = getData()
	except RuntimeError as e:
		return False
	
	### GET TIME AND WRITE DATA ###
	
	dT = datetime.datetime.now().strftime("%Y-%m-%d")
	tM = datetime.datetime.now().strftime("%H:%M:%S")
	rT = datetime.datetime.now().strftime("%H:%M:%S")
	
	with open(FILE_PATH, "a") as f:
		f.write(f"{dT},{tM},{rT},{mto},{per},{mils},{lux},{ir},{vis},{ph},{temp}\n")
	
	return True

def getDataForHTMX():
	ensureExists()
	
	data = []
	
	with open(FILE_PATH, "r") as f:
		for line in f.readlines():
			if line.strip() == "":
				continue
			
			if "DATE,TIME,SAM" in line: # it's the first line
				continue
			
			linedataraw = line.split(",")
			linedata = []
			
			for itm in linedataraw:
				try:
					t = float(itm)
					linedata.append(str(round(t, 3)))
				except:
					linedata.append(itm)
			
			data.append(linedata)
	
	data.append("DATE,TIME,SAMPLE_TIME,MTO,PERCENT,MIL,LUX,IR,VIS,PH,TEMP".split(','))
	
	return data

########################################### MQTT ###########################################

import json
import uuid
import time
import paho.mqtt.client as mqtt

BROKER   = "localhost"
PORT     = 1883
DEVICEID = "pi-1"

CMD_TOPIC  = f"devices/{DEVICEID}/commands"
RESP_TOPIC = f"devices/{DEVICEID}/responses"


def on_connect(client, userdata, flags, rc):
	print("Connected to broker, subscribing to responses…")
	client.subscribe(RESP_TOPIC)

def on_message(client, userdata, msg):
	global response
	payload = json.loads(msg.payload)
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
	t = threading.Thread(target=constantRead())
	t.start()
	
	app.run(port=9000, host="0.0.0.0", debug=True)