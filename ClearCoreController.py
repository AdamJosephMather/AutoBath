import time
import serial
import serial.tools.list_ports as port_list

def find_clearcore_port():
	"""Scan for a port whose description mentions ClearCore."""
	for p in port_list.comports():
		print("Option: ", p.description)
		if 'Teknic' in p.description or 'ClearCore' in p.description:
			print("  Found device")
			return p.device
	raise IOError("ClearCore port not found")

class ClearCore:
	def __init__(self, port=None, baud=115200, timeout=1):
		self.port = port or find_clearcore_port()
		# Open the virtual COM port at 115200 baud
		self.ser = serial.Serial(self.port, baudrate=baud, timeout=timeout)
		time.sleep(2)  # allow MCU to reset

	def send_cmd(self, cmd):
		"""
		Send an ASCII command (without trailing newline) and return
		all reply lines as a list of stripped strings.
		"""
		line = (cmd.strip() + '\n').encode('ascii')
		self.ser.write(line)
		replies = []
		while True:
			raw = self.ser.readline()
			if not raw:
				break
			replies.append(raw.decode('ascii', errors='ignore').strip())
		return replies

	# --- Convenience methods for motor control ---
	def enable_motor(self, motor=0):
		return self.send_cmd(f'e{motor}')

	def disable_motor(self, motor=0):
		return self.send_cmd(f'd{motor}')

	def move_absolute(self, motor, position):
		# CCCP defaults to absolute mode; see docs to toggle relative vs. absolute  :contentReference[oaicite:2]{index=2}
		return self.send_cmd(f'm{motor} {position}')

	def set_velocity(self, motor, vel):
		return self.send_cmd(f'v{motor} {vel}')

	def query_position(self, motor):
		resp = self.send_cmd(f'q{motor}p')
		return int(resp[0]) if resp else None

	# --- Digital I/O ---
	def read_input(self, connector):
		return int(self.send_cmd(f'i{connector}')[0])

	def write_output(self, connector, val):
		return self.send_cmd(f'o{connector} {val}')

if __name__ == '__main__':
	cc = ClearCore()
	print("Enabling motor 0:", cc.enable_motor(0))
	cc.move_absolute(0, 1000)
	time.sleep(1)
	pos = cc.query_position(0)
	print("Position after move:", pos)
	print("Digital input 9:", cc.read_input(9))
	cc.disable_motor(0)