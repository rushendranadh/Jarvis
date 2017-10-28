
from modules import thread, pi, os, time, re							#Modules
from modules import low, high, dev_pins, music_path, water_v, play_v, device, operation, music_path
from modules import er_pin, u_e, o_e, o_f, friends, default_path				#Variables
from modules import mail_from_address, smtplib, MIMEMultipart, MIMEText, s_features


def startup():
	global low, high, er_pin, dev_pins
#	pi.wiringPiSetupGpio()				#for gpio pin numbering
#	pi.pinMode(er_pin, low)				#setmode output(write) (pin 13)
#	pi.digitalWrite(er_pin, low)
#	for i in range(1,13):
#		pi.pinMode(i, low)			#setmode output(write) (pins 1-9)
#		pi.digitalWrite(i, low)			#make pin 'i' low
#	for i in range(14,19):
#		pi.pinMode(i, high)			#setmode input(read) (pins 14-19)
	for i in dev_pins.keys():
		for j in dev_pins[i].keys():
			if j == "fan":
				dev_pins[i][j]["obj"] = Fan(j, i)
			else:
				dev_pins[i][j]["obj"] = Switch(j, i)
	Play_speech("All systems active, command mode, activated").start()

class Switch():
	def __init__(self, name, room_name):
		global dev_pins
		self.name = name
		self.pin = dev_pins[room_name][name]["pin"]
		self.status = self.get()

	def get(self, g_pin=low):
		if not g_pin:
			g_pin = self.pin
		return True
		return pi.digitalRead(g_pin)			#get pin status(low/high)

	def toggle(self, state, t_pin=low):
		global low, high
		ops = {'on':high, 'off': low}
		try:
			i = ops[state]
		except KeyError:
			return False
		if not t_pin:
			t_pin = self.pin
		return True
		pi.digitalWrite(t_pin, i)				#make pin high(1)
		if self.get(t_pin) == i:
			self.status = i
		#return True

class Fan(Switch):
	def __init__(self, name, room_name):
		global dev_pins
		self.name = name
		self.l_bit = dev_pins[room_name][name]["pin"][0]
		self.h_bit = dev_pins[room_name][name]["pin"][1]
		self.status = low

	def get(self, pin=0):
		fan_ops = {False:0, True:1, "up":2, "down":3}
		if pin:
			return pi.digitalRead(pin)
		g_l = pi.digitalRead(self.l_bit)
		g_h = pi.digitalRead(self.h_bit)
		if not (g_l and g_h):
			return False
		elif g_l and g_l:
			return True
		else:
			return list(fan_ops.keys())[list(fan_ops.values()).index(self.status)]

	def fan_toggle(self, op):
		global low, high
		fan_ops = {False:0, True:1, "up":2, "down":3}
		try:
			var = fan_ops[op]
		except KeyError:
			var = 4
		if self.status == var:
			return True
		elif var == 1:
#			self.toggle(high, self.l_bit)			#fan speed
			self.toggle(high, self.h_bit)
		elif not var:
			self.toggle(low, self.l_bit)
			self.toggle(low, self.h_bit)
		elif var == 2:
			if self.get(self.l_bit) and (not self.get(self.h_bit)):
				self.toggle(high, self.h_bit)
				self.toggle(low, self.l_bit)
			elif (not self.get(self.l_bit)) and self.get(self.h_bit):
				self.toggle(high, self.l_bit)
			elif not (self.get(self.l_bit) and self.get(self.h_bit)):
				self.toggle(high, self.l_bit)
			elif self.get(self.l_bit) and self.get(self.h_bit):
				pass
		elif var == 3:
			if self.get(self.l_bit) and self.get(self.h_bit):
				self.toggle(low, self.l_bit)
			elif (not self.get(self.l_bit)) and self.get(self.h_bit):
				self.toggle(low, self.h_bit)
				self.toggle(high, self.l_bit)
			elif self.get(self.l_bit) and (not self.get(self.h_bit)):
				self.toggle(low, self.l_bit)
			elif not (self.get(self.l_bit) and self.get(self.h_bit)):
				pass
		elif var == 4:
			if not self.status:
	#			self.toggle(high, self.l_bit)			#fan speed
				self.toggle(high, self.h_bit)
				var = high
			else:
				self.toggle(low, self.l_bit)
				self.toggle(low, self.h_bit)
				var = low			
		self.status = var
		if self.get() != fan_ops[op]:
			return False
		return True
	
