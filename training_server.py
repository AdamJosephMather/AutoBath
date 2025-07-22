from flask import Flask, render_template, request
from datetime import datetime

import SensorReader
import os

import datetime

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
	
	lux, ir, vis = SensorReader.readData()
	
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