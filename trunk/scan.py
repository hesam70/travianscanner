#! /usr/bin/python
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
import os
import os.path
import cookielib
import sys
import threading
import random
import time
import re
from datetime import datetime
from Queue import Queue
from Queue import Empty
from TravianClient import TravianClient
from Config import Config

class Producer(threading.Thread):
    def __init__(self, threadname, scaner):
        threading.Thread.__init__(self, name = threadname)
        self.scaner = scaner
    def run(self):
		y=self.scaner.config.rect[1]+3
		while y<=self.scaner.config.rect[3]+3:
			x=self.scaner.config.rect[0]+3
			while x<=self.scaner.config.rect[2]+3:
				tmpx = x
				tmpy = y
				if tmpx > self.scaner.config.ServerScale:
					tmpx = x - self.scaner.config.ServerScale * 2 - 1
				if tmpy > self.scaner.config.ServerScale:
					tmpy = y - self.scaner.config.ServerScale * 2 - 1
				#gridID=320801+tmpx-801*tmpy
				tmp = self.scaner.config.ServerScale
				gridID = (tmp - tmpy) * (2 * tmp + 1) + tmpx + tmp + 1
				self.scaner.queue.put(str(gridID), 1)
				x=x+7
			y=y+7
			
		self.scaner.endflag = True
		print self.getName(),'Finished'

# KarteZThread thread
class KarteZThread(threading.Thread):
	def __init__(self, threadname, scaner):
		threading.Thread.__init__(self, name = threadname)
		self.scaner = scaner
	def run(self):
		try:
			while True:
				try:
					gridID = self.scaner.queue.get(False)
					fetchFlag = True
				except Empty:
					fetchFlag = False
				
				if fetchFlag:
					strHtml = self.scaner.tclient.getKarteZHtml(gridID)
					self.parseKarteZHtml(gridID, strHtml)
				elif self.scaner.endflag:
					print self.getName() + ' Finished'
					return
				else:
					time.sleep(random.randrange(10)/10.0)
		except:
			print 'exception catched in ' + self.getName()
			return
	
	def parseKarteZHtml(self, gridID, strHtml):
		index = strHtml.find('<map id="map' + gridID)
		strHtml = strHtml[index:]
		index = strHtml.find('</map>')
		strHtml = strHtml[:index]
		index = strHtml.find('<area href="karte.php?d=')
		strHtml = strHtml[index:]
		while(index >= 0):
			index2 = strHtml.find('/>') + 2
			strArea = strHtml[:index2]
			index2 = strArea.find('" coords="')
			Info = strArea[24:index2].replace('&amp;c=',' ').split()
			tempx = (int(Info[0]) - 1)%(self.scaner.config.ServerScale * 2 + 1) - self.scaner.config.ServerScale
			tempy = self.scaner.config.ServerScale - (int(Info[0]) - 1)/(self.scaner.config.ServerScale * 2 + 1)
			if self.scaner.config.rect[0] <= tempx 	and tempx <= self.scaner.config.rect[2] and self.scaner.config.rect[1] <= tempy and tempy <= self.scaner.config.rect[3] :
				index = strArea.find('onmouseover="map(')
				if index >=0 :
					strInfo = strArea[index+len('onmouseover="map('):strArea.find(')" onmouseout="map(')].replace('&lt;span class=\\\'t\\\'>&lt;i>','').replace('&lt;/i>&lt;/span>','').replace('\'','')
					self.scaner.VillageWriter.write(strInfo + '\n')
				else:
					if self.scaner.config.Output[1] or self.scaner.config.Output[2]:
						self.scaner.queueD.put(Info)
			strHtml = strHtml[40:]
			index = strHtml.find('<area href="karte.php?d=')
			strHtml = strHtml[index:]