#class Play(thread.Thread):
#	def __init__(self, dir_n):
#		thread.Thread.__init__(self)
#		self.dir_name = dir_n
#	def run(self):
#		play_d(self.dir_name)

def play_d(dir_name):
	global music_path, default_path, s_features
	file_list = []
	if dir_name and (dir_name != "songs"):
		search = re.search('songs\\s?from?\\s?(.*)?|(.*)', dir_name)
		if search:
			dir_name = search.group(1) or search.group(2)
	else:
		dir_name = default_path
	check_dir = re.compile('.*'+dir_name+'.*', re.I)
	check_song = re.compile('.*'+dir_name+'.*.mp3', re.I)
	for root, dirs, files in os.walk(music_path):
		found_dir = list(filter(lambda x: (check_dir.match(x)), dirs))
		found_song = list(filter(lambda x: (check_song.match(x)), files))
		if found_dir:
			path = os.path.join(root, found_dir.pop())
			file_list = list(filter(lambda x: re.search('.*.mp3', x), os.listdir(path)))
			break
		if found_song:
			path = root
			file_list.append(found_song.pop())
			break
	if file_list:
		for i in file_list:
			s_path = path +'/'+ i
			print(s_path)
#			p = process.Process(play_process(s_path), ())
#			s_features["play"] = p
			os.execlp("mpg123", "mpg123", s_path)
	else:
		Log("Album not found with name \""+dir_name+"\".").start()
		Play_speech("Album "+dir_name+" not found").start()
	return

def play_process(path):
	os.execlp("mpg123", "mpg123", path)

def error_led():
	global low, high, er_pin
	pi.digitalWrite(er_pin, low)			#make pin 13 low
	for i in range(0, 3):				#blink LED 3 times
		time.sleep(0.5)				#delay 0.5sec
		pi.digitalWrite(er_pin, high)		#make pin high
		time.sleep(0.5)
		pi.digitalWrite(er_pin, low)		#make pin low
	return

class Log(thread.Thread):
	def __init__(self, error_msg):
		thread.Thread.__init__(self)
		self.message = error_msg
		self.log_d()
	def run(self):
		error_led()
	def log_d(self):
		t_data = time.localtime()
		with open("Err_log.txt", 'a') as f:
			f.write("Date & Time: "+str(t_data[2])+"-"+ str(t_data[1])+ ", "+
				str(t_data[3])+ ":"+ str(t_data[4])+ ":"+ str(t_data[5])+"\n\tError: "+self.message+"\n")

def water_toggle(sw):
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

class Water(thread.Thread, Switch):
	def __init__(self, pin):
		thread.Thread.__init__(self)
		self.pin = pin
	def run(self):
		water_toggle(self)

def motor():
	global water_v, low
	if not water_v:
		w = Water()				#create water thread
		w.Start()
		time.sleep(2)
		if not w.isAlive:
			water_v = low
			Log("Unable to start water thread.").start()

class E_mail(thread.Thread):
	def __init__(self, msg, to):
		thread.Thread.__init__(self)
		self.message = msg
		self.to = to
	def run(self):
		mail(self.message, self.to)

def mail(message, to):
	global mail_from_address, friends

	msg = MIMEMultipart()
	msg['From'] = mail_from_address
	msg['To'] = friends[to]["email"]
	msg['Subject'] = "Message from Rishi"

	msg.attach(MIMEText(message, 'plain'))
	text = msg.as_string()
	s = smtplib.SMTP("smtp.gmail.com", 587)
	s.starttls()
	s.login(mail_from_address, "9676852995")
	status={msg['To']:message}
	try:
		status = s.sendmail(mail_from_address, msg['To'], text)
	except Exception:
		status_message = "Mail is not delivered to, "+msg['To']
		Log(status_message).start()
	s.quit()
	if not status:
		status_message = "Mail sent successfully."
	Play_speech(status_message).start()

	return

def play_string(string):
	t_data = time.localtime()
	print (t_data)
