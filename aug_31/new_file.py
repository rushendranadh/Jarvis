
from modules import thread, pi, os, time							#Modules
from modules import low, high, dev_pins, dev_objs, music_path, water_v, play_v, device, operation, music_path
from modules import er_pin, u_e, o_e, o_f, used_pins						#Variables
from modules import mail_from_address, smtplib, MIMEMultipart, MIMEText, copy

class Switch():
	def __init__(self, name, room_name):
		global dev_pins
		self.name = name
		self.pin = dev_pins[room_name][name]
		#self.__status = self.get()

	def get(self, g_pin=low):
		if not g_pin:
			g_pin = self.pin
		return pi.digitalRead(g_pin)			#get pin status(low/high)

	def toggle(self, state, t_pin=low):
		global low, high
		i = low
		if state:
			i = high
		if not t_pin:
			t_pin = self.pin
		pi.digitalWrite(t_pin, i)				#make pin high(1)
		if self.get(t_pin) == i:
			self.__status = i

class Fan(Switch):
	def __init__(self, name, room_name):
		global dev_pins
		self.name = name
		self.l_bit = dev_pins[room_name][name][0]
		self.h_bit = dev_pins[room_name][name][1]
		self.__status = low
	def fan_toggle(self):
		global low, high, device, operation
		fan_ops = {False:0, True:1, "up":2, "down":3}
		try:
			var = fan_ops[operation]
		except KeyError:
			var = 4
		if self.__status == var:
			return True
		elif var == 1:
			if not __f_state:
	#			self.toggle(high, self.l_bit)			#fan speed
				self.toggle(high, self.h_bit)
				self.__status = var
		elif not var:
			self.toggle(low, self.l_bit)
			self.toggle(low, self.h_bit)
			self.__status = var
		elif var == 2:
			if get(self.l_bit) and (not get(self.h_bit)):
				self.toggle(high, self.h_bit)
				self.toggle(low, self.l_bit)
			elif (not get(self.l_bit)) and get(self.h_bit):
				self.toggle(high, self.l_bit)
			elif not (get(self.l_bit) and get(self.h_bit)):
				self.toggle(high, self.l_bit)
				self.toggle(low, self.h_bit)
			self.__status = var
		elif var == 3:
			if get(self.l_bit) and get(self.h_bit):
				self.toggle(low, self.l_bit)
			elif (not get(self.l_bit)) and get(self.h_bit):
				self.toggle(low, self.h_bit)
				self.toggle(high, self.l_bit)
			elif get(self.l_bit) and (not get(self.h_bit)):
				self.toggle(low, self.l_bit)
			self.__status = var
		elif var == 4:
			if not self.__status:
	#			self.toggle(high, self.l_bit)			#fan speed
				self.toggle(high, self.h_bit)
				self.__status = high
				var = high
			else:
				self.toggle(low, self.l_bit)
				self.toggle(low, self.h_bit)
				self.__status = low
				var = low
		if self.__status != var:
			Log("Executing the command\n\t"+room+" "+device+" "+str(operation)+".").start()
		return True
	def get(self):
		return self.__status
	
class Play(thread.Thread):
	def __init__(self, dir_n):
		thread.Thread.__init__(self)
		self.dir_name = dir_n
	def run(self):
		play_d(self.dir_name)

def play_d(dir_name):
	global music_path
	file_list = []
	check_name = re.compile('.*'+dir_name+'.*', re.I)
	for root, dirs, files in os.walk(music_path):
		found = list(filter(lambda x: (check_name.match(x)), dirs))
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
		Log("Album not found with name \""+dir_name+"\".").start()
	return

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

def mail(message, to_address):
	global mail_from_address
	msg = MIMEMultipart()
	msg['From'] = mail_from_address
	msg['To'] = to_address
	msg['Subject'] = "Test subject"

	msg.attach(MIMEText(message, 'plain'))
	text = msg.as_string()
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	server.login(mail_from_address, "9676852995")
	status={to_address:message}
	try:
		status = server.sendmail(mail_from_address, to_address, text)
	except Exception:
		status_message = "'Mail is not delivered to "+to_address+"'"
		Log(status_message).start()
	server.quit()
	if not status:
		status_message = "'Mail sent successfully.'"
	os.system("google_speech -l en "+ status_message)

