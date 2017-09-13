#!/usr/bin/python3

from new_file import motor, get, mail	# importing modules
from classes import analyze, check, setup
from modules import os


"""
setup()
os.system("play audio (All systems active, command mode activated)")

motor()

"""

if __name__ == "__main__":
	while True:
		i_cmd = ""
		i_cmd = input("Enter command: ")
		ck = analyze(i_cmd)
		if ck:
			check()
		continue

