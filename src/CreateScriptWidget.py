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

import stat

from ScriptWriter import FlyScanScriptWriter
from ScriptWriter import ScriptLogWriter

try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except ImportError:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *


class ScriptWidget(QWidget):
    def __init__(self, parent):
        super(ScriptWidget, self).__init__()

        self.parent = parent

        self.coordinate_list = []
        self.table_index = 0

        # Create text labels and text boxes for creating a python script
        self.label_template = QLabel('Name of script template')
        self.text_template = QLineEdit()
        self.text_template.setMinimumWidth(500)
        self.text_template.setMaximumSize(700, 20)
        self.label_file = QLabel('Name of scan script')
        self.text_file = QLineEdit()
        self.text_file.setMinimumWidth(300)
        self.text_file.setMaximumSize(500, 20)
        self.text_file.setToolTip('Enter the file name for the python script')
        self.label_path = QLabel('Path to scan script')
        self.text_path = QLineEdit()
        self.text_path.setMinimumWidth(500)
        self.text_path.setMaximumSize(700, 20)
        self.text_path.setToolTip('Enter the file path for the python script')
        self.label_log = QLabel('Name of log file')
        self.log_file = QLineEdit()
        self.log_file.setMinimumWidth(300)
        self.log_file.setMaximumSize(500, 20)
        self.log_file.setToolTip('Enter the file name for the log file')

        self.selectTemplateButton = QPushButton('Select Template File')
        self.selectTemplateButton.setStyleSheet('background-color: yellow')
        self.selectTemplateButton.setMaximumSize(200, 25)
        self.selectTemplateButton.clicked.connect(self.on_select_template_button_click)

        self.selectFilePathButton = QPushButton('Select Script Path')
        self.selectFilePathButton.setStyleSheet('background-color: yellow')
        self.selectFilePathButton.setMaximumSize(200, 25)
        self.selectFilePathButton.clicked.connect(self.on_select_path_button_click)

        self.createScriptButton = QPushButton('Create Script')
        self.createScriptButton.setStyleSheet('background-color: yellow')
        self.createScriptButton.setMaximumSize(200, 25)
        self.createScriptButton.clicked.connect(self.on_create_script_button_click)

        self.scan_table = QTableWidget()
        self.scan_table.setRowCount(10)
        self.scan_table.setColumnCount(7)
        self.scan_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.scan_table.setHorizontalHeaderItem(0, QTableWidgetItem('Coordinates'))
        self.scan_table.setHorizontalHeaderItem(1, QTableWidgetItem('X Width'))
        self.scan_table.setHorizontalHeaderItem(2, QTableWidgetItem('X Step Size'))
        self.scan_table.setHorizontalHeaderItem(3, QTableWidgetItem('Y Width'))
        self.scan_table.setHorizontalHeaderItem(4, QTableWidgetItem('Y Step Size'))
        self.scan_table.setHorizontalHeaderItem(5, QTableWidgetItem('Dwell'))
        self.scan_table.setHorizontalHeaderItem(6, QTableWidgetItem('Copy'))
        self.scan_table.setColumnWidth(0, 200)
        for i in range(1, 7):
            self.scan_table.setColumnWidth(i, 100)

        for i in range(9):
            check_box = QTableWidgetItem()
            check_box.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_box.setCheckState(Qt.Unchecked)
            self.scan_table.setItem(i, 6, check_box)

        self.scan_table.itemClicked.connect(self.on_copy_checkbox_clicked)

        file_tab_form_layout = QFormLayout()
        file_tab_form_layout.addRow(self.label_template, self.text_template)
        file_tab_form_layout.addRow(self.label_file, self.text_file)
        file_tab_form_layout.addRow(self.label_log, self.log_file)
        file_tab_form_layout.addRow(self.label_path, self.text_path)

        button_hbox = QHBoxLayout()
        button_hbox.addWidget(self.selectTemplateButton, alignment=Qt.AlignCenter)
        button_hbox.addWidget(self.selectFilePathButton, alignment=Qt.AlignCenter)
        button_hbox.addWidget(self.createScriptButton, alignment=Qt.AlignCenter)
        file_tab_vbox = QVBoxLayout()
        file_tab_vbox.addWidget(self.scan_table)
        file_tab_vbox.addLayout(file_tab_form_layout)
        file_tab_vbox.addLayout(button_hbox)
        self.setLayout(file_tab_vbox)

    # The default signal passes no arguments, so indicate that this should
    # use the overloaded version that passes an object of type QTableWidgetItem.
    @pyqtSlot(QTableWidgetItem)
    def on_copy_checkbox_clicked(self, item):

        if item.checkState() == Qt.Checked:
            row = item.row()
            if row > 0:
                num_columns = self.scan_table.columnCount()
                for column in range(1, num_columns - 1):
                    self.scan_table.setItem(row, column, QTableWidgetItem(self.scan_table.item(row - 1, column).text()))

        return

    def clear_table(self):

        self.scan_table.clearContents()
        self.scan_table.setRowCount(10)
        for i in range(self.scan_table.rowCount()):
            if i > 9:
                self.scan_table.removeRow(i)

        return

    def remove_row(self, row_list):

        for index in range(len(row_list) - 1, -1, -1):
            row_num = row_list[index].row()
            self.scan_table.removeRow(row_num)

        return

    @pyqtSlot()
    def on_select_template_button_click(self):

        file_dialog = QFileDialog(self, "Select Template File", "")
        file_dialog.setFileMode(QFileDialog.AnyFile)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()
            self.text_template.setText(file_path[0])

        return

    @pyqtSlot()
    def on_select_path_button_click(self):

        file_dialog = QFileDialog(self, "Select Directory", "")
        file_dialog.setFileMode(QFileDialog.Directory)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()
            self.text_path.setText(file_path[0])

        return

    @pyqtSlot()
    def on_create_script_button_click(self):

        x_width_list = []
        y_width_list = []
        x_step_list = []
        y_step_list = []
        dwell_list = []

        # Combine the filename and file path
        template_name = "{}".format(self.text_template.text())
        file_name = "{}{}{}".format(self.text_path.text(), '/', self.text_file.text())
        log_file_name = "{}{}{}".format(self.text_path.text(), '/', self.log_file.text())

        num_rows = self.scan_table.rowCount()
        for row in range(self.table_index + 1):
            try:
                x_width_list.append(self.scan_table.item(row, 1).text())
                y_width_list.append(self.scan_table.item(row, 3).text())
                x_step_list.append(self.scan_table.item(row, 2).text())
                y_step_list.append(self.scan_table.item(row, 4).text())
                dwell_list.append(self.scan_table.item(row, 5).text())
            except TypeError:
                return

        with FlyScanScriptWriter() as writer:
            writer.set_template_file(template_name)
            writer.write_script(file_name, self.coordinate_list, x_width_list, y_width_list,
                                x_step_list, y_step_list, dwell_list)
            mask = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | \
                   stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
            writer.set_file_permissions(file_name, mask)

        with ScriptLogWriter() as log:
            log.add_scans(log_file_name, self.coordinate_list, x_width_list, y_width_list,
                          x_step_list, y_step_list, dwell_list)

        return

    # The default signal passes no arguments, so indicate that this should
    # use the overloaded version that passes an object of type QTableWidgetItem.
    @pyqtSlot(QTableWidgetItem)
    def on_copy_checkbox_clicked(self, item):

        if item.checkState() == Qt.Checked:
            row = item.row()
            if row > 0:
                num_columns = self.scan_table.columnCount()
                for column in range(1, num_columns - 1):
                    self.scan_table.setItem(row, column, QTableWidgetItem(self.scan_table.item(row - 1, column).text()))

        return

    def get_selected_rows(self):

        row_list = self.scan_table.selectionModel().selectedRows()

        return row_list

    def add_coordinates(self, table_index, coordinates):

        self.table_index = table_index
        self.coordinate_list.append(coordinates)

        self.scan_table.setItem(self.table_index, 0, QTableWidgetItem("%.3f, %.3f, %.3f" %
                                                                      (coordinates[4], coordinates[5], coordinates[2])))

        return
