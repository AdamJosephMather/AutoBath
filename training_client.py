# pi_client.py
import json
import paho.mqtt.client as mqtt
import SensorReader

BROKER   = "192.168.1.247"
PORT     = 1883
DEVICEID = "pi-1"

CMD_TOPIC = f"devices/{DEVICEID}/commands"
RESP_TOPIC = f"devices/{DEVICEID}/responses"

def on_connect(client, userdata, flags, rc):
	print("Connected (rc=%s)" % rc)
	client.subscribe(CMD_TOPIC)

def on_message(client, userdata, msg):
	try:
		payload = json.loads(msg.payload)
	except json.JSONDecodeError:
		print("Invalid JSON")
		return
	
	if payload.get("cmd") == "read_data":
		lux, ir, vis = SensorReader.readData()

		response = {
			"request_id": payload.get("request_id"),
			"data": [lux, ir, vis]
		}
		
		client.publish(RESP_TOPIC, json.dumps(response))
		print(f"Replied to {payload['request_id']}")
		
client = mqtt.Client()
client.reconnect_delay_set(min_delay=1, max_delay=120)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()