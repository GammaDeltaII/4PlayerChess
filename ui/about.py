# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(400, 300)
        About.setStyleSheet("background-color: rgb(50, 50, 50);\n"
"color: white;")
        self.buttonBox = QtWidgets.QDialogButtonBox(About)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 40))
        self.buttonBox.setStyleSheet("QPushButton {\n"
"    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"stop: 0 rgb(150, 150, 150), stop: 0.4 rgb(135, 135, 135),\n"
"stop: 0.5 rgb(125, 125, 125), stop: 1.0 rgb(110, 110, 110));\n"
"    border: 1px solid rgb(100, 100, 100);\n"
"    border-radius: 4px;\n"
"        color: black;\n"
"        padding: 5px 10px;\n"
"}\n"
"QPushButton:hover {\n"
"        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(200, 200, 200), stop: 0.4 rgb(185, 185, 185), stop: 0.5 rgb(175, 175, 175), stop: 1.0 rgb(160, 160, 160));\n"
"}\n"
"QPushButton:pressed {\n"
"        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 rgb(220, 220, 220), stop: 0.4 rgb(205, 205, 205), stop: 0.5 rgb(195, 195, 195), stop: 1.0 rgb(180, 180, 180));\n"
"}")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(About)
        self.label.setGeometry(QtCore.QRect(50, 110, 300, 120))
        self.label.setText("")
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")

        self.retranslateUi(About)
        self.buttonBox.accepted.connect(About.accept)
        self.buttonBox.rejected.connect(About.reject)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "About 4PlayerChess"))

