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

from XRF_Boundary import *
from CreateScriptWidget import *
from CheckBoxDialog import QMessageBoxWithCheckBox
from os.path import expanduser

try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except ImportError:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal

class CoarseScanWidget(QWidget):
    def __init__(self, parent, path=None):
        super(CoarseScanWidget, self).__init__()

        #  self.parent = CreateScriptWidget()
        self.parent = parent
        self.scan_boundary = XRFBoundary()
        self.scan_boundary.roiChangedSig.connect(self.bounds_changed)
        self.file_path = None
        self.file_list = None
        self.scan_params = None
        self.scan_params2 = None
        self.x_pixel_size = None
        self.y_pixel_size = None
        self.dwell_time = None
        self.eta = None
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

        self.tree_view.setRootIndex(self.dir_model.index('/'))
        self.tree_view.setColumnWidth(0,200)

        #  Enable selection of multiple files.
        self.list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.select_files_button = QPushButton('Select Files')
        self.select_files_button.setStyleSheet('background-color: yellow')
        self.select_files_button.setMaximumSize(200, 25)
        self.select_files_button.setToolTip('Save the list of selected files.')
        self.select_files_button.clicked.connect(self.on_select_files_button_click)

        self.select_element_button = QPushButton('Select Element')
        self.select_element_button.setStyleSheet('background-color: yellow')
        self.select_element_button.setMaximumSize(200, 25)
        self.select_element_button.setToolTip('Open a window to select an element.')
        self.select_element_button.clicked.connect(self.on_select_element_button_click)

        self.bound_y = QCheckBox("Bound y")
        self.bound_y.setChecked(True)

        self.build_scan_button = QPushButton('Build Scan')
        self.build_scan_button.setStyleSheet('background-color: yellow')
        self.build_scan_button.setMaximumSize(200, 25)
        self.build_scan_button.setToolTip('Calculate build scan parameters from boundaries.')
        self.build_scan_button.clicked.connect(self.on_build_scan_button_click)

        self.show_plots_button = QPushButton('Adjust ROIs')
        self.show_plots_button.setStyleSheet('background-color: yellow')
        self.show_plots_button.setMaximumSize(200, 25)
        self.show_plots_button.setToolTip('Show plots with calculated boundaries.')
        self.show_plots_button.clicked.connect(self.on_show_plots_button_click)

        self.label_x_size = QLabel('X step size (mm)')
        self.label_x_size.setAlignment(Qt.AlignRight)
        self.text_x_size = QLineEdit('0.001')
        self.text_x_size.setMinimumWidth(70)
        self.text_x_size.setMaximumSize(70, 20)
        #  self.text_x_size.textChanged.connect(self.enable_build_scan_button)

        self.label_ETA = QLabel('ETA hours:min:seconds')
        self.label_ETA.setAlignment(Qt.AlignLeft)
        self.text_ETA = QLineEdit('0: 0: 0')
        self.text_ETA.setMaximumSize(200, 25)

        self.label_y_size = QLabel('Y step size (mm)')
        self.label_y_size.setAlignment(Qt.AlignRight)
        self.text_y_size = QLineEdit('0.001')
        self.text_y_size.setMinimumWidth(70)
        self.text_y_size.setMaximumSize(70, 20)
        #  self.text_y_size.textChanged.connect(self.enable_build_scan_button)

        self.label_dwell = QLabel('Dwell time (ms)')
        self.label_dwell.setAlignment(Qt.AlignRight)
        self.text_dwell = QLineEdit('50')
        self.text_dwell.setMinimumWidth(70)
        self.text_dwell.setMaximumSize(70, 20)
        #  self.text_dwell.textChanged.connect(self.enable_build_scan_button)

        self.label_angle_offset = QLabel('Angle offset')
        self.label_angle_offset.setAlignment(Qt.AlignRight)
        self.text_angle_offset = QLineEdit('0')
        self.text_angle_offset.setMinimumWidth(70)
        self.text_angle_offset.setMaximumSize(70, 20)
        #  self.text_angle_offset.textChanged.connect(self.enable_build_scan_button)

        self.label_element = QLabel('Element')
        self.label_element.setAlignment(Qt.AlignRight)
        self.text_element = QLineEdit()
        self.text_element.setReadOnly(True)
        self.text_element.setMinimumWidth(70)
        self.text_element.setMaximumSize(70, 20)

        self.label_coefficient = QLabel('Boundary Coefficient')
        self.label_coefficient.setAlignment(Qt.AlignRight)
        self.text_coefficient = QLineEdit()
        self.text_coefficient.setMinimumWidth(70)
        self.text_coefficient.setMaximumSize(70, 20)

        self.label_boundary_offset_x = QLabel('X offset left,right (mm)')
        self.label_boundary_offset_x.setAlignment(Qt.AlignRight)
        self.text_boundary_offset_x = QLineEdit('0,0')
        self.text_boundary_offset_x.setMinimumWidth(70)
        self.text_boundary_offset_x.setMaximumSize(70, 20)

        self.label_boundary_offset_y = QLabel('Y offset top,bottom (mm)')
        self.label_boundary_offset_y.setAlignment(Qt.AlignRight)
        self.text_boundary_offset_y = QLineEdit('0,0')
        self.text_boundary_offset_y.setMinimumWidth(70)
        self.text_boundary_offset_y.setMaximumSize(70, 20)

        self.label_theta = QLabel('Angle Increment')
        self.label_theta.setAlignment(Qt.AlignRight)
        self.text_theta = QLineEdit()
        self.text_theta.setMinimumWidth(70)
        self.text_theta.setMaximumSize(70, 20)

        self.label_stage_pv = QLabel('Rotation Stage PV')
        self.label_stage_pv.setAlignment(Qt.AlignRight)
        self.text_stage_pv = QLineEdit()
        self.text_stage_pv.setMinimumWidth(80)
        self.text_stage_pv.setMaximumSize(100, 20)

        self.text_num_files = QLineEdit()
        self.text_num_files.setReadOnly(True)
        self.text_num_files.setMinimumWidth(80)
        self.text_num_files.setMaximumSize(200, 20)
        self.text_num_files.setText('0 Files Selected')

        self.select_element_button.setDisabled(True)
        self.show_plots_button.setDisabled(True)
        self.build_scan_button.setDisabled(True)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.select_files_button, 0, 0)
        grid_layout.addWidget(self.select_element_button, 1, 0)
        grid_layout.addWidget(self.build_scan_button, 2, 0)
        grid_layout.addWidget(self.show_plots_button, 3, 0)
        grid_layout.addWidget(self.label_ETA,4,0)

        grid_layout.addWidget(self.text_num_files, 0, 1)
        grid_layout.addWidget(self.bound_y,2,1)
        grid_layout.addWidget(self.text_ETA,4,1)

        grid_layout.addWidget(self.label_x_size, 0, 2)
        grid_layout.addWidget(self.label_y_size, 1, 2)
        grid_layout.addWidget(self.label_dwell, 2, 2)
        grid_layout.addWidget(self.label_theta, 0, 4)
        grid_layout.addWidget(self.text_x_size, 0, 3)
        grid_layout.addWidget(self.text_y_size, 1, 3)
        grid_layout.addWidget(self.text_dwell, 2, 3)
        grid_layout.addWidget(self.text_theta, 0, 5)

        grid_layout.addWidget(self.label_element, 3, 2)
        grid_layout.addWidget(self.label_angle_offset, 1, 4)
        grid_layout.addWidget(self.label_coefficient, 2, 4)
        grid_layout.addWidget(self.label_boundary_offset_x, 3, 4)
        grid_layout.addWidget(self.label_boundary_offset_y, 4, 4)
        grid_layout.addWidget(self.label_stage_pv, 4, 2)
        grid_layout.addWidget(self.text_element, 3, 3)
        grid_layout.addWidget(self.text_angle_offset, 1, 5)
        grid_layout.addWidget(self.text_coefficient, 2, 5)
        grid_layout.addWidget(self.text_boundary_offset_x, 3, 5)
        grid_layout.addWidget(self.text_boundary_offset_y, 4, 5)
        grid_layout.addWidget(self.text_stage_pv, 4, 3)

        widget_layout = QVBoxLayout()
        widget_layout.addLayout(files_hbox)
        widget_layout.addLayout(grid_layout)

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
        #tmp
        # self.file_path = '/home/fabricio/scans/coarsescan'
        self.list_view.clear()
        file_list = os.listdir(self.file_path)
        #tmp
        # file_list = ['2xfm_0046.h5', '2xfm_0047.h5', '2xfm_0048.h5', '2xfm_0049.h5', '2xfm_0044.h5', '2xfm_0045.h5', '2xfm_0043.h5']
        for file in file_list:
            if '.h5' in file:
                self.list_view.addItem(file)
        return

    def on_select_files_button_click(self):
        #tmp
        # self.file_path = '/home/fabricio/scans/coarsescan'
        # self.file_list = ['2xfm_0046.h5', '2xfm_0047.h5', '2xfm_0048.h5', '2xfm_0049.h5', '2xfm_0044.h5', '2xfm_0045.h5', '2xfm_0043.h5']
        stage_pv = self.text_stage_pv.text()
        if self.file_path is None or stage_pv is '':
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
            self.select_element_button.setDisabled(False)
            num_files = len(self.scan_boundary.get_hdf_file_list())
            self.text_num_files.setText('{} Files Selected'.format(num_files))

        if num_files <= 2:
            err_msg = QMessageBox()
            err_msg.setIcon(QMessageBox.Critical)
            err_msg.setText('Missing Information')
            err_msg.setInformativeText('less than 3 files selected')
            err_msg.setDetailedText('Please make sure more than 2 files have been selected in the browser window')
            err_msg.setStandardButtons(QMessageBox.Ok)

            ret_val = err_msg.exec_()       
        else:   
            return
        return

    def on_select_element_button_click(self):

        self.scan_boundary.create_element_list()
        elem_list = self.scan_boundary.get_element_list()
        elem_dialog = QMessageBoxWithCheckBox(elem_list)
        ret_val, elem_dict = elem_dialog.exec_()

        for key, value in elem_dict.items():
            if value.isChecked():
                self.text_element.setText(key)
                self.build_scan_button.setDisabled(False)

        #tmp
        # self.text_element.setText('TFY')
        self.build_scan_button.setDisabled(False)
        return

    def on_build_scan_button_click(self):
        coefficient = int(self.text_coefficient.text())
        element = self.text_element.text()
        dtheta = float(self.text_theta.text())
        angle_offset = float(self.text_angle_offset.text())
        try:
            left_offset, right_offset = self.text_boundary_offset_x.text().split(',')
            top_offset, bottom_offset = self.text_boundary_offset_y.text().split(',')

            left_offset = float(left_offset)
            right_offset = float(right_offset)
            top_offset = float(top_offset)
            bottom_offset = float(bottom_offset)

        except:
            print("invalid format: try 'x_offset (mm),y_offset (mm)")
            left_offset, right_offset = [0,0]
            top_offset, bottom_offset = [0,0]
            left_offset = float(left_offset)
            right_offset = float(right_offset)
            top_offset = float(top_offset)
            bottom_offset = float(bottom_offset)

        element_index = self.scan_boundary.get_element_index(element)
        self.scan_boundary.calc_xy_bounds(coefficient, element_index, self.bound_y.isChecked())
        self.scan_boundary.interpolate_bounds(dtheta)
        self.scan_boundary.offset_bounds(angle_offset, left_offset, right_offset, top_offset, bottom_offset)
        self.scan_boundary.offset_ROI_bounds(left_offset, right_offset, top_offset, bottom_offset)
        self.scan_params = self.scan_boundary.get_boundaries()

        self.show_plots_button.setDisabled(False)
        self.build_scan_button.setDisabled(False)
        #  self.enable_build_scan_button()

        self.scan_params2 = []
        self.x_pixel_size = self.text_x_size.text()
        self.y_pixel_size = self.text_y_size.text()
        self.dwell_time = self.text_dwell.text()
        coordinate_list = []

        self.parent.file_tab.scan_table.setRowCount(len(self.scan_params))
        for i in range(len(self.scan_params)): # i is the row number
            self.parent.file_tab.scan_table.setItem(i,0,QTableWidgetItem(str(self.scan_params[i][1]))) #  x center
            self.parent.file_tab.scan_table.setItem(i,1,QTableWidgetItem(str(self.scan_params[i][3]))) #  y center
            self.parent.file_tab.scan_table.setItem(i,2,QTableWidgetItem(str(0))) #  z center
            self.parent.file_tab.scan_table.setItem(i,3,QTableWidgetItem(str(self.scan_params[i][0]))) #  theta
            self.parent.file_tab.scan_table.setItem(i,4,QTableWidgetItem(str(self.scan_params[i][2]))) #  x width
            self.parent.file_tab.scan_table.setItem(i,5,QTableWidgetItem(str(self.x_pixel_size))) #  x step_size
            self.parent.file_tab.scan_table.setItem(i,6,QTableWidgetItem(str(self.scan_params[i][4]))) #  y width
            self.parent.file_tab.scan_table.setItem(i,7,QTableWidgetItem(str(self.y_pixel_size))) #  y step_sze
            self.parent.file_tab.scan_table.setItem(i,8,QTableWidgetItem(str(self.dwell_time))) #  dwell time

            coordinate_list.append((self.scan_params[i][1], self.scan_params[i][3], 0, self.scan_params[i][0],
                                    self.scan_params[i][1], self.scan_params[i][3]))

        self.parent.file_tab.set_coordinate_list(coordinate_list)

        eta = self.get_ETA()
        self.text_ETA.setText(eta)

    def bounds_changed(self, new_bounds):
        self.scan_params = new_bounds

        self.scan_params2 = []
        self.x_pixel_size = self.text_x_size.text()
        self.y_pixel_size = self.text_y_size.text()
        self.dwell_time = self.text_dwell.text()
        coordinate_list = []

        self.parent.file_tab.scan_table.setRowCount(len(self.scan_params))
        for i in range(len(self.scan_params)): # i is the row number
            self.parent.file_tab.scan_table.setItem(i,0,QTableWidgetItem(str(self.scan_params[i][1]))) #  x center
            self.parent.file_tab.scan_table.setItem(i,1,QTableWidgetItem(str(self.scan_params[i][3]))) #  y center
            self.parent.file_tab.scan_table.setItem(i,2,QTableWidgetItem(str(0))) #  z center
            self.parent.file_tab.scan_table.setItem(i,3,QTableWidgetItem(str(self.scan_params[i][0]))) #  theta
            self.parent.file_tab.scan_table.setItem(i,4,QTableWidgetItem(str(self.scan_params[i][2]))) #  x width
            self.parent.file_tab.scan_table.setItem(i,5,QTableWidgetItem(str(self.x_pixel_size))) #  x step_size
            self.parent.file_tab.scan_table.setItem(i,6,QTableWidgetItem(str(self.scan_params[i][4]))) #  y width
            self.parent.file_tab.scan_table.setItem(i,7,QTableWidgetItem(str(self.y_pixel_size))) #  y step_sze
            self.parent.file_tab.scan_table.setItem(i,8,QTableWidgetItem(str(self.dwell_time))) #  dwell time

            coordinate_list.append((self.scan_params[i][1], self.scan_params[i][3], 0, self.scan_params[i][0],
                                    self.scan_params[i][1], self.scan_params[i][3]))

        self.parent.file_tab.set_coordinate_list(coordinate_list)
        eta = self.get_ETA()
        self.text_ETA.setText(eta)

    def get_ETA(self):

        eta_seconds = 0
        for i in range(len(self.scan_params)):
           eta_seconds += (self.scan_params[i][2]/float(self.x_pixel_size)) * (self.scan_params[i][4]/float(self.y_pixel_size)) *float(self.dwell_time)/1000*1.1

        eta_hours = floor(eta_seconds/3600)
        eta_minutes = floor(eta_seconds%3600/60)
        eta_seconds = floor(eta_seconds%60%60)

        return "{}: {}: {}".format(eta_hours, eta_minutes, eta_seconds)

    def on_show_plots_button_click(self):

        w = self.scan_boundary.show_roi_box2()
        self.parent.w = w
        self.parent.w.show()
        # self.scan_boundary.show_roi_box()
        return w
