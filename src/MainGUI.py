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


class App(QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.title = 'Coordinate Transform Tool'
        self.left = 100
        self.top = 100
        self.width = 925
        self.height = 517
        self.layout = None
        self.table_index = 0  # This is the table row.

        # Create variables for each tab
        self.tabs = None
        self.table_tab = None
        self.file_tab = None
        self.run_tab = None

        # Create variables for two buttons
        self.clearTableButton = None
        self.removeRowButton = None

        self.init_ui()

        return

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.tabs = QTabWidget()

        self.table_tab = CoordinatesWidget(self)
        self.file_tab = ScriptWidget(self)
        self.run_tab = RunWidget(self)

        self.tabs.addTab(self.table_tab, "Table")
        self.tabs.addTab(self.file_tab, "File")
        self.tabs.addTab(self.run_tab, "Run")

        # Create all of the gui widgets.
        self.create_buttons()

        # Place the widgets on the window.
        self.create_layout()

        # Show widgets
        self.show()

        return

    def create_buttons(self):

        # Create two buttons and assign functions to the click event

        self.clearTableButton = QPushButton("Clear Table")
        self.clearTableButton.setStyleSheet('background-color: yellow')
        self.clearTableButton.setMaximumSize(200, 25)
        self.clearTableButton.clicked.connect(self.on_clear_table_button_click)

        self.removeRowButton = QPushButton('Remove Row')
        self.removeRowButton.setStyleSheet('background-color: yellow')
        self.removeRowButton.setMaximumSize(200, 25)
        self.removeRowButton.clicked.connect(self.on_remove_row_button_clicked)

        return

    def create_layout(self):

        # Add widgets to each tab
        self.tabs.addTab(self.table_tab, "Coordinates")
        self.tabs.addTab(self.file_tab, "Create Script")
        self.tabs.addTab(self.run_tab, "Run Script")

        # Create a vertical layout and add the tabs and buttons
        vbox = QVBoxLayout()
        vbox.addWidget(self.tabs)
        vbox.addWidget(self.clearTableButton)
        vbox.addWidget(self.removeRowButton)

        self.setLayout(vbox)

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

    def update_table(self, table_index, coordinates):

        self.file_tab.add_coordinates(table_index, coordinates)

        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
