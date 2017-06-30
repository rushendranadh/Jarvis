
import os
import re
import time
import signal
import threading as tha
import _thread as th
import wiringpi as pi

dev_list = {"d1":1, "d2":4, "motor":5, "fan":[2, 3], "play":0, "stop":0}		# fan => 2, 3 pins
m_pins = {"u_e":10, "o_e":11, "o_f":12}							# t1_empty, t2_empty, t2_full
ops = {"on": True, "off": False, "increase": "up", "decrease": "down", "switchoff": False, "turnoff": False, "turnon": True, "switchon": True}
low, high = 0, 1
cmd = ["Nill", "Nill"]
music_path = "../../../home/rushendranadh/Downloads/"
default_name = "default"
events = {}

def water():
	global m_pins, dev_list, events
	while events["water"].isset():
		if ((not get(m_pins["o_e"])) and get(m_pins["u_e"])) or get(dev_list["motor"]):
			if not get(dev_list["motor"]):
				toggle(dev_list["motor"], True)			#turn on
			while get(m_pins["u_e"]):
				if get(m_pins["o_f"]):
					break
				elif not get(dev_list["motor"]):
					break
				time.sleep(5)					#5 seconds
			if get(dev_list["motor"]):
				toggle(dev_list["motor"], False)		#turn off
		time.sleep(300)							#5 minutes
#		if os.getppid() != ppid:
#			th.exit()

def switch():
	global dev_list, cmd
	print ("switch", cmd)
	check = False
	if cmd[0] == "fan":	
		check = fan(cmd[1])
	elif get(dev_list[cmd[0]]) == cmd[1]:
		pass
	else:
		toggle(dev_list[cmd[0]], cmd[1])

	if (not check) or (get(dev_list[cmd[0]]) != cmd[1]):			#checking command execution
		log_error("Executing the command\n\t"+str(cmd))
	return

def fan(opt):
	global dev_list
	fan_ops = {False:0, True:1, "up":2, "down":3, "Nill":4}
	p_list = dev_list["fan"]
	var = fan_ops[opt]
	if var == 1:
		print (var)
		return
		if get(p_list[0]) or get(p_list[1]):
			pass
		else:
#			toggle(p_list[0], True)			#fan speed
			toggle(p_list[1], True)
	elif var == 0:
		print (var)
		return
		if get(p_list[0]):
			toggle(p_list[0], False)
		if get(p_list[1]):
			toggle(p_list[1], False)
	elif var == 2:
		print (var)
		return
		if get(p_list[0]) and (not get(p_list[1])):
			toggle(p_list[1], True)
			toggle(p_list[0], False)
		elif (not get(p_list[0])) and get(p_list[1]):
			toggle(p_list[0], True)
		elif not (get(p_list[0]) and get(p_list[1])):
			toggle(p_list[0], True)
			toggle(p_list[1], False)
	elif var == 3:
		print (var)
		return
		if get(p_list[0]) and get(p_list[1]):
			toggle(p_list[0], False)
		elif (not get(p_list[0])) and get(p_list[1]):
			toggle(p_list[1], False)
			toggle(p_list[0], True)
		elif get(p_list[0]) and (not get(p_list[1])):
			toggle(p_list[0], False)
	elif var == 4:
		print (var)
		return
		if not(get(p_list[0]) and get(p_list[1])):
#			toggle(p_list[0], True)			#fan speed
			toggle(p_list[1], True)
		else:
			if get(p_list[0]):
				toggle(p_list[0], False)
			if get(p_list[1]):
				toggle(p_list[1], False)
	return True

