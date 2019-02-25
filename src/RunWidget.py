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

try:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except ImportError:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    import time
    from pylab import *

class RunWidget(QWidget):
    def __init__(self, parent):
        super(RunWidget, self).__init__()

        self.parent = parent
        self.title = 'Run Python Script Tool'
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.on_start_button_click)
        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(self.on_stop_button_click)
        self.outputTextbox = QPlainTextEdit(self)
        self.outputTextbox.resize(300, 400)
        self.scriptFullPath = QTextEdit(self)
        self.scriptFullPath.setMaximumHeight(25)
        self.browseButton = QPushButton('Browse')
        self.browseButton.clicked.connect(self.on_browse_button_click)
        self.scriptProcess = QProcess(self)
        self.scriptProcess.readyRead.connect(self.on_process_ready_read)
        self.scriptProcess.started.connect(self.on_process_started)
        self.scriptProcess.finished.connect(self.on_process_finished)

        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()

        hbox1.addWidget(self.scriptFullPath)
        hbox1.addWidget(self.browseButton)

        hbox2.addWidget(self.startButton)
        hbox2.addWidget(self.stopButton)

        vbox.addWidget(self.outputTextbox)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

    def set_buttons_state(self, run_state):
        if run_state == 1:
            self.startButton.setEnabled(False)
            self.scriptFullPath.setEnabled(False)
            self.browseButton.setEnabled(False)
            self.stopButton.setEnabled(True)
        else:
            self.startButton.setEnabled(True)
            self.scriptFullPath.setEnabled(True)
            self.browseButton.setEnabled(True)
            self.stopButton.setEnabled(True)

    def update_batch_scan_list(self, scripts):
        plaintext = ""
        for script in scripts:
            plaintext = plaintext + script + "\n"
        plaintext = plaintext[:-1]
        return plaintext

    def get_scan_queue(self):

        return len(self.scripts)

    @pyqtSlot()
    def on_browse_button_click(self):
        file_names = QFileDialog.getOpenFileNames(self, "Select Python Script", "", "Python Files (*.py)")
        tmp_file_list = ""
        self.scriptFullPath.setMaximumHeight(20*len(file_names[0]))
        for file_name in file_names[0]:
            tmp_file_list += file_name + "\n"
        if tmp_file_list is not "":
            tmp_file_list = tmp_file_list[:-1]
            self.scriptFullPath.setText(tmp_file_list)

    @pyqtSlot()
    def on_start_button_click(self):
        self.scripts = self.scriptFullPath.toPlainText().split("\n")
        script = self.scripts[0]
        print('Starting script(s): ' + script)
        self.scriptProcess.start('python', [script])

    @pyqtSlot()
    def on_stop_button_click(self):
        print('Stopping script(s)')
        self.set_buttons_state(0)
        if self.scriptProcess.isOpen():
            self.scriptProcess.kill()

    @pyqtSlot()
    def on_process_ready_read(self):
        self.outputTextbox.insertPlainText(str(self.scriptProcess.readAll(), encoding='utf-8'))
        self.outputTextbox.verticalScrollBar().setValue(self.outputTextbox.verticalScrollBar().maximum())

    @pyqtSlot()
    def on_process_started(self):
        self.scripts = self.scripts[1:]
        plaintext = self.update_batch_scan_list(self.scripts)
        self.scriptFullPath.setText(plaintext)
        print('Python Script Started')
        self.set_buttons_state(1)

    @pyqtSlot(int)
    def on_process_finished(self, finVal):
        print('Python Script Finished with return value: ' + str(finVal))
        self.set_buttons_state(0)

        num_scripts = self.get_scan_queue()
        if num_scripts >= 1:
            self.on_start_button_click()
