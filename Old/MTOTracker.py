import os

BATH_SIZE = 350 # 350 liters

FILE_NAME = "MTO.mather"

# First Line is total deposited up to now
# Every line after is a deposite statement, start pump, or end pump

FILE_LOC = __file__.replace("\\", "/") # This is the way to make sure it goes wherever the script is
FILE_LOC = FILE_LOC.split("/")
FILE_LOC = "/".join(FILE_LOC[:-1])

FILE_PATH = FILE_LOC + "/" + FILE_NAME

def deposited(amount):
	if not os.path.exists(FILE_PATH):
		with open(FILE_PATH, "w") as f:
			f.write("Total: 0")
	
	with open(FILE_PATH, "r") as f:
		lines = f.read().splitlines()
	
	tot = lines[0].split(": ")
	