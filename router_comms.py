#!/usr/bin/env python

import sys, time, string, exceptions, re, threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket

class SmartHubComm(QDialog):

    new_inouts = pyqtSignal(QStringList, QStringList, QStringList, QStringList, list, list, name = 'new_smhub')

    def __init__(self, parent=None):
        super(SmartHubComm, self).__init__(parent)

        self.smarthubIP = '198.17.154.164'
        self.router_dim = 20
        self.min_smhub_status_size = 693
        self.msg_total = 0
        self.smhub_status_block = QString()
        self.raw_model_string = QString()
        self.this_is_set_smhub_phase = False

        self.start_comms_with_smhub()

    def get_model_info(self):
        print self.raw_model_string
        # Model name: Blackmagic Smart Videohub 12 x 12
        bmre = re.compile('Blackmagic Smart Videohub')
 #       (blah, model) = self.raw_model_string.split(':')

        #if bmre.match(model):
         #   print "Needs to be finished"
                    
        return self.raw_model_string

    def on_tcp_error(self, connect_error):

        if connect_error == QAbstractSocket.RemoteHostClosedError:
            print "ERROR: Remote host closed"
        elif connect_error == QAbstractSocket.HostNotFoundError:
            print "ERROR: Host was not found"
        elif connect_error == QAbstractSocket.ConnectionRefusedError:
            print "ERROR: The connection was refused by the peer"
        else:
            print "The following error occurred: %l" % self.sock.errorString()

    def on_ready_read(self):

        instream = QTextStream(self.sock)
        inblock = QString()

        bytes_avail = self.sock.bytesAvailable()
        inblock = instream.readAll() 
        self.smhub_status_block += inblock
        self.msg_total = self.msg_total + bytes_avail

        if self.msg_total >= self.min_smhub_status_size:
            self.smhub_dump_has_been_read = True
            if not self.this_is_set_smhub_phase:
                self.parse_hub_data(self.smhub_status_block)
            else:
                self.smhub_reply = inblock
                #print self.smhub_reply

    def parse_hub_data(self, fullblock):

        blocklist = QStringList()
        blocklist = fullblock.split('\n')

        ila = QStringList()
        ola = QStringList()
        vra = QStringList()
        inportl = []
        inlabell = []
        outportl = []
        outlabell = []
        routein = []
        routeout = []

        modre = QRegExp('^Model name')
        ilre = QRegExp('^INPUT LABELS:$')
        olre = QRegExp('^OUTPUT LABELS:$')
        vore = QRegExp('^VIDEO OUTPUT ROUTING:$')

        modind = blocklist.indexOf(modre)
        self.raw_model_string = QString(blocklist[modind])
        # Model name: Blackmagic Smart Videohub 12 x 12

        # Find lines starting the input label list, output label list, and routing list"
        ilind = blocklist.indexOf(ilre)
        olind = blocklist.indexOf(olre)
        voind = blocklist.indexOf(vore)
  
        # Read in the input and output label blocks, and the routing list
#        for i in range((ilind+1), (ilind+13)):
        for i in range((ilind+1), (ilind+(self.router_dim+1))):
            ila.append(QString(blocklist[i]))

#        for i in range((olind+1), (olind+13)):
        for i in range((olind+1), (olind+(self.router_dim+1))):
            ola.append(QString(blocklist[i]))

        # The routing list is just two numbers (input port and matched output port).
#        for i in range((voind+1), (voind+13)):
        for i in range((voind+1), (voind+(self.router_dim+1))):
            vra.append(QString(blocklist[i]))

        # Parse the label lists and populate a data structure to hold the labels
        for i in range(0, ila.count() ):
            line = QString(ila[i])
            #print line
            try:
                [port, label] = line.split(' ', QString.SkipEmptyParts)
            except:
                try:
                    [port, label1, label2] = line.split(' ')
                    label = label1 + " " + label2
                except:
                    try:
                        [port, label1, label2, label3] = line.split(' ')
                        label = label1 + " " + label2 + " " + label3
                    except:
                        [port, label1, label2, label3, label4] = line.split(' ')
                        label = label1 + " " + label2 + " " + label3 + " " + label4


            inportl.append(port)
            inlabell.append(label)

        for i in range(0, ola.count() ):
            line = QString(ola[i])
            #print line
            try:
                [port, label] = line.split(' ',QString.SkipEmptyParts)
            except:
                try:
                    [port, label1, label2] = line.split(' ')
                    label = label1 + " " + label2
                except:
                    try:
                        [port, label1, label2, label3] = line.split(' ')
                        label = label1 + " " + label2 + " " + label3
                    except:
                        [port, label1, label2, label3, label4] = line.split(' ')
                        label = label1 + " " + label2 + " " + label3 + " " + label4

            outportl.append(port)
            outlabell.append(label)

        for i in range(0, vra.count() ):
            line = QString(vra[i])
            try:
                [outport, inport] = line.split(' ')
                inport = int(inport)
                outport = int(outport)
            except:
                print "Failed to parse route line %d" % i
            routein.append(inport)
            routeout.append(outport)

        self.new_smhub.emit(inportl, inlabell, outportl, outlabell, routein, routeout)
                                        
    def start_comms_with_smhub(self):
        self.sock = QTcpSocket()
        self.sock.error.connect(self.on_tcp_error)
        self.sock.readyRead.connect(self.on_ready_read)

        try:
            self.sock.connectToHost(self.smarthubIP, 9990)
            if self.sock.waitForConnected(1000):
                print "Connected"
            else:
                errstr = "Comm Err"
                print errstr
        except:
            print self.sock.SocketError()

    def set_new_routes(self, vid_route_msg):
#        print "============== New Router Out List ================"
#        print vid_route_msg
        self.this_is_set_smhub_phase = True

        if not self.sock.isOpen():
            try:
                self.sock.connectToHost(self.smarthubIP, 9990)
                if self.sock.waitForConnected(100):
                    print "Connected"
                else:
                    errstr = "Comm Err"
                    print errstr
                # A new connection means a new dump from theSmarthub
                # Since we don't want its info, pull it in but do
                # nothing with it.
                self.start_hub_retrieve()
            except:
                print self.sock.SocketError()
                return

        # Now that we're past that, set the routes
        # TCP output here
        bytes_out = self.sock.write(vid_route_msg)
        self.sock.flush()

