import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Transform import XZT_Transform
from ScriptWriter import FlyScanScriptWriter


class App(QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Coordinate Transform Tool'
        self.left = 100
        self.top = 100
        self.width = 692
        self.height = 417
        self.layout = None
        self.table_index = 0  # This is the table row.

        self.coordinate_list = []

        # Define widgets to be used
        self.tableWidget = None

        self.tabs = None
        self.table_tab = None
        self.file_tab = None

        self.labelX = None
        self.labelY = None
        self.labelZ = None
        self.labelT = None

        self.label_x_width = None
        self.label_y_width = None
        self.label_x_step = None
        self.label_y_step = None
        self.label_dwell = None
        self.label_file = None
        self.label_path = None

        self.textX = None
        self.textY = None
        self.textZ = None
        self.textT = None

        self.text_x_width = None
        self.text_y_width = None
        self.text_x_step = None
        self.text_y_step = None
        self.text_dwell = None
        self.text_file = None
        self.text_path = None

        self.addCoordinateButton = None
        self.clearTableButton = None
        self.selectFilePathButton = None
        self.createScriptButton = None

        self.useTextValuesRadioButton = None
        self.usePVValuesRadioButton = None

        self.buttonGroup = None

        self.init_ui()

        self.xzt_transform = XZT_Transform()

        return

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.tabs = QTabWidget()

        self.table_tab = QWidget()
        self.file_tab = QWidget()

        self.tabs.addTab(self.table_tab, "Table")
        self.tabs.addTab(self.file_tab, "File")

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

        # Create text labels and text boxes for creating a python script
        self.label_x_width = QLabel('X Scan Width (um)')
        self.text_x_width = QLineEdit()
        self.text_x_width.setMaximumSize(150,20)
        self.text_x_width.setToolTip('Enter the width of the scan along the X-axis')
        self.label_y_width = QLabel('Y Scan Width (um)')
        self.text_y_width = QLineEdit()
        self.text_y_width.setMaximumSize(150, 20)
        self.text_y_width.setToolTip('Enter the width of the scan along the Y-axis')
        self.label_x_step = QLabel('X Scan Pixel Size (um)')
        self.text_x_step = QLineEdit()
        self.text_x_step.setMaximumSize(150, 20)
        self.text_x_step.setToolTip('Enter the size of each pixel along the X-axis')
        self.label_y_step = QLabel('Y Scan Pixel Size (um)')
        self.text_y_step = QLineEdit()
        self.text_y_step.setMaximumSize(150, 20)
        self.text_y_step.setToolTip('Enter the size of each pixel along the Y-axis')
        self.label_dwell = QLabel('Pixel Dwell Time (ms)')
        self.text_dwell = QLineEdit()
        self.text_dwell.setMaximumSize(150, 20)
        self.text_dwell.setToolTip('Enter the time to collect data at each pixel')
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

        self.selectFilePathButton = QPushButton("Select Path")
        self.selectFilePathButton.setStyleSheet('background-color: yellow')
        self.selectFilePathButton.setMaximumSize(200, 25)
        self.selectFilePathButton.clicked.connect(self.on_select_path_button_click)

        self.createScriptButton = QPushButton("Create Script")
        self.createScriptButton.setStyleSheet('background-color: yellow')
        self.createScriptButton.setMaximumSize(200, 25)
        self.createScriptButton.clicked.connect(self.on_create_script_button_click)

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
        table_tab_vbox.addWidget(self.clearTableButton)
        table_tab_vbox.addWidget(self.useTextValuesRadioButton)
        table_tab_vbox.addWidget(self.usePVValuesRadioButton)
        table_tab_vbox.addStretch(1)

        table_tab_hbox = QHBoxLayout()
        table_tab_hbox.addLayout(table_tab_vbox)
        table_tab_hbox.addWidget(self.tableWidget)

        self.tabs.addTab(self.table_tab, "Coordinates")
        self.tabs.addTab(self.file_tab, "Create Script")
        self.table_tab.setLayout(table_tab_hbox)

        file_tab_form_layout = QFormLayout()
        file_tab_form_layout.addRow(self.label_x_width, self.text_x_width)
        file_tab_form_layout.addRow(self.label_y_width, self.text_y_width)
        file_tab_form_layout.addRow(self.label_x_step, self.text_x_step)
        file_tab_form_layout.addRow(self.label_y_step,self.text_y_step)
        file_tab_form_layout.addRow(self.label_dwell, self.text_dwell)
        file_tab_form_layout.addRow(self.label_file, self.text_file)
        file_tab_form_layout.addRow(self.label_path, self.text_path)

        file_tab_vbox = QVBoxLayout()
        file_tab_vbox.addLayout(file_tab_form_layout)
        file_tab_vbox.addWidget(self.selectFilePathButton, alignment=Qt.AlignCenter)
        file_tab_vbox.addWidget(self.createScriptButton, alignment=Qt.AlignCenter)
        self.file_tab.setLayout(file_tab_vbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.tabs)

        self.setLayout(hbox)

        self.textX.setText("0")
        self.textY.setText("0")
        self.textZ.setText("0")
        self.textT.setText("15")

        return

    @pyqtSlot()
    def on_add_button_click(self):

        # Get the coordinate values entered in the text fields.
        x_coord = float(self.textX.text())
        y_coord = float(self.textY.text())
        z_coord = float(self.textZ.text())
        t_coord = float(self.textT.text())

        # The user can use the current axis positions instead of the text field values.
        if self.usePVValuesRadioButton.isChecked():
            self.xzt_transform.transform_axes(t_coord, 0, 0, z_coord, x_coord, y_coord, True, True)

        # If the user wants to use the text field values, they must first be converted to axis
        # values, then reconverted back to drive values.
        if self.useTextValuesRadioButton.isChecked():
            self.xzt_transform.transform_drives(0, 0, 0, z_coord, x_coord, y_coord, True, False)
            x_axis, y_axis, z_axis, t_axis, fx_axis, fy_axis = self.xzt_transform.get_axis_positions()
            self.xzt_transform.transform_axes(t_coord, x_axis, y_axis, z_axis, fx_axis, fy_axis, True, False)

        # Get the coordinate values at the new rotation angle.
        x, y, z, t, fx, fy = self.xzt_transform.get_drive_positions()

        # Add the coordinates to the list.
        self.coordinate_list.append(self.xzt_transform.get_drive_positions())

        # If necessary, add a row to the table
        num_items = self.tableWidget.rowCount()
        if self.table_index >= num_items:
            self.tableWidget.insertRow(self.table_index)

        # Add the original coordinates and the transformed coordinates to the table
        self.tableWidget.setItem(self.table_index, 0, QTableWidgetItem("%.3f, %.3f, %.3f" % (x_coord, y_coord, z_coord)))
        self.tableWidget.setItem(self.table_index, 1, QTableWidgetItem("%.3f, %.3f, %.3f" % (fx, fy, z)))

        # Increment the running count of coordinate sets.
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

        self.coordinate_list = []

        return

    @pyqtSlot()
    def on_select_path_button_click(self):

        file_dialog = QFileDialog(self, "Open File", "/Users/roehrig")
        file_path = QStringList()

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()
            self.text_path.setText(file_path[0])

        return

    @pyqtSlot()
    def on_create_script_button_click(self):

        file_name = self.text_path.text() + '/' + self.text_file.text()
        x_width = self.text_x_width.text()
        y_width = self.text_y_width.text()
        x_step = self.text_x_step.text()
        y_step = self.text_y_step.text()
        dwell = self.text_dwell.text()

        with FlyScanScriptWriter() as writer:
            writer.write_script(file_name, self.coordinate_list, x_width, y_width, x_step, y_step, dwell)

        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
