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

import getopt

class Config(object):
    def __init__(self):
        #Some default settings
        self.ServerName = 's1.travian.cn'
        self.UserName = 'travian0'
        self.PassWord = 'travian0'
        self.rect = [0,7,0,7]
        self.ThreadNum = 32
        self.RetryNum = 5
        self.ReLogin = False
        #Output mask for [Village, farm, oasis]
        self.Output = [True,True,True]
        self.ServerScale = 400
        self.log = False
        
    def getConfig(self ,argv):
        arg = argv[1:]
        try:
            opts, arg = getopt.getopt(arg, 'hlo:s:c:u:p:t:r:', ['help', 'server=','scale=','user=','pass=','thread=','retry=','login','output=','version','savelog'])
        except getopt.GetoptError:
            # print help information and exit:
            self.usage()
            return False
        #deal arguments
        try:
            for o, a in opts:
                if o in ("-h", "--help"):
                    self.usage()
                    return False
                if o in ("-l", "--login"):
                    self.ReLogin = True
                if o in ("-s", "--server"):
                    self.ServerName = a
                if o in ("-c", "--scale"):
                    if int(a) < 10 :
                        raise OptionException('scale must more than or equal to 10')
                    self.ServerScale = int(a)
                if o in ("-u", "--user"):
                    self.UserName = a.decode('GB18030')
                    if self.UserName[0] in (u'\'', u'"'):
                        self.UserName = self.UserName[1:]
                    if self.UserName[-1] in (u'\'', u'"'):
                        self.UserName = self.UserName[:-1]
                if o in ("-p", "--pass"):
                    self.PassWord = a.decode('GB18030')
                    if self.PassWord[0] in (u'\'', u'"'):
                        self.PassWord = self.PassWord[1:]
                    if self.PassWord[-1] in (u'\'', u'"'):
                        self.PassWord = self.PassWord[:-1]
                if o in ("-t", "--thread"):
                    if int(a) < 2 :
                        raise OptionException('thread number should more than 1')
                    self.ThreadNum = int(a)
                if o in ("-r", "--retry"):
                    if int(a) < 1 :
                        raise OptionException('retrys should more than 0')
                    self.RetryNum = int(a)
                if o in ("-o", "--output"):
                    self.Output = [False,False,False]
                    a = str(a)
                    if a.find('v') >= 0:
                        self.Output[0] = True
                    if a.find('f') >= 0:
                        self.Output[1] = True
                    if a.find('o') >= 0:
                        self.Output[2] = True
                    if not(self.Output[0] or self.Output[1] or self.Output[2]) :
                        raise OptionException('output should have one on at least')
                if o in ('--savelog',):
                    self.log = True
                if o in ('--version',):
                    self.printVersion()
                    return False
                
            if len(arg) == 2:
                x1,y1 = [int(k) for k in arg[0].replace('\'','').replace('"','').split(':')]
                x2,y2 = [int(k) for k in arg[1].replace('\'','').replace('"','').split(':')]
                if x1 < -self.ServerScale or x1 > self.ServerScale or x2 < -self.ServerScale or x2 > self.ServerScale \
                or y1 < -self.ServerScale or y1 > self.ServerScale or y2 < -self.ServerScale or y2 > self.ServerScale :
                    raise OptionException('start and end coordinate should be in map')
                #x1 must less than x2
                if x1>x2:
                    tmp=x1
                    x1=x2
                    x2=tmp
                #y1 must less than y2
                if y1>y2:
                    tmp=y1
                    y1=y2
                    y2=tmp
                self.rect = [x1,y1,x2,y2]
            else:
                raise OptionException('coordinate option error')
                
            return True
        except OptionException, e:
            print e.info
            self.usage()
            return False
                
    def printVersion(self):
        print 'Travian scaner 0.0.6 (2007/09/07)'
        print 'Written by sevenever.'
        print 'Copyright (C) 2007 Sevenever.'
        print 'This is free software; see the source for copying conditions.  There is NO'
        print 'warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'
    
    def usage(self):
        print '''Usage: scan [-options] startX:startY endX:endY

Scan travian(http://www.travian.com) server for map infomation.
where options include:
    -h, --help   Show this help message.
    -l, --login  Relogin with username and password given.
    -s, --server=HostNameOrIP
                 The travian server host name or IP address(without 'http://' prefix).
    -c, --scale=value
                 The scale of map on this server, 400 usually.
    -u, --user=username
                 Username to login.
    -p, --pass=password
                 Password to login.
    -t, --thread=value
                 Max thread to fetch webpages(not exactly).
    -r, --retry=value
                 Max retrys while fetch webpages(not exactly).
    -o, --output=type
                 Output option.Config type(s) of result will be output.
                 Which type is one of this three:
                      v for Village
                      f for oasis with resource
                      o for oasis with beast
                 or combine of them.
        --savelog
                Save log.
        --version
                print version information and exit.
    
    Report bugs to <seven@sevenever.com>.'''

class OptionException(Exception):
    def __init__(self,info):
        self.info = info
    def __str__(self):
        return repr(self.info)
