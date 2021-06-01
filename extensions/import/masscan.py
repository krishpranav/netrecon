#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
from core.database import *
from xml.etree import ElementTree

import json

class karma_ext():

	name     = "masscan importer"
	
	def match(self, head_str):
		""" match string in order to identify nmap xml report """
		if "masscan" in head_str.lower():
			return True
		return False

	def parse(self, xml, database):
		""" import masscan xml output """

		dom = ElementTree.parse(xml)
		scan = dom.findall('host')
		out = {}
		add_host = ""

		for s in scan:
			addr = s.getchildren()[0].items()[0][1]
			port = s.getchildren()[1].getchildren()[0].items()[1][1]

			try:
				service = s.getchildren()[1].getchildren()[0].getchildren()[1].items()[0][1]
			except: 
				service = ""
			try:
				banner = s.getchildren()[1].getchildren()[0].getchildren()[1].items()[1][1]
			except: 
				banner = ""
			try:
				port_state =  s.getchildren()[1].getchildren()[0].getchildren()[0].items()[0][1]
			except:
				port_state = ""

			try:
				proto = s.getchildren()[1].getchildren()[0].items()[0][1]
			except: 
				proto= ""


			if addr in out:
				if service != "title" and service != "":

					if database.port_exist(add_host.id, port, proto):
						# update the existing port
						add_port = database.session.query(services).filter( services.host_id == add_host.id, services.port == port, services.protocol == proto ).one()

						if len(service) > 0:
							add_port.service = service
						#if len(service.servicefp) > 0:
						#	add_port.fingerprint = str(service.servicefp)

						if len(port_state) > 0:
							add_port.state = port_state
						if len(banner) > 0:
							add_port.banner = banner

					else:
						# add the new port
						add_port = services(port=port, protocol=proto, service=service, fingerprint=banner, state=port_state, banner="", host = out[addr])

						# commit to db
						database.session.add(add_port)

			else:
				if database.host_exist(addr):

					add_host = database.session.query(targets).filter( targets.address == addr ).one()

				else:
					# add the host to the db
					add_host = targets(address=addr, status="up")
					
					# commit to db
					database.session.add(add_host)

				out[addr] = add_host

			database.session.commit()
			

	def parse_json(self, json_file, database):
		""" 
		broken json importer, seems like python 3 json parser doesn't like
		 masscan's json output for some reason :/
		"""

		file = open(json_file,'r')
		sp_out = file.read()
		file.close()

		#print s

		masscan_out = json.loads(sp_out.replace('\0', ''))


		for line in masscan_out:

			if database.host_exist(line["ip"]):

				add_host = database.session.query(targets).filter( targets.address == line["ip"] ).one()

			else:
				# add the host to the db
				add_host = targets(address=line["ip"], status="up")
				
				# commit to db
				database.session.add(add_host)

				#out[addr] = add_host

			for port in line["ports"]:
				if port_exist(add_host.id, port["port"], port["proto"]):

					# update the existing port
					add_port = database.session.query(services).filter( services.host_id == add_host.id, services.port == port["port"], services.protocol == port["proto"] ).one()

					try:
						if len(port["status"]) > 0:
							add_port.state = port["status"]

						if len(port["service"]["name"]) > 0:
							add_port.service = port["service"]["name"]

						if len(port["service"]["banner"]) > 0:
							add_port.fingerprint = banner


					except:
						pass

				else:
					# add the new port
					add_port = services(port=port["port"], protocol=port["proto"], service=port["service"]["name"], fingerprint=port["service"]["banner"], state=port["status"], banner="", host = line["ip"])

					# commit to db
					database.session.add(add_port)

				database.session.commit()



