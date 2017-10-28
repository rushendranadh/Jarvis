import os
import re
import time
import threading as thread
import wiringpi as pi
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import multiprocessing as process

dev_pins = {"hall":{"light":{"pin":1, "obj":None}, "fan":{"pin":[2, 3], "obj":None}}, "others":{"light":{"pin":8, "obj":None}, "fan":{"pin":[6, 7], "obj":None}}}
#dev_pins = {"hall":{"light":{"pin":1, "obj":None}, "tv":{"pin":4, "obj":None}, "cooler":{"pin":6, "obj":None}, "fan":{"pin":[2, 3], "obj":None}}, "kitchen":{"light":{"pin":7, "obj":None}, "exhaust":{"pin":[8, 9], "obj":None}}, "others":{"motor":{"pin":5, "obj":None}, "light":{"pin":8, "obj":None}, "fan":{"pin":[6, 7], "obj":None}}}

#dev_pins = {"hall":{"light":1, "tv":4, "cooler":6, "fan":[2, 3]}, "kitchen":{"light":7, "fan":[8, 9]}, "others":{"motor":5, "light": 8, "fan":[6, 7]}}
s_features={"play": None, "day": None, "time": None, "send": None, "setup": None}

friends = {'rishi':{"email":"rushendranadh@gmail.com", "phone": 9032332132}, 'giri':{"email":"pgp262@gmail.com", "phone": 8884319180}}

er_pin = 13										#Error pin
u_e, o_e, o_f = 14, 15, 16								#Tank check pins

ops = {"on": True, "off": False, "increase": "up", "decrease": "down", "switchoff": False, "turnoff": False, "turnon": True, "switchon": True, "up": "up", "down": "down"}
music_path = "../../../Downloads/"		#Change according to songs location or set it as home
default_path = "upp"					#Default songs folder name
low, high = 0, 1
play_v, water_v = low, low
device = ''
operation = ''
room = ''
event = ''
mail_from_address = "rushendranad@gmail.com"



