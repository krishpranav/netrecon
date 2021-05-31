#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
import argparse
import sys
import configparser
import ipaddress
import os
import json
import threading

from shodan import Shodan

sout = {}

class shodanThread (threading.Thread):
	def __init__(self, threadID, name, targets, verbose=False):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.targets = targets
		self.verbose = verbose

	def run(self):

		for target in self.targets:
			try:
				ipinfo = api.host(target)

				print('[+] target ip \t\t %s' % target)
				print(' ')#[-] ')
				print('[-] os \t\t\t %s' % ipinfo['os'])
				print('[-] org \t\t %s' % ipinfo['org'])
				print('[-] city \t\t %s' % ipinfo['city'])
				print('[-] region code \t %s' % ipinfo['region_code'])
				print('[-] ISP \t\t %s' % ipinfo["isp"])
				print('[-] country code \t %s' % ipinfo['country_code'])
				print('[-] latitude \t\t %s' % ipinfo['latitude'])
				print('[-] longitude \t\t %s' % ipinfo['longitude'])

				print(' ')
				print('[*] hostnames :')

				for hostname in ipinfo["hostnames"]:
					print("[-]\t%s" % hostname )

				print(' ')
				print('[*] Ports :')

				i = 0
				for port in ipinfo["ports"]:
					print("[-]\t%s - %s" % (port, ipinfo["data"][i]["transport"]) )

					i += 1

				print( ' ')

				sout[target] = ipinfo



			except:
				if (self.verbose):
					print('[+] target ip \t\t %s' % target)
					print("[!] Not found.")
					print( ' ')


def chunkify(lst,n):
	return [lst[i::n] for i in range(n)]

if __name__ == "__main__":

	# init
	config = configparser.ConfigParser()
	parser = argparse.ArgumentParser()

	# Target ip address, required
	parser.add_argument('target', metavar='target(s)', help='Target ip address')

	# --key or --config are required 
	parser.add_argument('--key', help='Shodan API key')
	parser.add_argument('--config', help='Get Shodan api key from config file')

	# verbose boolean
	parser.add_argument('--verbose', help='Get some extra info', action="store_true")

	# threads number
	parser.add_argument('--threads', help='Threads to query shodan', default=2)

	# output file name
	parser.add_argument('--out', help='json output file path')

	args = parser.parse_args()

	got_api = False
	default_config_path = os.path.abspath(str(os.path.dirname(os.path.realpath(__file__)) ) + "/../conf/shodan.conf")

	if args.config:
		config.read(args.config)

		if config['Shodan']["api_key"] != "API KEY HERE":
			api = Shodan(config['Shodan']["api_key"])
			got_api = True


	elif args.key:
		api = Shodan(args.key)
		got_api = True

	else:
		config.read(default_config_path)

		if config['Shodan']["api_key"] != "API KEY HERE":
			
			api = Shodan(config['Shodan']["api_key"])
			got_api = True




	print(" ")
	print('Shodanmap')
	print('---------')

	if not got_api:
		print("[!] Error: Shodan API key is missing, add it in the config file located under %s or using the --key option" % default_config_path)
		sys.exit()		

	todo = []


	try:

		if "/" in args.target:
			# get ip from range
			net4 = ipaddress.ip_network(args.target)

			for x in net4.hosts():
				todo.append(str(x))

		elif "-" in args.target:
			# get first ip
			start = args.target.split("-")[0]
			dot = start.split(".")
			end = args.target.split("-")[1]

			for t in range(int(dot[3]),int(end.split(".")[-1])+1):
				ip = dot[0] +"."+ dot[1] +"."+ dot[2] +"."+str(t)
				todo.append(ip)

				
		else:
			todo.append(args.target)

	except:
		print("[!] Invalid Target")
		sys.exit()


	t_num = int(args.threads)
	threads = []
	x = 0

	pt = chunkify(todo,t_num)

	for chunk in pt:

		# Create new threads
		thread = shodanThread(x, "Thread-"+str(x), chunk, verbose = args.verbose)
		
		if args.verbose:
			print("[+] Starting thread "+ str(x))

		# Start new Threads
		thread.start()

		threads.append(thread)

		x += 1

	for thread in threads:
		# wait threads to end
		thread.join()


	if args.out:
		try:
			with open(args.out, 'w') as fp:
				json.dump(sout, fp)
			print('[+] Results available under: %s' % args.out)

		except:
			pass
		
		

	print('[+] Done.')


