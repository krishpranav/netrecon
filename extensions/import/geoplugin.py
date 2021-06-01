#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
from core.database import *
import json

class karma_ext():

	name     = "geoplugin importer"
			
	def match(self, head_str):
		""" match string in order to identify nmap xml report """
		if "geoplugin_request" in head_str:
			return True
		return False

	def parse(self, json_file, database):
		""" import host's longitude and latitude from geoplugin json """
		file = open(json_file,'r')
		sp_out = file.read()
		file.close()

		geo_out = json.loads(sp_out)

		# check if the host exists
		if database.host_exist(geo_out["geoplugin_request"]):
			# update
			add_host = database.session.query(targets).filter( targets.address == geo_out["geoplugin_request"] ).one()
				
			# update values only if there's more informations
			
			add_host.latitude = geo_out["geoplugin_latitude"]
			add_host.longitude = geo_out["geoplugin_longitude"]
			add_host.country_code = geo_out["geoplugin_countryCode"]
			add_host.country_name = geo_out["geoplugin_countryName"]

			database.session.add(add_host)
			database.session.commit()