def analyze(temp):
	global dev_list, events, cmd, ops, default_name
	temp = temp.lower()
	temp = temp.split()
	cmd = ["Nill", "Nill"]
	for i in temp:
		if i in dev_list.keys():
			cmd[0] = i
		elif i in ops.keys():
			cmd[1] = ops[i]
		elif "Nill" not in cmd:
			break
	if cmd[0] == "Nill":
		log_error("Invalid command\n\t"+str(temp))
		return False

	if cmd[0] == "play":
		play(temp[1])
		return False
		try:
			cmd[1] = temp[1]
		except IndexError:
			cmd[1] = default_name
		check = stop("play")
		if check:
			p = tha.Thread(play, (cmd[1],))		#create play thread
			p.start()
			events[p] = False
			print ("P: ", p_id)
			if p.Isalive():
				th_ids["play"] = p
			else:
				log_error("unable to start play thread")
		else:
			log_error("unable to stop the play thread")
		return False

	elif cmd[0] == "stop":
		try:
			cmd[1] = temp[1]
		except IndexError:
			return False
		stop(cmd[1])
		return False

	elif (cmd[0] != "fan") and (cmd[1] == "Nill"):
		if get(dev_list[cmd[0]]):
			cmd[1] = ops["off"]
		else:
			cmd[1] = ops["on"]
	print ("analyze: ", cmd)
	return True

class play_cl(tha.Thread):
	def __init__(self, dir_name):
		global name, events
		tha.Thread.__init__(self)
		self.dir = dir_name

	def run(self):
		new(self.dir)

def play(dir_name):
	global music_path, events
	file_list = []
	print ("play", dir_name)
	check_name = re.compile('.*'+dir_name+'.*', re.I)
	for root, dirs, files in os.walk(music_path):
		found = list(filter(lambda x: (check_name.match(x) != None), dirs))
		if found:
			path= os.path.join(root, found[0])
			file_list = os.listdir(path)
			break
	if file_list:
		for i in file_list:
			s_cmd = "vlc" + path + '/' + i
			print(s_cmd)
#			os.system(s_cmd)
	else:
		log_error("Album not found with name \""+dir_name+"\"")
	return

def get(pin):
	print ("get:", pin)
	return pi.digitalRead(pin)			#get pin status(low/high)

def toggle(pin, status):
	print ("toggle")
	global low, high
	i = low
	if status:
		i= high
	pi.digitalWrite(pin, i)				#make pin high(1)

def setup():
	print("setup")
	global low, high, events
	events["water"] = tha.Event()
	events["play"] = tha.Event()
	pi.wiringPiSetupGpio()				#for gpio pin numbering
	pi.pinMode(13, low)				#setmode out(write)
	for i in range(1,10):
		pi.pinMode(i, low)			#setmode out(write) (pins 0-9)
		pi.digitalWrite(i, low)			#make pin 'i' low
	for i in range(14,20):
		pi.pinMode(i, high)			#setmode in(read) (pins 14-19)

def stop(func):
	global events
	print("stop: ", events[func])
	return
	try:
		events[func].clear()
	except KeyError:
		return False
	
	if os.kill(end):
		th_ids[func] = False
		return True
	else:
		log_error("Unable to kill '"+func+"' thread")
		return False

def error_led():
	print("error_led")
	global low, high
	pi.digitalWrite(13, low)			#make pin 13 low
	for i in range(0, 3):
		time.sleep(0.5)				#delay 0.5sec
		pi.digitalWrite(13, high)		#make pin high
		time.sleep(0.5)
		pi.digitalWrite(13, low)		#make pin low

def log_error(string):
	print("log_error")
	err = th.start_new_thread(error_led, ())			#create thread for error
	t_data = time.localtime()
	with open("Err_log.txt", 'a') as f:
		f.write("Date & Time: "+str(t_data[2])+"-"+ str(t_data[1])+ ", "+
			str(t_data[3])+ ":"+ str(t_data[4])+ ":"+ str(t_data[5])+"\n\tError: "+string+"\n")




class play_cla(tha.Thread):
	def __init__(self):
		global name, events
		tha.Thread.__init__(self)
	def run(self):
		new()
	def stop(self):
		self._stop = True

def new():
	n=0
	while True:
		print(n)
		n += 1
		time.sleep(3)

def stopf(name):
	name.stop()

def analyze_test(temp):
	p = th.start_new_thread(new, ())
	print (p)
	return False



