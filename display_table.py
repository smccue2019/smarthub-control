#!/usr/bin/env python

from PyQt4.QtCore import Qt, QString, QSignalMapper, pyqtSignal
from PyQt4.QtGui import *


class SmartHubTableWidget(QTableWidget):

    new_ins = pyqtSignal(int, int, str, name = 'new_ins')
    new_fg = pyqtSignal(str, str, name = 'new_fg')

    def __init__(self, header_list = ['Smarthub 20x20 In', 'Smarthub 20x20 Out']):
        QWidget.__init__(self)

        self.signalMapper = QSignalMapper()
        self.signalMapper.mapped[QWidget].connect(self.on_signalMapper_mapped)

        self.router_dim = 20
        self.setRowCount(self.router_dim)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(header_list)
#	self.setHorizontalHeaderResizeMode(QHeaderView.ResizeToContents)
#        self.setStretchLastSection(True)

# June 2017 SJM Added to support signalling by UDP the framegrabber host/program.
        self.out_to_fg1_portnum = 1       #  1-indexed 
        self.out_to_fg2_portnum = 2       #  1-indexed 

        self.out_to_fg1_portnum_ = self.out_to_fg1_portnum - 1       #  0-indexed 
        self.out_to_fg2_portnum_ = self.out_to_fg2_portnum - 1       #  0-indexed

    def on_signalMapper_mapped(self, changed_dl):
        event = QString()

        rowval = int(changed_dl.property("row").toString())
        old_label = self.in_list[rowval]
        new_index = changed_dl.currentIndex()
        new_input = self.in_list[new_index]
        output = self.dest_list[rowval]
        # List indexing, etc is zero-based, but displayed rows are one-based
        display_row = rowval + 1
        display_index = new_index + 1
        event = "SmartHub input %s (port %d) routed to output %s (port %d)" % (new_input, display_index, output, display_row)

        # June 2017 SJM Added to support signalling by UDP the framegrabber host/program.
        # SHOULD IT BE rowval OR new_index? fg_portnum 0-indexed or 1-indexed?
        if rowval == self.out_to_fg1_portnum_ or  rowval == self.out_to_fg2_portnum_ :
            self.FG1_src_str = self.in_list[self.out_to_fg1_portnum_]
            self.FG2_src_str = self.in_list[self.out_to_fg2_portnum_]
            self.new_fg.emit(self.FG1_src_str, self.FG2_src_str)            

        self.new_ins.emit(rowval, new_index, event)


    def show_smhub_inouts(self, in_list, dest_list, in_index_list):

        self.blockSignals(True)

        self.in_list = in_list
        self.dest_list = dest_list
        self.current_index_list = in_index_list

        # First column, drop lists of variable content
        for row in range(0,self.router_dim):
            dli = self.droplist(in_list, dest_list[row])
            dli.setProperty("row", row)
            self.setCellWidget(row, 0, dli)
            self.signalMapper.setMapping(dli, dli)

        # Set the labels in the first column combo boxes
        # to the current settings of the SmartHub
        for irow in range(0, self.router_dim):
            dli = self.cellWidget(irow, 0)
            dli.setCurrentIndex(in_index_list[irow])

        # Second column, fixed list of destinations
        for row in range(0, len(dest_list) ):
            dest_str = "-> %s" % dest_list[row]
            item = QTableWidgetItem(dest_str, 0)
            self.setItem(row, 1, item)

        self.blockSignals(False)

    def droplist(self, input_list, dest_label):
        dl = QComboBox()
	dl.setStyleSheet("QComboBox {font-size:12px}")
        dl.currentIndexChanged.connect(self.signalMapper.map)

        if not dest_label == 'Null':
            li = []
            for i in range(0, len(input_list) ):
                li.append(input_list[i])
            dl.addItems(li)

        return dl