# KarteDThread thread
class KarteDThread(threading.Thread):
	def __init__(self, threadname, scaner):
		threading.Thread.__init__(self, name = threadname)
		self.scaner = scaner
	def run(self):
		try:
			while True:
				try:
					gridID, cCode = self.scaner.queueD.get(False)
					fetchFlag = True
				except Empty:
					fetchFlag = False
				
				if fetchFlag:
					strHtml = self.scaner.tclient.getKarteDHtml(gridID, cCode)
					self.parseKarteDHtml(gridID, strHtml)
				elif self.scaner.endflagD:
					print self.getName() + ' Finished'
					return
				else:
					time.sleep(random.randrange(10)/10.0)
		except:
			print 'exception catched in ' + self.getName()
			return
	def parseKarteDHtml(self, gridID, strHtml):
		tempx, tempy = [int(gridID)%(self.scaner.config.ServerScale * 2 + 1) - (self.scaner.config.ServerScale + 1), self.scaner.config.ServerScale - int(gridID)/(self.scaner.config.ServerScale * 2 + 1)]
			
		strHtmlOld = strHtml
		index = strHtml.find('<div id="pr" class="map_details_right">')
		strHtml = strHtml[index:]
		index = strHtml.find('<div class="f10 b">') + len('<div class="f10 b">')
		strHtml = strHtml[index:]
		index = strHtml.find('</div>') + len('</div>')
		strInfo = strHtml[:index]
		strHtml = strHtml[index:]
		index = strHtml.find('</div>')
		strHtml = strHtml[:index]
		if strInfo.find(u'资源分配') >= 0:
			#farm
			Info = ['','','','',str(tempx),str(tempy)]
			index = strHtml.find('<td class="s7 b">')
			strHtml = strHtml[index + len('<td class="s7 b">'):]
			while index >=0:
				index = strHtml.find('</td>')
				strInfo = strHtml[:index]
				strHtml = strHtml[index + len('</td>'):]
				index = strHtml.find('<td>') + len('<td>')
				index2 = strHtml.find('</td>')
				strInfo2 = strHtml[index:index2]
				if strInfo2.find(u'伐木场') >= 0:
					Info[0] = strInfo
				elif strInfo2.find(u'泥坑') >= 0:
					Info[1] = strInfo
				elif strInfo2.find(u'铁矿场') >= 0:
					Info[2] = strInfo
				elif strInfo2.find(u'农场') >= 0:
					Info[3] = strInfo
				index = strHtml.find('<td class="s7 b">')
				strHtml = strHtml[index + len('<td class="s7 b">'):]
			self.scaner.FarmWriter.write(",".join(Info) + '\n')
		elif strInfo.find(u'军队') >= 0:
			#oasis
			pattern = r'''<img src="img/un/m/w(?P<id>\d+).jpg" id="resfeld">'''
			reresult = re.search(pattern, strHtmlOld)
			if reresult != None :
				strOasisType = reresult.group('id')
			else:
				strOasisType = ''
			Info = ['','','','','','','','','','',strOasisType,str(tempx),str(tempy)]
			index = strHtml.find('<td align="right">&nbsp;<b>')
			strHtml = strHtml[index + len('<td align="right">&nbsp;<b>'):]
			while index >=0 :
				index = strHtml.find('</b>')
				strInfo = strHtml[:index]
				strHtml = strHtml[index + len('</td>'):]
				index = strHtml.find('<td>') + len('<td>')
				index2 = strHtml.find('</td>')
				strInfo2 = strHtml[index:index2]
				if strInfo2.find(u'老鼠') >= 0:
					Info[0] = strInfo
				elif strInfo2.find(u'蜘蛛') >= 0:
					Info[1] = strInfo
				elif strInfo2.find(u'野猪') >= 0:
					Info[2] = strInfo
				elif strInfo2.find(u'蛇') >= 0:
					Info[3] = strInfo
				elif strInfo2.find(u'蝙蝠') >= 0:
					Info[4] = strInfo
				elif strInfo2.find(u'狼') >= 0:
					Info[5] = strInfo
				elif strInfo2.find(u'熊') >= 0:
					Info[6] = strInfo
				elif strInfo2.find(u'鳄鱼') >= 0:
					Info[7] = strInfo
				elif strInfo2.find(u'老虎') >= 0:
					Info[8] = strInfo
				elif strInfo2.find(u'大象') >= 0:
					Info[9] = strInfo
				index = strHtml.find('<td align="right">&nbsp;<b>')
				strHtml = strHtml[index + len('<td align="right">&nbsp;<b>'):]
			self.scaner.OasisWriter.write(",".join(Info) + '\n')
		else:
			print 'Invalid'

