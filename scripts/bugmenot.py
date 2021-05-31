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

	def _get_account(self, host):
		headers = dict()
		headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'
		headers['Pragma'] = 'no-cache'
		headers['Cache-Control'] = 'no-cache'

		try:
			request = urllib.request.Request('http://www.bugmenot.com/view/%s' % host, None, headers)

			page = urllib.request.urlopen(request).read().decode() 
            
		except Exception as e:
			print(e)
			print ('Http Error! Please check the url you input and the network connection')
			sys.exit()

		re_loginpwd = re.compile(self.regex, re.IGNORECASE | re.DOTALL)

		match = re_loginpwd.findall(page)
	
		return [{'username':i, 'password':j, 'stats':s} for i, j, s in match if i and j and len(i) < 30]

	def get_account(self, host):
		return self._get_account(host)
