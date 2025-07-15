import time
import os

CAL_ROTS = 10 # number of rotations to calibrate on

FILE_NAME = "PumpControlState.mather"

FILE_LOC = __file__.replace("\\", "/") # This is the way to make sure it goes wherever the script is
FILE_LOC = FILE_LOC.split("/")
FILE_LOC = "/".join(FILE_LOC[:-1])

FILE_PATH = FILE_LOC + "/" + FILE_NAME

rotationsPerAmountA = 1
rotationsPerAmountC = 1

if os.path.exists(FILE_PATH):
	with open(FILE_PATH, "r") as f:
		for line in f.readlines():
			k,v = line.split(':')
			if k == "rotationsPerAmountA":
				rotationsPerAmountA = float(v)
			elif k == "rotationsPerAmountC":
				rotationsPerAmountC = float(v)

def saveState():
	with open(FILE_PATH, "w") as f:
		f.write("\n".join( [ ":".join([str(j) for j in i]) for i in [ ("rotationsPerAmountA", rotationsPerAmountA), ("rotationsPerAmountC", rotationsPerAmountC) ] ]))

def turn_pump(to_pump, rotations):
	# to_pump is a string 'a' or 'c'
	# rotations is the number of turns
	# here we rotate the pump (coming soon)
	return True

def pump(to_pump, amount): # this is for manual pumping
	if to_pump == "a":
		rots = rotationsPerAmountA*amount
	elif to_pump == "c":
		rots = rotationsPerAmountC*amount
	else:
		return False
	
	turn_pump(to_pump, rots)
	return True

def calibrate(to_pump, amount):
	global rotationsPerAmountA, rotationsPerAmountC
	
	print("Calibration on : ", to_pump, "Pumped: ", amount)
	
	print("RotPerAmA: ", rotationsPerAmountA)
	print("RotPerAmC: ", rotationsPerAmountC)
	
	if to_pump == "a":
		rotationsPerAmountA = CAL_ROTS/amount
	elif to_pump == "c":
		rotationsPerAmountC = CAL_ROTS/amount
	else:
		return False
	
	print("RotPerAmA: ", rotationsPerAmountA)
	print("RotPerAmC: ", rotationsPerAmountC)
	
	saveState()
	return True