class Scaner(object):
	def __init__(self, config, tclient, writers):
		object.__init__(self)
		self.config = config
		self.tclient = tclient
		self.VillageWriter = writers[0]
		self.FarmWriter = writers[1]
		self.OasisWriter = writers[2]
		
		self.queue = Queue(128)
		self.endflag = False
		self.queueD = Queue(1024)
		self.endflagD = False
	def scan(self):
		threadNum = self.config.ThreadNum / 8
		if threadNum <= 0 :
			threadNum = 1
		threadNumD = self.config.ThreadNum - threadNum
		if threadNumD <= 0 :
			threadNumD = 1
		
		print 'Starting threads ...'
		producer = Producer('Producer', self)
		
		producer.start()
		
		#thread = KarteZThread('Z Thread ', self)
		#thread.run()
		#thread = KarteDThread('D Thread ', self)
		#thread.run()
		#sys.exit()
		
		threadlist = []
		for i in range(threadNum):
			thread = KarteZThread('Z Thread '+str(i+1), self)
			threadlist.append(thread)
			thread.start()
		
		threadlistD = []
		if self.config.Output[1] or self.config.Output[2]:
			for i in range(threadNumD):
				thread = KarteDThread('D Thread '+str(i+1), self)
				threadlistD.append(thread)
				thread.start()
		
		for i in threadlist:
			i.join()
		self.endflagD = True
		
		print 'all Get Z thread finished'
		
		for i in threadlistD:
			i.join()
		
		print 'all thread finished'

class ScanWriter(object):
	def __init__(self,filename,real):
		self.real = real
		if real:
			self.fs = codecs.open(filename,'w+a','UTF-8')
	def __del__(self):
		if self.real:
			self.fs.close()
	def write(self,str):
		if self.real:
			self.fs.write(str)
	
def main():
	init()
	config = Config()
	if not config.getConfig(sys.argv):
		sys.exit()
	
	dt = datetime.now()
	fslog = ScanWriter('log' + os.path.sep + dt.strftime('%Y%m%d %H%M%S') + '.log',config.log)
	
	tclient = TravianClient(config, fslog)
	if config.ReLogin:
		if not tclient.login():
			print 'Invalid username or password'
			sys.exit()
	else:
		#cookie check
		strHtml = tclient.getKarteZHtml(320801)
		if strHtml.find('login') > 0 and strHtml.find(u'用户名:') > 0 and strHtml.find(u'密码:') > 0 :
			print 'Cookie time out, relogin needed. Please use -l option or try --help option.'
			sys.exit()
	
	fsVillage = ScanWriter('result' + os.path.sep + dt.strftime('%Y%m%d %H%M%S') + 'Village.csv',config.Output[0])
	fsFarm = ScanWriter('result' + os.path.sep + dt.strftime('%Y%m%d %H%M%S') + 'Farm.csv',config.Output[1])
	fsOasis = ScanWriter('result' + os.path.sep + dt.strftime('%Y%m%d %H%M%S') + 'Oasis.csv',config.Output[2])
	fsVillage.write(u'村庄,玩家,居民,联盟,x,y\n')
	fsFarm.write(u'伐木场,泥坑,铁矿场,农场,x,y\n')
	fsOasis.write(u'老鼠,蜘蛛,野猪,蛇,蝙蝠,狼,熊,鳄鱼,老虎,大象,绿洲类型,x,y\n')
	
	scaner = Scaner(config, tclient, [fsVillage,fsFarm,fsOasis])
	scaner.scan()
	
def init():
	for n in ['log','result']:
		if os.path.exists(n):
			if os.path.isfile(n):
				os.remove(n)
				os.mkdir(n)
		else:
			os.mkdir(n)

if __name__ == '__main__':
	main()
