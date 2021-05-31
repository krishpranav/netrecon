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
