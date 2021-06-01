#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
import os
import gi
import random
import string
import subprocess
import threading
import socket

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import Gdk

from core import widgets
from core.extensions import base_ext

class karma_ext(base_ext):

	name = "websession"
	log = True
	menu = { "service" : ["http"], "label" : "Send to webSession" }


	def task(self, config):
		""" WebSession task: a Gtk.Paned that contains mitmproxy and  """
		ext              = config["menu-sel"].replace(" ","_")
		serv             = config["service"]
		proxychains      = config["proxychains"]
		auto_exec        = config["autoexec"]
		rhost            = config["rhost"]
		domain           = config["domain"]
		rport            = config["rport"]
		output_file      = config["outfile"]
		path_config      = config["path_config"]
		self.path_script = config["path_script"]
		self.o_file      = "/tmp/"+''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".mitm"

		config_file = self.conf()

		if domain:
			target = domain.split()[0]
		else:
			target = rhost

		# proxy port
		proxy_port = 8080
		found=True

		while found:
			# search for an open port for mitm
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			result = sock.connect_ex(('127.0.0.1',proxy_port))

			if result == 0:
			   proxy_port += 1
			else:
			   found = False

		cmd = "mitmproxy -p %d -w %s; exit;\n" % (proxy_port, self.o_file) # --set console_focus_follow=true

		if proxychains:
			cmd = "proxychains %s" % cmd

		terminal = widgets.Terminal()
		terminal.feed_child(cmd.encode())

		status = terminal.status
		pid    = terminal.pid

		box      = Gtk.Paned()
		scroller = Gtk.ScrolledWindow()

		scroller.add(terminal)

		if "443" in rport:
			url = "https://%s:%s" % (target, rport)
		else:
			url = "http://%s:%s" % (target, rport)


		webview  = widgets.WebView(url, proxy="http://127.0.0.1:%d" % proxy_port)

		webview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		webview_box.show()

		webview_box.add(webview.toolbar)
		webview_box.add(webview)

		webview_box.set_vexpand(True)
		scroller.set_hexpand(True)

		box.pack1(scroller, False, False);
		box.pack2(webview_box, True, False);

		scroller.set_property("width-request", 480)

		terminal.set_hexpand(True)
		box.set_vexpand(True)
		box.show_all()

		# add main window
		builder	         = self.gui()
		main_win         = builder.get_object('websession-main')
		payloads_toolbar = builder.get_object('payloads-bar')
		main_win.add(box)

		
		for payload_cat in config_file:
			if payload_cat != "DEFAULT":
				catbtn = Gtk.MenuItem(payload_cat)
				catbtn.show()
				subcat = Gtk.Menu()

				for payload_subcat in config_file[payload_cat]:
					

					subcatbtn = Gtk.MenuItem(payload_subcat)
					subcat.add(subcatbtn)
					subcat.show_all()

					payload_menu = Gtk.Menu()

					for payload in config_file[payload_cat][payload_subcat].split("\n"):
						
						payloadbtn = Gtk.MenuItem(payload)
						payload_menu.add(payloadbtn)

						payload_menu.show_all()

						payloadbtn.connect('activate', self.copy_payload, payload)

						subcatbtn.set_submenu(payload_menu)
					catbtn.set_submenu(subcat)
					

				payloads_toolbar.add(catbtn)

		terminal.connect("child_exited", self.task_terminated, main_win)

		return main_win, pid


	def copy_payload(self, widget, payload):
		""" Copy payload to clipboard """

		clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

		clipboard.set_text(payload, -1)


	def task_terminated(self, widget, two, box):
		""" run mitmdump on the mitmproxy's dumpfile """

		box.set_sensitive(False)

		cmd = "mitmdump -n -r %s; exit;\n" % self.o_file
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)


		log = p.stdout.read().decode()

		# removing the dump file
		os.remove(self.o_file)

		self.emit('end_task', log)



	def read(self, output):
		""" default reader """
		return output

	def get_log(self, output):
		""" default logger view"""
		
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_hexpand(True)
		scrolledwindow.set_vexpand(True)

		textview = widgets.SourceView()
		textbuffer = textview.get_buffer()
		textbuffer.set_text(output)

		textview.set_editable(False)

		scrolledwindow.add(textview)
		scrolledwindow.show_all()

		return scrolledwindow

