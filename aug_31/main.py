#!/usr/bin/python3

from new_file import motor, get, mail, start_setup	# importing modules
from classes import analyze, check, startup
from modules import os


"""
startup()
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


