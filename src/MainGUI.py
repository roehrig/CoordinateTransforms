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

import sys
import os
import datetime
try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except ImportError:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
from RunWidget import RunWidget
from CreateCoordinatesWidget import CoordinatesWidget
from CreateScriptWidget import ScriptWidget
from CoarseScanWidget import CoarseScanWidget


class App(QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Coordinate Transform Tool'
        self.left = 100
        self.top = 100
        self.width = 1125
        self.height = 517
        self.layout = None
        self.table_index = 0  # This is the table row.
        self.config_dir = None

        config_param_dict = self.load_config_file()
        self.config_dir = config_param_dict['config_dir']
        self.pv_prefix = config_param_dict['pv_prefix']

        # Create variables for each tab
        self.tabs = None
        self.table_tab = None
        self.file_tab = None
        self.run_tab = None
        self.coarse_scan_tab = None

        # Create variables for two buttons
        self.clearTableButton = None
        self.removeRowButton = None
        self.loadConfigButton = None
        self.saveConfigButton = None

        self.init_ui(config_param_dict)

        return

    def init_ui(self, config_dict):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.tabs = QTabWidget()

        self.table_tab = CoordinatesWidget(self, self.pv_prefix)
        self.file_tab = ScriptWidget(self)
        self.run_tab = RunWidget(self)
        self.coarse_scan_tab = CoarseScanWidget(self)

        # Create all of the gui widgets.
        self.create_buttons()

        # Place the widgets on the window.
        self.create_layout()

        # Put values from the loaded configuration file into the widgets.
        self.set_default_values(config_dict)

        # Show widgets
        self.show()

        return

    def create_buttons(self):

        # Create four buttons and assign functions to the click event

        self.clearTableButton = QPushButton("Clear Table")
        self.clearTableButton.setStyleSheet('background-color: yellow')
        self.clearTableButton.setMaximumSize(200, 25)
        self.clearTableButton.clicked.connect(self.on_clear_table_button_click)

        self.removeRowButton = QPushButton('Remove Row')
        self.removeRowButton.setStyleSheet('background-color: yellow')
        self.removeRowButton.setMaximumSize(200, 25)
        self.removeRowButton.clicked.connect(self.on_remove_row_button_clicked)

        self.loadConfigButton = QPushButton('Load Config')
        self.loadConfigButton.setStyleSheet('background-color: yellow')
        self.loadConfigButton.setMaximumSize(200, 25)
        self.loadConfigButton.clicked.connect(self.on_load_config_button_clicked)

        self.saveConfigButton = QPushButton('Save Config')
        self.saveConfigButton.setStyleSheet('background-color: yellow')
        self.saveConfigButton.setMaximumSize(200, 25)
        self.saveConfigButton.clicked.connect(self.on_save_config_button_clicked)

        return

    def create_layout(self):

        # Add widgets to each tab
        self.tabs.addTab(self.table_tab, 'Coordinates')
        self.tabs.addTab(self.coarse_scan_tab, 'Coarse Scans')
        self.tabs.addTab(self.file_tab, 'Create Script')
        self.tabs.addTab(self.run_tab, 'Run Script')

        # Create vertical layouts for the buttons
        button_vbox1 = QVBoxLayout()
        button_vbox1.addWidget(self.clearTableButton)
        button_vbox1.addWidget(self.removeRowButton)

        button_vbox2 = QVBoxLayout()
        button_vbox2.addWidget(self.loadConfigButton)
        button_vbox2.addWidget(self.saveConfigButton)

        # Create a horizontal layout for the buttons.
        hbox = QHBoxLayout()
        hbox.addLayout(button_vbox1)
        hbox.addLayout(button_vbox2)

        # Create a vertical layout and add the tabs and buttons
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        return

    def set_default_values(self, config_dict):

        self.table_tab.useTextValuesRadioButton.setChecked(config_dict['use_text_values'])
        self.table_tab.usePVValuesRadioButton.setChecked(config_dict['use_pv_values'])
        self.table_tab.textT.setText(config_dict['theta'])
        self.file_tab.useThetaCheckBox.setChecked(config_dict['use_theta'])
        self.file_tab.useZCheckBox.setChecked(config_dict['use_z'])
        self.file_tab.text_template.setText(config_dict['template'])
        self.file_tab.text_path.setText(config_dict['script_path'])
        self.file_tab.text_file.setText(config_dict['script_name'])
        self.file_tab.log_file.setText(config_dict['log_name'])
        self.coarse_scan_tab.text_stage_pv.setText(config_dict['stage_pv'])
        self.coarse_scan_tab.text_theta.setText(config_dict['theta'])
        self.coarse_scan_tab.text_element.setText(config_dict['element'])
        self.coarse_scan_tab.text_coefficient.setText(config_dict['coefficient'])

        return

    # Clear all entries from both tables
    @pyqtSlot()
    def on_clear_table_button_click(self):

        self.table_tab.clear_table()
        self.file_tab.clear_table()

        return

    @pyqtSlot()
    def on_remove_row_button_clicked(self):
        rows = self.table_tab.get_selected_rows()
        if not rows:
            rows = self.file_tab.get_selected_rows()
        self.table_tab.remove_row(rows)
        self.file_tab.remove_row(rows)

        return

    @pyqtSlot()
    def on_load_config_button_clicked(self):

        config_param_dict = self.load_config_file()

        self.config_dir = config_param_dict['config_dir']
        self.pv_prefix = config_param_dict['pv_prefix']

        self.set_default_values(config_param_dict)

        return

    @pyqtSlot()
    def on_save_config_button_clicked(self):

        file_name = QFileDialog.getSaveFileName(parent=self,caption='Save Config File',directory=self.config_dir)
        self.config_dir = os.path.dirname(file_name[0])
        try:
            with open(file_name[0], 'w') as config_file:
                # Put some comments in the file.
                config_file.write('Here is the structure of this file:\n')
                config_file.write('     The date and time the file was written.\n')
                config_file.write('     The directory that this file is in.\n')
                config_file.write('     The prefix of coordinate system PVs.\n')
                config_file.write('     Use stage positions entered manually? True/False\n')
                config_file.write('     Use stage positions from PV values? True/False\n')
                config_file.write('     The default theta position.\n')
                config_file.write('     Use the theta angle in the scan? True/False\n')
                config_file.write('     Use the Z value in the scan? True/False\n')
                config_file.write('     The path to the scan script template.\n')
                config_file.write('     The path to use for saving the scan script and log file.\n')
                config_file.write('     The name of the scan script file.\n')
                config_file.write('     The name of the log file.\n')
                config_file.write('     The PV for the sample rotation stage position.\n')
                config_file.write('     The change in angle between 2D scans.\n')
                config_file.write('     The element to use from coarse tomo scans.\n')
                config_file.write('     The scaling parameter for finding sample boundaries.\n')
                # Write the current date and time.
                config_file.write('{}\n'.format(datetime.datetime.now()))
                # Write the save directory
                config_file.write('{}\n'.format(self.config_dir))
                # Write the PV prefix
                config_file.write('{}\n'.format(self.pv_prefix))
                # Write the from the coordinate table tab.
                config_file.write('{}\n'.format(str(self.table_tab.useTextValuesRadioButton.isChecked())))
                config_file.write('{}\n'.format(str(self.table_tab.usePVValuesRadioButton.isChecked())))
                config_file.write('{}\n'.format(self.table_tab.textT.text()))
                # Write values from the create scan tab.
                config_file.write('{}\n'.format(str(self.file_tab.useThetaCheckBox.isChecked())))
                config_file.write('{}\n'.format(str(self.file_tab.useZCheckBox.isChecked())))
                config_file.write('{}\n'.format(self.file_tab.text_template.text()))
                config_file.write('{}\n'.format(self.file_tab.text_path.text()))
                config_file.write('{}\n'.format(self.file_tab.text_file.text()))
                config_file.write('{}\n'.format(self.file_tab.log_file.text()))
                # Write values from the coarse scan tab.
                config_file.write('{}\n'.format(self.coarse_scan_tab.text_stage_pv.text()))
                config_file.write('{}\n'.format(self.coarse_scan_tab.text_theta.text()))
                config_file.write('{}\n'.format(self.coarse_scan_tab.text_element.text()))
                config_file.write('{}\n'.format(self.coarse_scan_tab.text_coefficient.text()))

        except IOError as e:
            print(e)
            return
        except FileNotFoundError as e:
            print(e)
            return

        return

    def update_table(self, table_index, coordinates):

        self.file_tab.add_coordinates(table_index, coordinates)

        return

    def load_config_file(self):

        file_name = QFileDialog.getOpenFileName(parent=self,caption='Load Config File',directory=self.config_dir)

        config_dict = {}

        try:
            with open(file_name[0], 'r') as config_file:

                for i in range(18):
                    line = config_file.readline()

                line = config_file.readline()
                config_dict['config_dir'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['pv_prefix'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['use_text_values'] = self.string_to_bool(line.rstrip('\n'))

                line = config_file.readline()
                config_dict['use_pv_values'] = self.string_to_bool(line.rstrip('\n'))

                line = config_file.readline()
                config_dict['theta'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['use_theta'] = self.string_to_bool(line.rstrip('\n'))

                line = config_file.readline()
                config_dict['use_z'] = self.string_to_bool(line.rstrip('\n'))

                line = config_file.readline()
                config_dict['template'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['script_path'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['script_name'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['log_name'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['stage_pv'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['theta'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['element'] = line.rstrip('\n')

                line = config_file.readline()
                config_dict['coefficient'] = line.rstrip('\n')

        except IOError as e:
            print(e)
            return
        except FileNotFoundError as e:
            print(e)
            return

        return config_dict

    def string_to_bool(self,value):
        if value == 'True':
            return True
        elif value == 'False':
            return False
        else:
            raise ValueError

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
