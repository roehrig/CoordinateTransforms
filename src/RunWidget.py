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
except:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *

class RunWisget(QWidget):
    def __init__(self):
        super(RunWisget, self).__init__()
        self.title = 'Run Python Script Tool'
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.onStartPush)
        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(self.onStopPush)
        self.outputTextbox = QPlainTextEdit(self)
        self.outputTextbox.resize(300, 400)
        self.scriptFullPath = QLineEdit(self)
        self.browseButton = QPushButton('Browse')
        self.browseButton.clicked.connect(self.onBrowsePush)
        self.scriptProcess = QProcess(self)
        self.scriptProcess.readyRead.connect(self.onProcessReadyRead)
        self.scriptProcess.started.connect(self.onProcessStarted)
        self.scriptProcess.finished.connect(self.onProcessFinished)

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

    def setButtonsState(self, runState):
        if runState == 1:
            self.startButton.setEnabled(False)
            self.scriptFullPath.setEnabled(False)
            self.browseButton.setEnabled(False)
            self.stopButton.setEnabled(True)
        else:
            self.startButton.setEnabled(True)
            self.scriptFullPath.setEnabled(True)
            self.browseButton.setEnabled(True)
            self.stopButton.setEnabled(True)

    @pyqtSlot()
    def onBrowsePush(self):
        fileName = QFileDialog.getOpenFileName(self, "Select Python Script", "", "Python Files (*.py)")
        if fileName is not None:
            if len(fileName) > 0:
                self.scriptFullPath.setText(fileName[0])

    @pyqtSlot()
    def onStartPush(self):
        print('Starting script: ' + self.scriptFullPath.text())
        if self.scriptProcess.isOpen():
            print ('Close process first')
            self.scriptProcess.kill()
        self.scriptProcess.start('python', [self.scriptFullPath.text()])

    @pyqtSlot()
    def onStopPush(self):
        print('Stopping script: ' + self.scriptFullPath.text())
        self.setButtonsState(0)
        if self.scriptProcess.isOpen():
            self.scriptProcess.kill()

    @pyqtSlot()
    def onProcessReadyRead(self):
        self.outputTextbox.insertPlainText(str(self.scriptProcess.readAll(), encoding='utf-8'))
        self.outputTextbox.verticalScrollBar().setValue(self.outputTextbox.verticalScrollBar().maximum())

    @pyqtSlot()
    def onProcessStarted(self):
        print('Python Script Started')
        self.setButtonsState(1)

    @pyqtSlot(int)
    def onProcessFinished(self, finVal):
        print('Python Script Finished with return value: ' + str(finVal))
        self.setButtonsState(0)