def get(string):
	t_data = time.localtime()
#	t_data[year, month_num, m_day, h, m, sec, w_day, y_day, isdst]
	day = {0:'monday', 1:'tuesday', 2:'wednesday', 3:'thursday', 4:'friday', 5:'saturday', 6:'sunday'}
	month = {1:"january", 2:"february", 3:"march", 4:"april", 5:"may", 6:"june", 7:"july", 8:"august", 9:"september", 10:"october", 11:"november", 12:"december"}
	hours = t_data[3]
	minutes = str(t_data[4])
	if not hours:
		hours = str(12)
		minutes = minutes +" AM"
	elif hours >= 12:
		hours = str(hours-12)
		minutes = minutes +" PM"
	else:
		hours = str(hours)
		minutes = minutes +" AM"
	if string == 'time':
		time_get = "'time is "+hours+" "+minutes+"'"
		Play_speech(time_get).start()
	if string == 'day':
		day_get = "'today is "+day[t_data[6]]+" "+str(t_data[2])+" "+month[t_data[1]]+" "+str(t_data[0])+"'"
		Play_speech(day_get).start()

class Play_speech(thread.Thread):
	def __init__(self, msg, rep=0):
		thread.Thread.__init__(self)
		self.message = msg
		self.repeat = rep
	def run(self):
		play_speech_d(self.message, self.repeat)

def play_speech_d(string, repeat):
	os.system("google_speech -l en "+string+" -e repeat "+str(repeat))
	return

class Setup():
	def __init__(self):
		global used_pins
		used_pins = self.available_pins()

	def available_pins(self):
		pins = []
		for i in dev_pins.keys():
			pins += list(dev_pins[i].values())
		else:
			used = []
			for i in pins:
				used.extend(i) if isinstance(i, list) else used.append(i)
			return used

	def get_pin(self):
		global dev_pins, used_pins
		for i in range(1,13):
			if i not in used_pins:
				print (i)
				return i

	def add_device(self, device_name, room_name= None):
		global dev_pins, dev_objs, used_pins
		pin_number = []
		if not room_name:
			room_name = "others"
		if device_name == "fan":
			new_pin = self.get_pin()
			pin_number.append(new_pin)
			used_pins.append(new_pin)
			new_pin = self.get_pin()
			pin_number.append(new_pin)
			used_pins.append(new_pin)
			dev_pins[room_name][device_name] = pin_number
			dev_objs[room_name][device_name]= Fan(device_name, room_name)
		else:
			pin_number = self.get_pin()
			used_pins.append(pin_number)
			dev_pins[room_name][device_name] = pin_number
			dev_objs[room_name][device_name]= Switch(device_name, room_name)
		if dev_pins[room_name][device_name]:
			Play_speech("'Device added successfully'").start()
		else:
			Play_speech("'Device not added'").start()

	def remove_device(self, device_name, room_name= None):
		global dev_pins, dev_objs
		if not room_name:
			room_name = "others"
		del dev_pins[room_name][device_name]
		del dev_objs[room_name][device_name]
		if not dev_pins[room_name][device_name]:
			Play_speech("'Device removed successfully'").start()
		else:
			Play_speech("'Device not removed'").start()

def start_setup():
	global dev_pins, dev_objs
	pwd = "1"
	password = input("Enter password: ")
	if pwd != password:
		Play_speech("'Please check your password'", 1).start()
		print("Wrong password !!!")
		return False
	else:
		set_up = Setup()
		dev_objs = copy.deepcopy(dev_pins)
		selection = ''
		while selection != 'x':
			selection = input("Select :"+"\n"+"a : Add device"+"\n"+"r : Remove device"+"\n"+"x : Exit"+"\n")
			selection = selection.lower()
			if selection == 'x':
				print ("Exiting...")
				break
			elif selection == 'a':
				room_name = input("Enter room: ").strip()
				device_name = input("Enter device: ").strip()
				set_up.add_device(device_name, room_name)
			elif selection == 'r':
				room_name = input("Enter room: ").strip()
				device_name = input("Enter device: ").strip()
				set_up.remove_device(device_name, room_name)
		return








