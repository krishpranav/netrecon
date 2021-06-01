#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
import signal
import argparse
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from core.main import Handler
from core.extensions import karmaEngine

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--session', help='Open a session file')
	args = parser.parse_args()

	signal.signal(signal.SIGINT, signal.SIG_DFL)

	if args.session:
		engine = karmaEngine(session_file=args.session)
	else:
		engine = karmaEngine()

	Handler(engine)
	Gtk.main()
