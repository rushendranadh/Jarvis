
from classes import th, pi, os, time							#Modules
from classes import low, high, dev_pins, music_path, water_v, play_v, device, operation
from classes import er_pin, u_e, o_e, o_f						#Variables


class switch():
	def __init__(self, name):
		global dev_pins
		self.name = name
		print(self.name)
		self.pin = dev_pins[name]
		print(self.pin)
		self.__status = get()

	def get(self, g_pin):
		return pi.digitalRead(g_pin)			#get pin status(low/high)

	def toggle(self, state, t_pin):
		global low, high
		i = low
		if state:
			i = high
		pi.digitalWrite(pin, i)				#make pin high(1)
		if get(t_pin) == i:
			self.__status = i

class fan(switch):
	__f_state = 0
	def __init__(self, name):
		global dev_pins
		self.name = name
		self.l_bit = dev_pins[name][0]
		self.h_bit = dev_pins[name][1]
	def fan_d(self):
		global low, high, device, operation
		fan_ops = {False:0, True:1, "up":2, "down":3}
		try:
			var = fan_ops[operation]
		except KeyError:
			var = 4
		if __f_state == var:
			return True
		elif var == 1:
			if not __f_state:
	#			toggle(high, self.l_bit)			#fan speed
				toggle(high, self.h_bit)
				__f_state = var
		elif not var:
			toggle(low, self.l_bit)
			toggle(low, self.h_bit)
			__f_state = var
		elif var == 2:
			if get(self.l_bit) and (not get(self.h_bit)):
				toggle(high, self.h_bit)
				toggle(low, self.l_bit)
			elif (not get(self.l_bit)) and get(self.h_bit):
				toggle(high, self.l_bit)
			elif not (get(self.l_bit) and get(self.h_bit)):
				toggle(high, self.l_bit)
				toggle(low, self.h_bit)
			__f_state = var
		elif var == 3:
			if get(self.l_bit) and get(self.h_bit):
				toggle(low, self.l_bit)
			elif (not get(self.l_bit)) and get(self.h_bit):
				toggle(low, self.h_bit)
				toggle(high, self.l_bit)
			elif get(self.l_bit) and (not get(self.h_bit)):
				toggle(low, self.l_bit)
			__f_state = var
		elif var == 4:
			if not __f_state:
	#			toggle(high, self.l_bit)			#fan speed
				toggle(high, self.h_bit)
				__f_state = high
				var = high
			else:
				toggle(low, self.l_bit)
				toggle(low, self.h_bit)
				__f_state = low
				var = low
		if __f_state != var:
			log("Executing the command\n\t"+str(device+" "+operation)+".").start()
		return True
	
class play(th.Thread):
	def __init__(self, dir_n):
		th.Thread.__init__(self)
		self.dir_name = dir_n
	def run(self):
		play_d(self.dir_name)

def play_d(dir_name):
	global music_path
	file_list = []
	check_name = re.compile('.*'+dir_name+'.*', re.I)
	for root, dirs, files in os.walk(music_path):
		found = filter(lambda x: (check_name.match(x)), dirs)
		if found:
			path = os.path.join(root, found.pop())
			file_list = os.listdir(path)
			break
	if file_list:
		for i in file_list:
			s_cmd = "vlc" + path + '/' + i
			print(s_cmd)
#			os.system(s_cmd)
	else:
		log("Album not found with name \""+dir_name+"\".").start()
	return

def error_led():
	global low, high, er_pin
	pi.digitalWrite(er_pin, low)			#make pin 13 low
	for i in range(0, 3):				#blink LED 3 times
		time.sleep(0.5)				#delay 0.5sec
		pi.digitalWrite(er_pin, high)		#make pin high
		time.sleep(0.5)
		pi.digitalWrite(er_pin, low)		#make pin low

class log(th.Thread):
	def __init__(self, error):
		self.error = error
		self.log_d()
	def run(self):
		error_led()
	def log_d(self):
		t_data = time.localtime()
		with open("Err_log.txt", 'a') as f:
			f.write("Date & Time: "+str(t_data[2])+"-"+ str(t_data[1])+ ", "+
				str(t_data[3])+ ":"+ str(t_data[4])+ ":"+ str(t_data[5])+"\n\tError: "+self.error+"\n")

def water_d(sw):
	global water_v, low, high, u_e, o_e, o_f
	water_v = high
	while water_v:
		if ((not sw.get(o_e)) and sw.get(u_e)) or sw.get():
			if not sw.get():
				sw.toggle(high)					#turn on
			while sw.get(u_e) and water_v:
				if sw.get(o_f):
					break
				elif not sw.get():
					break
				time.sleep(5)					#5 seconds
			if sw.get():
				sw.toggle(low)					#turn off
		time.sleep(300)							#5 minutes

class water(th.Thread, switch):
	def __init__(self, pin):
		th.Thread.__init__(self)
		self.pin = pin
	def run(self):
		water_d(self)

def motor():
	global water_v, low
	if not water_v:
		w = water()				#create water thread
		w.Start()
		time.sleep(2)
		if not w.isAlive:
			water_v = low
			log("Unable to start water thread.").start()


