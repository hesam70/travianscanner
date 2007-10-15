#!/usr/bin/python
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*- 
#
# Copyright 2007 Sevenever
# Copyright (C) 2007 Sevenever
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

import codecs
import os.path
import urllib
import urllib2
import cookielib

class TravianClient(object):
	def __init__(self,config,fslog):
		object.__init__(self)
		#initialize cookie
		self.COOKIEFILE = 'travian.cookie'
		# the path and filename to save your cookies in
		
		# importing cookielib worked
		self.cj = cookielib.LWPCookieJar()
		# This is a subclass of FileCookieJar
		# that has useful load and save methods	
		if os.path.isfile(self.COOKIEFILE):
			# if we have a cookie file already saved
			# then load the cookies into the Cookie Jar
			self.cj.load(self.COOKIEFILE)
		# then we get the HTTPCookieProcessor
		# and install the opener in urllib2
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		urllib2.install_opener(opener)
		
		self.fslog = fslog
		self.config = config
		self.txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT)'}
		
	def login(self):
		self.fslog.write('start login...\n')
		self.fslog.write('********************************************************\n')
		self.fslog.write('getting login web page...\n')
		theurl = 'http://' + self.config.ServerName + '/login.php'
		
		txdata = None
		
		# fake a user agent, some websites (like google) don't like automated exploration
		
		#get login page and form item names
		try:
			req = urllib2.Request(theurl, txdata, self.txheaders)
			# create a request object
			
			handle = urllib2.urlopen(req)
			# and open it to return a handle on the url
		except IOError, e:
			print 'We failed to open "%s".' % theurl
			if hasattr(e, 'code'):
				print 'We failed with error code - %s.' % e.code
			elif hasattr(e, 'reason'):
				print "The error object has the following 'reason' attribute :"
				print e.reason
			return False
		else:
			strForm = handle.read().decode('UTF-8')
			#here we got login web form
			self.fslog.write('here we got login web form\n')
			self.fslog.write('********************************************************\n')
			self.fslog.write(strForm)
			self.fslog.write('\n')
			strForm = strForm[strForm.find(u'<input type="hidden" name="login" value="')+len(u'<input type="hidden" name="login" value="'):]
			loginvalue = strForm[:10]
			strForm = strForm[strForm.find(u'用户名:'):]
			strForm = strForm[strForm.find(u'name="')+len(u'name="'):]
			userfield = strForm[:7]
			strForm = strForm[strForm.find(u'密码:'):]
			strForm = strForm[strForm.find(u'name="')+len(u'name="'):]
			passfield = strForm[:7]
			strForm = strForm[strForm.find(u'name="')+len(u'name="'):]
			extrafield = strForm[:7]
		
		self.fslog.write('********************************************************\n')
		self.fslog.write('Post login data...\n')
		theurl = 'http://' + self.config.ServerName + '/dorf1.php'
		# an example url that sets a cookie,
		# try different urls here and see the cookie collection you can make !
		txdata = urllib.urlencode({'w':'1280:1024','login':loginvalue.encode('UTF-8'),userfield.encode('UTF-8'):self.config.UserName.encode('UTF-8'),passfield.encode('UTF-8'):self.config.PassWord.encode('UTF-8'),extrafield.encode('UTF-8'):'','autologin':'ja'})
		print 'use username: ',self.config.UserName,' and password: ', self.config.PassWord, ' to login'
		print loginvalue.encode('UTF-8'),userfield.encode('UTF-8'),passfield.encode('UTF-8'),extrafield.encode('UTF-8')
		#txdata = None
		# if we were making a POST type request,
		# we could encode a dictionary of values here,
		# using urllib.urlencode(somedict)
		
		try:
			req = urllib2.Request(theurl, txdata, self.txheaders)
			# create a request object
			
			handle = urllib2.urlopen(req)
			# and open it to return a handle on the url
		except IOError, e:
			print 'We failed to open "%s".' % theurl
			if hasattr(e, 'code'):
				print 'We failed with error code - %s.' % e.code
			elif hasattr(e, 'reason'):
				print "The error object has the following 'reason' attribute :"
				print e.reason
			return False
		else:
			#here we got web form after login should be http://s1.travian.cn/dorf1.php
			self.fslog.write('here we got page after login\n')
			self.fslog.write('********************************************************\n')
			strHtml = handle.read().decode('UTF-8')
			self.fslog.write(strHtml)
			self.fslog.write('\n')
			if strHtml.find('login') > 0 and strHtml.find(u'用户名:') > 0 and strHtml.find(u'密码:') > 0 :
				return False
			#print 'These are the cookies we have received so far :'
			#for index, cookie in enumerate(self.cj):
			#	print index, '  :  ', cookie        
			self.cj.save(self.COOKIEFILE)                     # save the cookies again
		return True
		
	def getKarteZHtml(self,gridID):
		theurl = 'http://' + self.config.ServerName + '/karte.php?z=' + str(gridID)
		return self.getHtmlByURL(theurl)
		
	def getKarteDHtml(self,gridID,cCode):
		theurl = 'http://' + self.config.ServerName + '/karte.php?d=' + str(gridID) + '&c=' + str(cCode)
		return self.getHtmlByURL(theurl)
		
	def getHtmlByURL(self,theurl):
		strHtml = ''
		
		self.fslog.write('********************************************************\n')
		self.fslog.write('Getting ' + theurl + '\n')
		# fake a user agent, some websites (like google) don't like automated exploration
		succ = False
		for i in range(self.config.RetryNum):
			if not succ:
				self.fslog.write(str(i+1) + 'th try...\n')
				print 'Getting ' + theurl + '. The ' + str(i+1) + 'th try...'
				try:
					req = urllib2.Request(theurl, None, self.txheaders)
					# create a request object
					
					handle = urllib2.urlopen(req)
					# and open it to return a handle on the url
				except IOError, e:
					print 'We failed to open "%s".' % theurl
					if hasattr(e, 'code'):
						print 'We failed with error code - %s.' % e.code
					elif hasattr(e, 'reason'):
						print "The error object has the following 'reason' attribute :"
						print e.reason
				else:
					succ = True
					strHtml = handle.read().decode('UTF-8');
					#here we got web page http://s1.travian.cn/karte.php
					self.fslog.write('********************************************************\n')
					self.fslog.write('Here we got web page ' + theurl + '\n')
					self.fslog.write(strHtml)
					self.fslog.write('\n')
		return strHtml