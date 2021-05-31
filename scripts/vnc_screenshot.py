#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# imports
import base64
import gi
import time 
import threading
import sys

gi.require_version('GtkVnc', '2.0')

from gi.repository import GtkVnc
from gi.repository import Gtk


def screenshot(dpy):
	time.sleep(5)
	pix = dpy.get_pixbuf()
	pix.savev( "/tmp/netrecon-screenshot"+sys.argv[1]+"-"+sys.argv[2], "png", "", "")

	with open ("/tmp/netrecon-screenshot"+sys.argv[1]+"-"+sys.argv[2], "rb" ) as image:
		print( base64.b64encode(image.read()).decode() )

	# quit
	Gtk.main_quit()
	quit()		