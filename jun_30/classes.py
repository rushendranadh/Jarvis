
import os
import re
import time
import threading as th
import wiringpi as pi
from itertools import cycle
from new_file import play, fan, log

dev_objs = {}										#Device_name : object
dev_pins = {"light":1, "tv":4, "motor":5, "cooler":6, "fan":[2, 3], "play":0, "stop":0}	#Device_name : pin_number
er_pin = 13										#Error pin
u_e, o_e, o_f = 14, 15, 16								#Tank check pins

ops = {"on": True, "off": False, "increase": "up", "decrease": "down", "switchoff": False, "turnoff": False, "turnon": True, "switchon": True, "up": "up", "down": "down"}
music_path = "../../../home/rushendranadh/Downloads/"		#Change according to songs location
default_name = "default"					#Default songs folder name
low, high = 0, 1
play_v, water_v = low, low
device = ''
operation = ''


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
	for i, j in zip(cycle(dev_pins.keys()), ops.keys()):
		d_f = re.search(i, temp, re.I)
		o_f = re.search(i, temp, re.I)
		if d_f:
			device = i
		if o_f:
			operation = i
	for i in temp:
		if i in dev_objs.keys():
			device = i
		elif i in ops.keys():
			operation = ops[i]
		elif device and operation:
			break
	if not device:
		log("Invalid command\n\t"+str(temp)+".").start()
		return False
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
				p = play(operation)		#create play thread
				p.start()
				time.sleep(2)
				if p.isAlive():
					play_v = high
				else:
					log("Unable to start play thread.").start()	#Create and run error thread

		elif device == "stop":
			if "play" in operation and play_v and p.isAlive():
				p._Thread__stop()
				play_v = low
				if p.isAlive():
					play_v = high
					log("Unable to stop play thread.").start()
			elif operation == "motor":
				water_v = low
		return False

	elif (device != "fan") and (not operation):
		operation = high
		if dev_objs[device].get():
			operation = low
		return True


def check():
	global dev_objs, device, operation
	try:
		dev = dev_objs[device]
	except KeyError:
		if device == "fan":
			dev = fan(device)
			dev_objs[device] = dev
		else:
			dev = switch(device)
			dev_objs[device] = dev
	if device == "fan":
		dev.fan_d()
		return True
	elif dev.get() != operation:
		dev.toggle(operation)

	if dev.get() != operation:				#checking command execution
		log("Executing the command\n\t"+str(device+" "+operation)+".").start()
	return True