#	t_data[year, month_num, m_day, h, m, sec, w_day, y_day, isdst]
	day = {0:'monday', 1:'tuesday', 2:'wednesday', 3:'thursday', 4:'friday', 5:'saturday', 6:'sunday'}
	month = {1:"january", 2:"february", 3:"march", 4:"april", 5:"may", 6:"june", 7:"july", 8:"august", 9:"september", 10:"october", 11:"november", 12:"december"}
	hours = t_data[3]
	minutes = str(t_data[4])
	if hours >= 12:
		hours = "12" if (hours-12)==0 else str(hours-12)
		minutes = minutes +" PM"
	elif not hours:
		hours = str(12)
		minutes = minutes +" AM"
	else:
		hours = str(hours)
		minutes = minutes +" AM"
	if string == 'time':
		string = "time is "+hours+" "+minutes
	elif string == 'day':
		string = "today is, "+day[t_data[6]]+" "+str(t_data[2])+" "+month[t_data[1]]+" "+str(t_data[0])
	Play_speech(string).start()

class Play_speech(thread.Thread):
	def __init__(self, msg, rep=0):
		thread.Thread.__init__(self)
		self.message = msg
		self.repeat = rep
	def run(self):
		play_speech_d(self.message)

def play_speech_d(string):
	string = "'"+string+"'"
	try:
		os.system("google_speech -l en "+string+" -e echo 0.98 0.97 0.66 0.64 echo 0.95 0.91 0.63 0.61 echo 0.92 0.87 0.59 0.58")
	except RuntimeError:
		Log("Cannot play "+string).start()
	return

class Setup():
	def __init__(self):
		self.used_pins = self.available_pins()

	def available_devs(self):
		global dev_pins
		for i in dev_pins.keys():
			print ("Devices in '"+i+"' are ", list(dev_pins[i].keys()))

	def available_pins(self):
		pins = []
		for r in dev_pins.keys():
			for dev in dev_pins[r].keys():
				pins.append(dev_pins[r][dev]["pin"])
		else:
			used = []
			for i in pins:
				used.extend(i) if isinstance(i, list) else used.append(i)
			return used

	def get_pin(self):
		for i in range(1,13):
			if i not in self.used_pins:
				print (i)
				return i

	def add_device(self, device_name, room_name= None):
		global dev_pins
		pin_number = []
		if not room_name:
			room_name = "others"
		elif room_name not in dev_pins.keys():
			dev_pins[room_name] = dict([(device_name, None)])
		if device_name == "fan":
			new_pin = self.get_pin()
			pin_number.append(new_pin)
			self.used_pins.append(new_pin)
			new_pin = self.get_pin()
			pin_number.append(new_pin)
			self.used_pins.append(new_pin)
		else:
			pin_number = self.get_pin()
			self.used_pins.append(pin_number)
		dev_pins[room_name][device_name] = dict([("pin", pin_number),("obj", None)])
		if dev_pins[room_name][device_name]:
			Play_speech("Device added successfully").start()
		else:
			Play_speech("Device not added").start()

	def remove_device(self, device_name, room_name= "others"):
		global dev_pins
		if (not device_name) or (not dev_pins.get(room_name)) or (device_name not in dev_pins[room_name].keys()):
			print ("No device found.\n")
			return None
		elif device_name in dev_pins[room_name].keys():
			del dev_pins[room_name][device_name]
			if not dev_pins[room_name] and room_name != "others":
				del dev_pins[room_name]
		if (not dev_pins.get(room_name)) or (dev_pins.get(room_name) and (device_name not in dev_pins[room_name].keys())):
			Play_speech("Device removed successfully").start()
		else:
			Play_speech("Device not removed").start()

def start_setup():
	pwd = "1"
	password = input("Enter password: ")
	if pwd == password:
		s = Setup()
		selection = ''
		while selection != 'x':
			print("Available devices are:")
			s.available_devs()
			selection = input("\nSelect :"+"\n"+"a : Add device"+"\n"+"r : Remove device"+"\n"+"x : Exit"+"\n")
			selection = selection.lower()
			if selection == 'x':
				print ("Exiting...")
				Play_speech("System rebooting").start()
				time.sleep(2)
				startup()
				break
			elif selection == 'a':
				room_name = input("Enter room: ").strip()
				device_name = input("Enter device: ").strip()
				s.add_device(device_name, room_name)
			elif selection == 'r':
				room_name = input("Enter room: ").strip()
				device_name = input("Enter device: ").strip()
				s.remove_device(device_name, room_name)
	else:
		Play_speech("Please check your password").start()
		print("Wrong password !!!")
	return False







