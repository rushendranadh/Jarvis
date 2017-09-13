
from new_file import Switch, Play, Log, Fan
from modules import low, high, er_pin, dev_pins, dev_objs, ops, device, operation, default_name, water_v, play_v

def setup():
	global low, high, er_pin
	pi.wiringPiSetupGpio()				#for gpio pin numbering
	pi.pinMode(er_pin, low)				#setmode output(write) (pin 13)
	pi.digitalWrite(er_pin, low)
	for i in range(1,10):
		pi.pinMode(i, low)			#setmode output(write) (pins 1-9)
		pi.digitalWrite(i, low)			#make pin 'i' low
	for i in range(14,19):
		pi.pinMode(i, high)			#setmode input(read) (pins 14-19)

def analyze(temp):
	global dev_objs, ops, device, operation, default_name, water_v, play_v, low, high
	temp = temp.lower().split()
	device = ''
	operation = ''
	for i in temp:
		if i in dev_pins.keys():
			device = i
		elif i in ops.keys():
			operation = ops[i]
		elif device and operation:
			break
	if not device:
		pass
		#Log("Invalid command\n\t"+str(temp)+".").start()
		return False
	print (device, operation)
	if not dev_pins[device]:
		try:
			operation = temp[1]
		except IndexError:
			if device == "play":
				operation = default_name
			elif device == "stop":
				return False

		if device == "play":
			if not play_v:
				p = Play(operation)		#create play thread
				p.start()
				time.sleep(2)
				if p.isAlive():
					play_v = high
				else:
					pass
					#Log("Unable to start play thread.").start()	#Create and run error thread

		elif device == "stop":
			if "play" in operation and play_v and p.isAlive():
				p._Thread__stop()
				play_v = low
				if p.isAlive():
					play_v = high
					#Log("Unable to stop play thread.").start()
			elif operation == "motor":
				water_v = low
		return False
	else:
		return True

def check():
	global dev_objs, device, operation
	try:
		dev = dev_objs[device]
	except KeyError:
		if device == "fan":
			dev = Fan(device)
			dev_objs[device] = dev
		else:
			dev = Switch(device)
			dev_objs[device] = dev
	if device == "fan":
		dev.fan_d()
		return True
	elif not operation:
		operation = high
		if dev_objs[device].get():
			operation = low
		return True
	elif dev.get() != operation:
		dev.toggle(operation)

	if dev.get() != operation:				#checking command execution
		pass
		#Log("Executing the command\n\t"+device+" "+str(operation)+".").start()
	return True

"""	for i, j in zip(cycle(dev_pins.keys()), ops.keys()):
		d_f = re.search(i, temp, re.I)
		o_f = re.search(i, temp, re.I)
		if d_f:
			device = i
		if o_f:
			operation = i"""


