#!/usr/bin/python3

from modules import tha, os, water, switch, setup, analyze_test	# importing modules
from modules import events					# importing variables

"""
setup()
os.system("play audio (All systems active, command mode activated)")
w = th.Thread(water, ())				#create water thread
w.Start()
if w.Isalive:
	th_ids["water"] = water
else:
	log_error("Error: unable to start water thread")
"""

if __name__ == "__main__":
	while True:
		i_cmd = ""
		i_cmd = input("Enter command: ")

		check = analyze_test(i_cmd)
		if check:
			switch()
		continue

