#!/usr/bin/env python

import signal
from sys import argv, exit
from PyQt4.QtCore import Qt, QString, QSignalMapper, pyqtSignal
from PyQt4.QtGui import *

# Most indices are zero-indexed. The exception is is the row
# number displayed in the GUI table.

# SJM June 2017 Adapt code for 12x12 to 20x20 router.

class RouterControl(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('ROV Jason SmartHub Control')
#        self.setFixedSize(260, 515)
        self.setFixedSize(300, 815)
        self.router_dim = 20

        # Set up the GUI
        self.text_display = QLabel("Info Box")
        self.text_display.setFrameShape(QFrame.WinPanel)
        self.text_display.setFrameShadow(QFrame.Raised)
        self.text_display.setWordWrap(True)
        self.do_button = QPushButton('Make It So')
        self.do_button.clicked.connect(self.on_do_clicked)
        self.tw = SmartHubTableWidget()
        self.tw.new_ins.connect(self.on_new_inchoice)
        self.tw.new_fg.connect(self.on_new_fg_routing)
        self.createEvents_cb = QCheckBox("Events to VVan")
        self.createEvents_cb.setChecked(False)
        self.createEvents_cb.toggled.connect(self.on_cb_toggled)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.text_display)
        self.layout.addWidget(self.tw)
        self.layout.addWidget(self.createEvents_cb)
        self.layout.addWidget(self.do_button)
        self.setLayout(self.layout)

        self.shc = SmartHubComm()
        self.shc.new_inouts.connect(self.on_new_smhub)

        vvanIP = "198.17.154.221"
        vvanSocket = 10502
        fgIP = "198.17.154.194"
	fgSocket=10520
        self.event_writer = UDP_sendEvent(vvanSocket, vvanIP)
        self.fg_writer = UDP_write2FG(fgSocket, fgIP)

        # June 2017 SJM Additions to send info to framegrabber
        # Define the two channels feeding the framegrabber Epiphans
        # Define using one-based addressing, convert to internal 0-based.
        self.fg1_out_index = 19
        self.fg2_out_index = 20

        self.ini_smb_in_portlist = range(0, self.router_dim)
        self.ini_smb_out_portlist = range(0, self.router_dim)
        self.ini_smb_in_labellist = []
        self.ini_smb_out_labellist = []
        self.ini_smb_in_vidrtports = []
        self.ini_smb_out_vidrtports = []

        model = self.shc.get_model_info()
        #print model

        self.events_list = QStringList()
        self.events_list.clear()

    # June 2017 SJM added to send signal to FG host by UDP
    def on_new_fg_routing(self, FG1_src_str, FG2_src_str):

        outstr = "FG1=%s FG2=%s" % (FG1_src_str, FG2_src_str)
        self.fg_writer.write2FG(outstr)

    def on_new_inchoice(self, row, dl_index, event_str):

        self.events_list.append(event_str)

        label = self.ini_smb_in_labellist[dl_index]
        self.ul_inlist[row] = int(self.ini_smb_in_portlist[dl_index])

        outstr = "row=%d index=%d inlabel= %s" % (row, dl_index, label)
        self.text_display.setText(outstr)

        # June 2017 SJM Determine the sources being fed to the outputs
        # that go to the Framegrabbing Epiphans.

#        fg1_src_label = self.ini_smb_in_label[self.fg1_out_index]
#        fg2_src_label = self.ini_smb_in_label[self.fg2_out_index]
        
 
    def on_do_clicked(self):

        self.text_display.setText("Updating SmartHub")
        outmsg=self.build_vid_route_msg()
        self.shc.set_new_routes(outmsg)

        if self.createEvents_cb.isChecked():
            self.event_writer.sendEvent(self.events_list)
        self.events_list.clear()

    def build_vid_route_msg(self):

        vrm = QByteArray()

        msg= "VIDEO OUTPUT ROUTING:\r\n"
        vrm.append(msg)

        for i in range(0, self.router_dim):
            msg="%d %d\r\n" % (self.ul_outlist[i],self.ul_inlist[i])
            vrm.append(msg)
        
        term_str = "\r\n"
        vrm.append(term_str)

        return vrm
                                
    def on_new_smhub(self, ipl, ill, opl, oll, portsin, portsout):

        self.ini_smb_in_portlist = ipl
        self.ini_smb_out_portlist = opl
        self.ini_smb_in_labellist = ill
        self.ini_smb_out_labellist = oll
        self.ini_smb_in_vidrtports = portsin
        self.ini_smb_out_vidrtports = portsout

        # Initialize the route upload lists to the current state of the SmartHub
        self.ul_inlist = self.ini_smb_in_vidrtports
        self.ul_outlist = self.ini_smb_out_vidrtports

        self.tw.show_smhub_inouts(self.ini_smb_in_labellist, self.ini_smb_out_labellist, self.ini_smb_in_vidrtports)

    def on_cb_toggled(self, checked):
        if checked:
            self.text_display.setText('Virtual Van events on')
        else:
            self.text_display.setText('Virtual Van events off')
            self.events_list.clear()

def sigint_handler(*args):
    sys.stderr.write('\r')
    QApplication.quit()

if __name__ == "__main__":

    signal.signal(signal.SIGINT, sigint_handler)

    try:
        execfile("./router_comms.py")
    except Exception as e:
        print "error opening or running ./router_comms.py", e

    try:
        execfile("./display_table.py")
    except Exception as e:
        print "error opening or running /home/scotty/src/SmartHubControl/display_table.py", e

    try:
        execfile("./udp_sender.py")
    except Exception as e:
        print "error opening or running /home/scotty/src/SmartHubControl/udp_sender.py", e

    qapp=QApplication(argv)

    rc=RouterControl()
    rc.show()
    rc.raise_()
    exit(qapp.exec_())

        

        
