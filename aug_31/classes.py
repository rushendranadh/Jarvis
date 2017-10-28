
from new_file import Switch, Log, play_d, Fan, Play_speech, start_setup, E_mail, play_string
from modules import low, high, er_pin, dev_pins, ops, room, device, operation, water_v, play_v
from modules import event, s_features, time, re, process


def analyze(temp):

	#lists = dir()
	global dev_pins, s_features, ops, room, device, operation, event
	device = ''
	operation = ''
	room = ''
	event = ''

	f = list(filter(lambda x: re.search(x, temp, re.I), dev_pins.keys()))
	room = f.pop() if f else "others"

	f = list(filter(lambda x: re.search(x, temp, re.I), dev_pins[room].keys()))
	device = f.pop() if f else None

	f = list(filter(lambda x: re.search(x, temp, re.I), ops.keys()))
	operation = ops[f.pop()] if f else None

	f = list(filter(lambda x: re.search(x, temp, re.I), s_features.keys()))

	if f:
		event = f.pop()
		op = re.search(event+'\\s(.*)', temp, re.I)
		if op:
			try:
				operation = op.group(1).strip()
			except AttributeError:
				operation = None
	else:
		event = None
	if (not event) and ("stop" in temp):
		event = "stop"
	if (not device) and (not event) and ("stop" not in temp):
		Log("Invalid command\n\t"+str(temp)+".").start()
		Play_speech("Device not found").start()
		return False
	else:
		return True

def check():
	global dev_pins, room, device, operation, event
	if device:
		dev = dev_pins[room][device]["obj"]
		if not operation:
			operation = high
			if dev.get():
				operation = low
		if device == "fan":
			response = dev.fan_toggle(operation)
		else:
			response = dev.toggle(operation)

		if not response or dev.get() != operation:				#checking command execution
			Log("Executing the command\n\t"+room+" "+device+" "+str(operation)+".").start()
		return True
	else:
		if event == "play":
			if not s_features["play"]:
				p = process.Process(target=play_d, args=(operation,))
				p.start()
				time.sleep(0.2)
				if p.is_alive():
					s_features["play"] = p
				else:
					s_features["play"] = None
					Log("Unable to start play thread.").start()	#Create and run error thread
			elif s_features["play"].is_alive():
				print ("Already playing...")
		elif event == "send":
			response = re.search('(.*)\\sto\\s.*?(\w+)', operation, re.I)
			if response:
				message = response.group(1)
				to = response.group(2)
			E_mail(message, to).start()
		elif event == "time":
			play_string("time")
		elif event == "day":
			play_string("day")
		elif event == "stop":
			if s_features["play"] and s_features["play"].is_alive():
				s_features["play"].terminate()
				time.sleep(0.5)
				if s_features["play"].is_alive():	
					Log("Unable to stop play thread.").start()
				else:
					s_features["play"] = None
			elif operation == "motor":
				water_v = low
		elif event == "setup":
			start_setup()
		return True



