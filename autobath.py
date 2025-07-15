from flask import Flask, render_template, request
from datetime import datetime

import TrainingDataset
import SensorReader

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/training')
def training():
	return render_template('training.html')

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

if __name__ == '__main__':
	app.run(port=9000, host="0.0.0.0", debug=True)