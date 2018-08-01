'''
Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.
Copyright 2016. UChicago Argonne, LLC. This software was produced
under U.S. Government contract DE-AC02-06CH11357 for Argonne National
Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
U.S. Department of Energy. The U.S. Government has rights to use,
reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should
be clearly marked, so as not to confuse it with the version available
from ANL.
Additionally, redistribution and use in source and binary forms, with
or without modification, are permitted provided that the following
conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in
      the documentation and/or other materials provided with the
      distribution.
    * Neither the name of UChicago Argonne, LLC, Argonne National
      Laboratory, ANL, the U.S. Government, nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

import h5py
import numpy as np
import string
from XRF_Boundary import *
from CheckBoxDialog import QMessageBoxWithCheckBox
from os.path import expanduser

try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except ImportError:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *


class CoarseScanWidget(QWidget):

    def __init__(self, parent, path=None):
        super(CoarseScanWidget, self).__init__()

        self.scan_boundary = XRFBoundary()
        self.file_path = None
        self.file_list = None

        self.tree_view = QTreeView()
        self.list_view = QListWidget()

        files_hbox = QHBoxLayout()
        files_hbox.addWidget(self.tree_view)
        files_hbox.addWidget(self.list_view)

        if path is None:
            path = expanduser("~")

        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(path)
        self.dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)

        self.tree_view.setModel(self.dir_model)

        self.tree_view.setRootIndex(self.dir_model.index(path))
        self.tree_view.setColumnWidth(0,200)

        # Enable selection of multiple files.
        self.list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.select_element_button = QPushButton('Select Element')
        self.select_element_button.setStyleSheet('background-color: yellow')
        self.select_element_button.setMaximumSize(200, 25)
        self.select_element_button.setToolTip('Open a window to select an element.')
        self.select_element_button.clicked.connect(self.on_select_element_button_click)

        self.build_scan_button = QPushButton('Build Scan')
        self.build_scan_button.setStyleSheet('background-color: yellow')
        self.build_scan_button.setMaximumSize(200, 25)
        self.build_scan_button.setToolTip('Calculate fine scan boundaries.')
        self.build_scan_button.clicked.connect(self.on_build_scan_button_click)

        self.show_plots_button = QPushButton('Show Plots')
        self.show_plots_button.setStyleSheet('background-color: yellow')
        self.show_plots_button.setMaximumSize(200, 25)
        self.show_plots_button.setToolTip('Show plots with calculated boundaries.')
        self.show_plots_button.clicked.connect(self.on_show_plots_button_click)

        self.label_theta = QLabel('Delta Theta')
        self.label_theta.setAlignment(Qt.AlignRight)
        self.text_theta = QLineEdit()
        self.text_theta.setMinimumWidth(80)
        self.text_theta.setMaximumSize(100, 20)

        self.label_element = QLabel('Element')
        self.label_element.setAlignment(Qt.AlignRight)
        self.text_element = QLineEdit()
        self.text_element.setReadOnly(True)
        self.text_element.setMinimumWidth(80)
        self.text_element.setMaximumSize(100, 20)

        self.label_coefficient = QLabel('Boundary coefficient')
        self.label_coefficient.setAlignment(Qt.AlignRight)
        self.text_coefficient = QLineEdit()
        self.text_coefficient.setMinimumWidth(80)
        self.text_coefficient.setMaximumSize(100, 20)

        self.label_stage_pv = QLabel('Rotation Stage PV')
        self.label_stage_pv.setAlignment(Qt.AlignRight)
        self.text_stage_pv = QLineEdit()
        self.text_stage_pv.setMinimumWidth(80)
        self.text_stage_pv.setMaximumSize(100, 20)

        button_vbox = QVBoxLayout()
        button_vbox.addWidget(self.select_element_button)
        button_vbox.addWidget(self.build_scan_button)
        button_vbox.addWidget(self.show_plots_button)

        text_form_layout = QFormLayout()
        text_form_layout.addRow(self.label_element, self.text_element)
        text_form_layout.addRow(self.label_coefficient, self.text_coefficient)
        text_form_layout.addRow(self.label_theta, self.text_theta)
        text_form_layout.addRow(self.label_stage_pv, self.text_stage_pv)

        hbox = QHBoxLayout()
        hbox.addLayout(button_vbox)
        hbox.addLayout(text_form_layout)

        widget_layout = QVBoxLayout()
        widget_layout.addLayout(files_hbox)
        widget_layout.addLayout(hbox)

        self.setLayout(widget_layout)

        self.tree_view.clicked.connect(self.on_directory_clicked)
        self.list_view.itemSelectionChanged.connect(self.on_files_selected_changed)

        return

    def on_files_selected_changed(self):

        items = self.list_view.selectedItems()
        self.file_list = []
        for item in items:
            self.file_list.append(item.text())
        list.sort(self.file_list)

        return

    def on_directory_clicked(self, index):

        self.file_path = self.dir_model.fileInfo(index).absoluteFilePath()
        self.list_view.clear()
        file_list = os.listdir(self.file_path)
        for file in file_list:
            if '.h5' in file:
                self.list_view.addItem(file)

        return

    def on_select_element_button_click(self):

        stage_pv = self.text_stage_pv.text()

        if self.file_path is None and stage_pv is '':
            err_msg = QMessageBox()
            err_msg.setIcon(QMessageBox.Critical)
            err_msg.setText('Missing Information')
            err_msg.setInformativeText('No files or stage PV')
            err_msg.setDetailedText('Please make sure that files have been selected in the browser window and a valid'
                                    ' PV has been given for the rotation stage.')
            err_msg.setStandardButtons(QMessageBox.Ok)

            ret_val = err_msg.exec_()

            return
        else:
            self.scan_boundary.open_files(self.file_path, self.file_list, stage_pv)
            self.scan_boundary.create_element_list()
            elem_list = self.scan_boundary.get_element_list()
            elem_dialog = QMessageBoxWithCheckBox(elem_list)
            ret_val, elem_dict = elem_dialog.exec_()

            for key, value in elem_dict.items():
                if value.isChecked():
                    self.text_element.setText(key)

        return

    def on_build_scan_button_click(self):

        coefficient = int(self.text_coefficient.text())
        element = self.text_element.text()
        stage_pv = self.text_stage_pv.text()

        element_index = self.scan_boundary.get_element_index(element)

        self.scan_boundary.calc_xy_bounds(self.file_path, coefficient, stage_pv, element_index)

        return

    def on_show_plots_button_click(self):

        self.scan_boundary.show_roi_box()

        return