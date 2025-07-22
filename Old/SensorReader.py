import time
import board
import busio
import adafruit_tsl2591

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create TSL2591 instance
sensor = adafruit_tsl2591.TSL2591(i2c)

# Optionally configure gain and integration time
# sensor.gain = adafruit_tsl2591.GAIN_LOW  # Options: LOW, MED, HIGH, MAX
# sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS  # 100, 200, 300, etc.

def readData():
	return sensor.lux, sensor.infrared, sensor.visible

if __name__ == "__main__":
	while True:
		lux = sensor.lux
		infrared = sensor.infrared
		visible = sensor.visible
		full_spectrum = sensor.full_spectrum
	
		print(f"Lux: {lux:.2f}")
		print(f"Infrared: {infrared}")
		print(f"Visible: {visible}")
		print(f"Full Spectrum (IR + Visible): {full_spectrum}")
		print("-" * 40)
		time.sleep(1)