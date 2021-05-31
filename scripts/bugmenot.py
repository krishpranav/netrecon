#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports
import optparse
import sys
import urllib.request
import re
import json


class BugMeNot:
    def __init__(self):
        self.regex = u'<dl><dt>Username:</dt><dd><kbd>([^<]*)</kbd></dd>'
        self.regex += u'<dt>Password:</dt><dd><kbd>([^<]*)</kbd></dd>'
        self.regex += u'<dt class="stats">Stats:</dt><dd class="stats"> <ul> <li class="[^"]* [^"]*">([0-9]*%)[^<]*</li>'
