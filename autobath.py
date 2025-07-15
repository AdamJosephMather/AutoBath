from flask import Flask, render_template, request
from datetime import datetime

import TrainingDataset
import SensorReader
import PumpControl

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/training')
def training():
	return render_template('training.html')

@app.route('/calibration')
def calibration():
	return render_template('calibration.html')

@app.route('/pump_calibration', methods=['POST'])
def pump_calibration():
	pump = request.form.get('pump', '')
	
	if not pump:
		return "<p style='color: red;'>Missing pump.</p>", 400
	
	if not PumpControl.turn_pump(pump, PumpControl.CAL_ROTS):
		return "<p style='color: red;'>Pumping failed.</p>", 400
	
	return "<p>Pumping.</p>", 200

@app.route('/submit_calibration', methods=['POST'])
def submit_calibration():
	pump = request.form.get('pump_2', '')
	value = request.form.get('input_value', '')
	
	if not pump or not value:
		return "<p style='color: red;'>Both fields are required.</p>", 400
	
	try:
		val = float(value)
	except:
		return "<p style='color: red;'>Could not convert amount to float.</p>", 400
	
	if not PumpControl.calibrate(pump, val):
		return "<p style='color: red;'>Failed to calibrate.</p>", 400
	
	return "<p>Calibrated.</p>", 200

@app.route('/submit_titration', methods=['POST'])
def submit_titration():
	print("Submitted!")
	
	value = request.form.get('input_value', '').strip()
	unit = request.form.get('unit', '')
	
	if not value or not unit:
		return "<p style='color: red;'>Both fields are required.</p>", 400
	
	worked = TrainingDataset.writeEntry(value, unit)
	
	if not worked:
		print("[ERROR] TrainingDataset.writeEntry failed")
		return "<p style='color: red;'>Dataset did not accept data.</p>", 400
	
	return "<p>Submitted!</p>"

@app.route('/titration_data')
def titration_data():
	data = TrainingDataset.getDataForHTMX()
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

@app.route('/html_widget')
def html_widget():
	lux, ir, vis = SensorReader.readData()
	
	lux = round(lux, 2)
	ir = round(ir, 2)
	vis = round(vis, 2)
	
	return f"""
		<table>
			<tr>
				<th>Lux</th>
				<th>IR</th>
				<th>Visible</th>
			</tr>
			<tr>
				<td>{lux}</td>
				<td>{ir}</td>
				<td>{vis}</td>
			</tr>
		</table>"""

@app.route('/manual_a_dose')
def manual_a_dose():
	value = request.form.get('input_a_value', '').strip()
	
	if not value:
		return "<p style='color: red;'>Required feild.</p>", 400
	
	try:
		flt_val = float(value)
	except:
		return "<p style='color: red;'>Requires a number.</p>", 400
	
	# here we need to call our function to pump flt_val of fluid
	
	PumpControl.pump('a', flt_val)
	
	return "<p>Pumping.</p>"


@app.route('/manual_c_dose')
def manual_c_dose():
	value = request.form.get('input_c_value', '').strip()
	
	if not value:
		return "<p style='color: red;'>Required feild.</p>", 400
	
	try:
		flt_val = float(value)
	except:
		return "<p style='color: red;'>Requires a number.</p>", 400
	
	# here we need to call our function to pump flt_val of fluid
	
	PumpControl.pump('c', flt_val)
	return "<p>Pumping.</p>"

if __name__ == '__main__':
	app.run(port=9000, host="0.0.0.0", debug=True)