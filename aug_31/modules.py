import os
import re
import time
import threading as thread
import wiringpi as pi
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


dev_pins = {"hall":{"light":1, "tv":4, "cooler":6, "fan":[2, 3]}, "kitchen":{"light":7, "fan":8}, "motor":5, "play":0, "stop":0}

dev_objs = {}										#Device_name : object
dev_pins = {"light":1, "tv":4, "motor":5, "cooler":6, "fan":[2, 3], "play":0, "stop":0}	#Device_name : pin_number
er_pin = 13										#Error pin
u_e, o_e, o_f = 14, 15, 16								#Tank check pins

ops = {"on": True, "off": False, "increase": "up", "decrease": "down", "switchoff": False, "turnoff": False, "turnon": True, "switchon": True, "up": "up", "down": "down"}
music_path = "../../../home/rushendranadh/Downloads/"		#Change according to songs location or set it as home
default_name = "default"					#Default songs folder name
low, high = 0, 1
play_v, water_v = low, low
device = ''
operation = ''
mail_from_address = "rushendranad@gmail.com"

