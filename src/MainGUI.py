import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Transform import XZT_Transform


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Coordinate Transform Tool'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 363
        self.layout = None
        self.table_index = 0  # This is the table row.

        self.coordinateList = []

        # Define widgets to be used
        self.tableWidget = None

        self.labelX = None
        self.labelY = None
        self.labelZ = None
        self.labelT = None

        self.textX = None
        self.textY = None
        self.textZ = None
        self.textT = None

        self.addCoordinateButton = None

        self.init_ui()

        self.xzt_transform = XZT_Transform()

        return

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create all of the gui widgets.
        self.create_text_entry()
        self.create_table()

        # Place the widgets on the window.
        self.create_layout()

        self.useTextValuesRadioButton.setChecked(True)

        # Show widget
        self.show()

        return

    def create_text_entry(self):

        # Create text labels and text boxes
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
        self.addCoordinateButton = QPushButton("Add To Table")
        self.addCoordinateButton.setStyleSheet('background-color: yellow')
        self.addCoordinateButton.clicked.connect(self.on_add_button_click)
	
        self.clearTableButton = QPushButton("Clear Table")
        self.clearTableButton.setStyleSheet('background-color: yellow')
        self.clearTableButton.clicked.connect(self.on_clear_table_button_click)

        self.useTextValuesRadioButton = QRadioButton("Use entered values.", self)
        self.usePVValuesRadioButton = QRadioButton("Use current PV values.", self)

        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.useTextValuesRadioButton, 1)
        self.buttonGroup.addButton(self.usePVValuesRadioButton, 2)
	
        return

    def create_table(self):
        # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("0 Deg. Coordinates"))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("Rotated Coordinates"))
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 200)

        return

    def create_layout(self):

        vbox = QVBoxLayout()
        vbox.addWidget(self.labelX)
        vbox.addWidget(self.textX)
        vbox.addWidget(self.labelY)
        vbox.addWidget(self.textY)
        vbox.addWidget(self.labelZ)
        vbox.addWidget(self.textZ)
        vbox.addWidget(self.labelT)
        vbox.addWidget(self.textT)
        vbox.addWidget(self.addCoordinateButton)
        vbox.addWidget(self.clearTableButton)
        vbox.addWidget(self.useTextValuesRadioButton)
        vbox.addWidget(self.usePVValuesRadioButton)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self.tableWidget)
        self.setLayout(hbox)

        self.textX.setText("0")
        self.textY.setText("0")
        self.textZ.setText("0")
        self.textT.setText("15")

        return

    @pyqtSlot()
    def on_add_button_click(self):

        x_coord = float(self.textX.text())
        y_coord = float(self.textY.text())
        z_coord = float(self.textZ.text())
        t_coord = float(self.textT.text())

        if self.usePVValuesRadioButton.isChecked():
            self.xzt_transform.transform_axes(t_coord, 0, 0, z_coord, x_coord, y_coord, True, True)

        if self.useTextValuesRadioButton.isChecked():
            self.xzt_transform.transform_drives(0, 0, 0, z_coord, x_coord, y_coord, True, False)
            x_axis, y_axis, z_axis, t_axis, fx_axis, fy_axis = self.xzt_transform.get_axis_positions()
            self.xzt_transform.transform_axes(t_coord, x_axis, y_axis, z_axis, fx_axis, fy_axis, True, False)

        x, y, z, t, fx, fy = self.xzt_transform.get_drive_positions()
	
        num_items = self.tableWidget.rowCount()

        if self.table_index >= num_items:
            self.tableWidget.insertRow(self.table_index)

        self.tableWidget.setItem(self.table_index, 0, QTableWidgetItem("%.3f, %.3f, %.3f" % (x_coord, y_coord, z_coord)))
        self.tableWidget.setItem(self.table_index, 1, QTableWidgetItem("%.3f, %.3f, %.3f" % (fx, fy, z)))
        self.table_index = self.table_index + 1

        return
	
    @pyqtSlot()
    def on_clear_table_button_click(self):
    		    
        self.tableWidget.clearContents()
        self.table_index = 0
        self.tableWidget.setRowCount(10)
        for i in range(self.tableWidget.rowCount()):
            if i > 9:
                self.tableWidget.removeRow(i)
	
        return
	

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
