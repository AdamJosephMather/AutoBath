import time

# OPTICAL

import board
import busio
import adafruit_tsl2591

# PH AND TEMP

from atlas_i2c.atlas_i2c import AtlasI2C

# pH sensor (default I2C address 0x63)
ph = AtlasI2C(address=0x63)
# optional: temp sensor if on its own RTD module (default addr 0x65)
temp = AtlasI2C(address=0x66)

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create TSL2591 instance
sensor = adafruit_tsl2591.TSL2591(i2c)

# Optionally configure gain and integration time
# sensor.gain = adafruit_tsl2591.GAIN_LOW  # Options: LOW, MED, HIGH, MAX
# sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS  # 100, 200, 300, etc.

def readData():
	try:
		ph_val = float(ph.query("R", processing_delay=3500).data.decode())
	except Exception as e:
		print(e)
		ph_val = -999 # just in case
	
	try:
		t = float(temp.query("R", processing_delay=2500).data.decode())
	except Exception as e:
		print(e)
		t = -999
	
	return sensor.lux, sensor.infrared, sensor.visible, ph_val, t

if __name__ == "__main__":
	while True:
		l, i, v, p, t = readData()
		
		print(f"Lux: {l:.2f}")
		print(f"Infrared: {i}")
		print(f"Visible: {v}")
		print(f"PH: {p}")
		print(f"Temp: {t}")
		print("-" * 40)
		time.sleep(1)