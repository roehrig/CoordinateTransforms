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

from CS import CoordinateSystem as CS
from Transform import XZT_Transform

try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except ImportError:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *


class CoordinatesWidget(QWidget):
    def __init__(self, parent):
        super(CoordinatesWidget, self).__init__()

        self.parent = parent

        self.table_index = 0  # This is the table row.
        self.coordinate_list = []
        self.xzt_transform = XZT_Transform()

        # Create text labels and text boxes for Coordinates
        self.labelX = QLabel('X Coordinate (um)')
        self.textX = QLineEdit()
        self.textX.setMaximumSize(150, 20)
        self.textX.setToolTip('Enter the X coordinate')
        self.labelY = QLabel('Y Coordinate (um)')
        self.textY = QLineEdit()
        self.textY.setMaximumSize(150, 20)
        self.textY.setToolTip('Enter the Y coordinate')
        self.labelZ = QLabel('Z Coordinate (um)')
        self.textZ = QLineEdit()
        self.textZ.setMaximumSize(150, 20)
        self.textZ.setToolTip('Enter the Z coordinate')
        self.labelT = QLabel('Theta Coordinate (deg.)')
        self.textT = QLineEdit()
        self.textT.setMaximumSize(150, 20)
        self.textT.setToolTip('Enter the Theta coordinate')

        # Create a pushbutton and assign the click signal to a slot.
        self.addCoordinateButton = QPushButton('Add To Table')
        self.addCoordinateButton.setStyleSheet('background-color: yellow')
        self.addCoordinateButton.clicked.connect(self.on_add_button_click)

        self.useTextValuesRadioButton = QRadioButton('Use entered values.', self)
        self.useTextValuesRadioButton.setToolTip('Use manually entered stage positions.')
#        self.useTextValuesAtZeroRadioButton = QRadioButton('Use entered values at 0 degrees.', self)
#        self.useTextValuesAtZeroRadioButton.setToolTip('Use manually entered stage positions at 0 degrees.')
        self.usePVValuesRadioButton = QRadioButton('Use current PV values.', self)
        self.usePVValuesRadioButton.setToolTip('Get stage positions from current PV values.')

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.useTextValuesRadioButton, 1)
#        self.buttonGroup.addButton(self.useTextValuesAtZeroRadioButton, 2)
        self.buttonGroup.addButton(self.usePVValuesRadioButton, 3)

        # Create table
        self.coordinate_table = QTableWidget()
        self.coordinate_table.setMaximumWidth(438)
        self.coordinate_table.setRowCount(10)
        self.coordinate_table.setColumnCount(2)
        self.coordinate_table.setHorizontalHeaderItem(0, QTableWidgetItem('0 Deg. Coordinates'))
        self.coordinate_table.setHorizontalHeaderItem(1, QTableWidgetItem('Rotated Coordinates'))
        self.coordinate_table.setColumnWidth(0, 200)
        self.coordinate_table.setColumnWidth(1, 200)

        # Create the layouts for the widgets.
        table_tab_vbox = QVBoxLayout()
        table_tab_vbox.addWidget(self.labelX)
        table_tab_vbox.addWidget(self.textX)
        table_tab_vbox.addWidget(self.labelY)
        table_tab_vbox.addWidget(self.textY)
        table_tab_vbox.addWidget(self.labelZ)
        table_tab_vbox.addWidget(self.textZ)
        table_tab_vbox.addWidget(self.labelT)
        table_tab_vbox.addWidget(self.textT)
        table_tab_vbox.addWidget(self.addCoordinateButton)
        table_tab_vbox.addWidget(self.useTextValuesRadioButton)
#        table_tab_vbox.addWidget(self.useTextValuesAtZeroRadioButton)
        table_tab_vbox.addWidget(self.usePVValuesRadioButton)
        table_tab_vbox.addStretch(1)

        table_tab_hbox = QHBoxLayout()
        table_tab_hbox.addLayout(table_tab_vbox)
        table_tab_hbox.addWidget(self.coordinate_table)

        self.setLayout(table_tab_hbox)

        # Set some default values
        self.textX.setText("0")
        self.textY.setText("0")
        self.textZ.setText("0")
        self.textT.setText("15")
        self.useTextValuesRadioButton.setChecked(True)

        return

    def clear_table(self):

        self.coordinate_table.clearContents()
        self.table_index = 0
        self.coordinate_table.setRowCount(10)
        for i in range(self.coordinate_table.rowCount()):
            if i > 9:
                self.coordinate_table.removeRow(i)

        self.coordinate_list = []

        return

    def remove_row(self, row_list):

        for index in range(len(row_list) - 1, -1, -1):
            row_num = row_list[index].row()
            self.coordinate_table.removeRow(row_num)
            del self.coordinate_list[row_num]
            self.table_index = self.table_index - 1

        return

    @pyqtSlot()
    def on_add_button_click(self):

        # Get the angle value entered in the text field.
        t_coord = float(self.textT.text())

        # The user can use the current axis positions instead of the text field values.
        if self.usePVValuesRadioButton.isChecked():
            # Create a coordinate system and get the current drive values
            coords = CS("9idbTAU")
            coarse_x, coarse_y, z_coord, theta, x_coord, y_coord = coords.get_drive_pv_positions()
            # Convert the axes values to drive values using the new angle entered.
            self.xzt_transform.transform_axes(t_coord, coarse_x, coarse_y, z_coord, x_coord, y_coord, True, True)
            coords = None

        # If the user wants to use the text field values, they must first be converted to axis
        # values, then reconverted back to drive values.
        if self.useTextValuesRadioButton.isChecked():
            # Get the coordinate values entered in the text fields.
            # These user positions are "drive" positions
            x_coord = float(self.textX.text())
            y_coord = float(self.textY.text())
            z_coord = float(self.textZ.text())

            # Convert the drive positions to axes positions at 0 degrees, then back to drive
            # positions using the new angle.
            self.xzt_transform.transform_drives(0, 0, 0, z_coord, x_coord, y_coord, True, False)
            x_axis, y_axis, z_axis, t_axis, fx_axis, fy_axis = self.xzt_transform.get_axis_positions()
            self.xzt_transform.transform_axes(t_coord, x_axis, y_axis, z_axis, fx_axis, fy_axis, True, False)

        # Get the coordinate values at the new rotation angle.
        x, y, z, t, fx, fy = self.xzt_transform.get_drive_positions()

        # Add the coordinates to the list.
        self.coordinate_list.append(self.xzt_transform.get_drive_positions())

        # If necessary, add a row to the table
        num_items = self.coordinate_table.rowCount()
        if self.table_index >= num_items:
            self.coordinate_table.insertRow(self.table_index)
            self.scan_table.insertRow(self.table_index)

        # Add the original coordinates and the transformed coordinates to the table
        self.coordinate_table.setItem(self.table_index, 0,
                                      QTableWidgetItem("%.3f, %.3f, %.3f" % (x_coord, y_coord, z_coord)))
        self.coordinate_table.setItem(self.table_index, 1, QTableWidgetItem("%.3f, %.3f, %.3f" % (fx, fy, z)))

        self.parent.update_table(self.table_index, self.coordinate_list[-1])
        # Increment the running count of coordinate sets.
        self.table_index = self.table_index + 1

        return

    def get_coordinate_list(self):

        return self.coordinate_list

    def get_selected_rows(self):

        row_list = self.coordinate_table.selectionModel().selectedRows()

        return row_list
