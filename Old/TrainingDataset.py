import os
import json
import time

import SensorReader

MAX_MILS = 10.2

FILE_NAME = "TitrationData.json"

FILE_LOC = __file__.replace("\\", "/") # This is the way to make sure it goes wherever the script is
FILE_LOC = FILE_LOC.split("/")
FILE_LOC = "/".join(FILE_LOC[:-1])

FILE_PATH = FILE_LOC + "/" + FILE_NAME

print("Working with file: " + FILE_PATH)

def getAllData():
	if not os.path.exists(FILE_PATH):
		with open(FILE_PATH, "w") as f:
			json.dump([], f)
	
	with open(FILE_PATH, 'r') as f:
		data = json.load(f)
	
	return data

def writeEntry(value, units) -> bool:
	value = value.replace(" ", "")
	if "percent" in units.lower():
		value = value.replace("%", "")
	
	try:
		value = float(value)
	except:
		print("[ERROR] Couldn't convert value to float")
		return False # Failed to convert to a floating point number
		
	if "mils" in units.lower():
		percentage = (value/MAX_MILS)*100
		mils = value
	elif "percent" in units.lower():
		percentage = value
		mils = (value/100)*MAX_MILS
	else:
		print("[ERROR] Units were neither mils or percentage")
		return False
	
	lux, ir, vis = SensorReader.readData()
	
	entry_time = time.time() # unix time (seconds since that random date - to prevent issues with time zones, etc -> CLOCK MUST BE SET RIGHT)
	
	existing_data = getAllData()
	existing_data.append({"time":entry_time, "mils": mils, "percentage": percentage, "lux":lux, "ir":ir, "vis":vis})
	
	with open(FILE_PATH, "w") as f:
		json.dump(existing_data, f)
	
	return True

def getDataForHTMX():
	data = getAllData()
	final_data = []
	
	for d in data:
		entry = []
		
		t = d["time"]
		readable = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
		
		entry.append(readable)
		entry.append(round(d["mils"], 2))
		entry.append(str(round(d["percentage"], 2))+"%")
		entry.append(round(d["lux"], 2))
		entry.append(round(d["ir"], 2))
		entry.append(round(d["vis"], 2))
		
		final_data.append(entry)
	
	final_data.append(["Time", "Mils", "Percentage", "Lux", "IR", "Visible"])
	
	return final_data