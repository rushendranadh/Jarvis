#!/usr/bin/python3

from new_file import motor, startup			# importing modules
from classes import analyze, check


startup()
#motor()

if __name__ == "__main__":
	while True:
		i_cmd = ""
		i_cmd = input("Enter command: ")
		ck = analyze(i_cmd)
		if ck:
			check()
		continue


