#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
import os

class karma_ext():
	
	name = "browser"
	menu = {"service" : ["http"], "label" : "Open in Browser"}
	log = False

	def task(self, config):
		""" open an url with browser"""
		host = config["rhost"]
		port = config["rport"]

		url = host + ":" + port

		if '443' in port:
			url = "https://"+ url
		else:
			url = "http://"+ url
			
		os.system("xdg-open "+url),9999