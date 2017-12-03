import sys
import stat
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Transform import XZT_Transform
from CS import CoordinateSystem as CS
from ScriptWriter import FlyScanScriptWriter
from ScriptWriter import ScriptLogWriter


class App(QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Coordinate Transform Tool'
        self.left = 100
        self.top = 100
        self.width = 925
        self.height = 417
        self.layout = None
        self.table_index = 0  # This is the table row.

        self.coordinate_list = []

        # Define widgets to be used
        self.coordinate_table = None
        self.scan_table = None

        self.tabs = None
        self.table_tab = None
        self.file_tab = None

        self.labelX = None
        self.labelY = None
        self.labelZ = None
        self.labelT = None

        self.label_file = None
        self.label_log = None
        self.label_path = None

        self.textX = None
        self.textY = None
        self.textZ = None
        self.textT = None

        self.text_file = None
        self.log_file = None
        self.text_path = None

        self.addCoordinateButton = None
        self.clearTableButton = None
        self.selectTemplateButton = None
        self.selectFilePathButton = None
        self.createScriptButton = None
        self.removeRowButton = None

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
        self.log_file.setMaximumSize(500,20)
        self.log_file.setToolTip('Enter the file name for the log file')

        self.selectTemplateButton = QPushButton('Select Template File')
        self.selectTemplateButton.setStyleSheet('background-color: yellow')
        self.selectTemplateButton.setMaximumSize(200, 25)
        self.selectTemplateButton.clicked.connect(self.on_select_template_button_click)

        self.selectFilePathButton = QPushButton('Select Script Path')
        self.selectFilePathButton.setStyleSheet('background-color: yellow')
        self.selectFilePathButton.setMaximumSize(200, 25)
        self.selectFilePathButton.clicked.connect(self.on_select_path_button_click)

        self.removeRowButton = QPushButton('Remove Row')
        self.removeRowButton.setStyleSheet('background-color: yellow')
        self.removeRowButton.setMaximumSize(200, 25)
        self.removeRowButton.clicked.connect(self.on_remove_row_button_clicked)

        self.createScriptButton = QPushButton('Create Script')
        self.createScriptButton.setStyleSheet('background-color: yellow')
        self.createScriptButton.setMaximumSize(200, 25)
        self.createScriptButton.clicked.connect(self.on_create_script_button_click)

        return

    def create_table(self):
        # Create table
        self.coordinate_table = QTableWidget()
        self.coordinate_table.setMaximumWidth(438)
        self.coordinate_table.setRowCount(10)
        self.coordinate_table.setColumnCount(2)
        self.coordinate_table.setHorizontalHeaderItem(0, QTableWidgetItem('0 Deg. Coordinates'))
        self.coordinate_table.setHorizontalHeaderItem(1, QTableWidgetItem('Rotated Coordinates'))
        self.coordinate_table.setColumnWidth(0, 200)
        self.coordinate_table.setColumnWidth(1, 200)

        self.scan_table = QTableWidget()
        self.scan_table.setRowCount(10)
        self.scan_table.setColumnCount(7)
        self.scan_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.scan_table.setHorizontalHeaderItem(0, QTableWidgetItem('Coordinates'))
        self.scan_table.setHorizontalHeaderItem(1, QTableWidgetItem('X Width'))
        self.scan_table.setHorizontalHeaderItem(2, QTableWidgetItem('X Pixel'))
        self.scan_table.setHorizontalHeaderItem(3, QTableWidgetItem('Y Width'))
        self.scan_table.setHorizontalHeaderItem(4, QTableWidgetItem('Y Pixel'))
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
        table_tab_hbox.addWidget(self.coordinate_table)

        self.tabs.addTab(self.table_tab, "Coordinates")
        self.tabs.addTab(self.file_tab, "Create Script")
        self.table_tab.setLayout(table_tab_hbox)

        file_tab_form_layout = QFormLayout()
        file_tab_form_layout.addRow(self.label_template, self.text_template)
        file_tab_form_layout.addRow(self.label_file, self.text_file)
        file_tab_form_layout.addRow(self.label_log, self.log_file)
        file_tab_form_layout.addRow(self.label_path, self.text_path)

        button_hbox = QHBoxLayout()
        button_hbox.addWidget(self.selectTemplateButton, alignment=Qt.AlignCenter)
        button_hbox.addWidget(self.selectFilePathButton, alignment=Qt.AlignCenter)
        button_hbox.addWidget(self.removeRowButton, alignment=Qt.AlignCenter)
        button_hbox.addWidget(self.createScriptButton, alignment=Qt.AlignCenter)
        file_tab_vbox = QVBoxLayout()
        file_tab_vbox.addWidget(self.scan_table)
        file_tab_vbox.addLayout(file_tab_form_layout)
        file_tab_vbox.addLayout(button_hbox)
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
        self.coordinate_table.setItem(self.table_index, 0, QTableWidgetItem("%.3f, %.3f, %.3f" % (x_coord, y_coord, z_coord)))
        self.coordinate_table.setItem(self.table_index, 1, QTableWidgetItem("%.3f, %.3f, %.3f" % (fx, fy, z)))
        self.scan_table.setItem(self.table_index, 0, QTableWidgetItem("%.3f, %.3f, %.3f" % (fx, fy, z)))

        # Increment the running count of coordinate sets.
        self.table_index = self.table_index + 1

        return

    @pyqtSlot()
    def on_clear_table_button_click(self):

        self.coordinate_table.clearContents()
        self.scan_table.clearContents()
        self.table_index = 0
        self.coordinate_table.setRowCount(10)
        for i in range(self.coordinate_table.rowCount()):
            if i > 9:
                self.coordinate_table.removeRow(i)
                self.scan_table.removeRow(i)

        self.coordinate_list = []

        return

    @pyqtSlot()
    def on_select_template_button_click(self):

        file_dialog = QFileDialog(self, "Select Template File", "")
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_path = None

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()
            self.text_template.setText(file_path[0])

        return

    @pyqtSlot()
    def on_select_path_button_click(self):

        file_dialog = QFileDialog(self, "Select Directory", "")
        file_dialog.setFileMode(QFileDialog.Directory)
        file_path = None

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
        file_name = "{}{}{}".format(self.text_path.text(),'/',self.text_file.text())
        log_file_name = "{}{}{}".format(self.text_path.text(),'/',self.log_file.text())

        num_rows = self.scan_table.rowCount()
        for row in range(self.table_index):
            try:
                x_width_list.append(self.scan_table.item(row, 1).text())
                y_width_list.append(self.scan_table.item(row, 2).text())
                x_step_list.append(self.scan_table.item(row, 3).text())
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

    # The default signal passes no arguements, so indicate that this should
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

    @pyqtSlot(QTableWidgetItem)
    def on_remove_row_button_clicked(self, item):

        row_list = self.scan_table.selectionModel().selectedRows()
        for index in range(len(row_list) - 1, -1, -1):
            row_num = row_list[index].row()
            self.scan_table.removeRow(row_num)
            self.coordinate_table.removeRow(row_num)
            del self.coordinate_list[row_num]
            self.table_index = self.table_index - 1

        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
