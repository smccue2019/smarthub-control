#!/usr/bin/env python

import sys,socket
#from PyQt4.QtCore import 
#from PyQt4.QtGui import *
from PyQt4 import QtNetwork

# Simple sender of SmartHub events to virtual van server at 198.17.154.221
# SJM June 2017 Add sending of event to the framegrabber host at 198.17.154.194
# SJM Aug 2020 Improve sending to FG at .199.

class UDP_sendEvent(QObject):

        def __init__(self, send_port, targetIP, parent=None):
            super(UDP_sendEvent, self).__init__(parent)

	    self.vvan_port = send_port
	    self.vvan_IP = targetIP

            try:
                self.vvsock = QtNetwork.QUdpSocket(self)
            except:
                print "Trouble opening UDP on socket %d" % (self.vvan_port)


        def sendEvent(self, eventslist):
            for event in eventslist:
                vv_msg = "EVT %s DLG: %s" % (systime(), event)
		self.vvsock.writeDatagram(vv_msg, self.vvan_IP, self.vvan_port)


class UDP_write2FG(QObject):

        def __init__(self, send_port, targetIP, parent=None):
            super(UDP_write2FG, self).__init__(parent)

	    fg_IP = "198.17.154.199"
            self.fg_port = 10522
            self.target_IP = QtNetwork.QHostAddress(fg_IP)

            try:
                self.fgsock = QtNetwork.QUdpSocket(self)
            except:
                print "Trouble opening UDP on socket %d" % (self.fg_port)


        def write2FG(self, fg_msg):

		self.fgsock.writeDatagram(fg_msg, self.fg_IP, self.fg_port)

def num (s):
	try:
		return int(s)
	except ValueError as e:
		return float(s)

def systime():
	now = QDateTime.currentDateTime()
	systime = now.toString("yyyyMMddhhmmss")
	return systime
