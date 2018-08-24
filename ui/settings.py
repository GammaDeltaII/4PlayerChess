# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName("Preferences")
        Preferences.resize(400, 300)
        Preferences.setStyleSheet("background-color: rgb(50, 50, 50);\n"
"color: white;")
        self.buttonBox = QtWidgets.QDialogButtonBox(Preferences)
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
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.RestoreDefaults|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtWidgets.QGroupBox(Preferences)
        self.groupBox.setGeometry(QtCore.QRect(10, 20, 371, 131))
        self.groupBox.setObjectName("groupBox")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 30, 378, 103))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.showcoordinates = QtWidgets.QCheckBox(self.layoutWidget)
        self.showcoordinates.setObjectName("showcoordinates")
        self.verticalLayout.addWidget(self.showcoordinates)
        self.shownames = QtWidgets.QCheckBox(self.layoutWidget)
        self.shownames.setObjectName("shownames")
        self.verticalLayout.addWidget(self.shownames)
        self.autocolor = QtWidgets.QCheckBox(self.layoutWidget)
        self.autocolor.setObjectName("autocolor")
        self.verticalLayout.addWidget(self.autocolor)
        self.autorotate = QtWidgets.QCheckBox(self.layoutWidget)
        self.autorotate.setObjectName("autorotate")
        self.verticalLayout.addWidget(self.autorotate)

        self.retranslateUi(Preferences)
        self.buttonBox.accepted.connect(Preferences.accept)
        self.buttonBox.rejected.connect(Preferences.reject)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        _translate = QtCore.QCoreApplication.translate
        Preferences.setWindowTitle(_translate("Preferences", "Preferences"))
        self.groupBox.setTitle(_translate("Preferences", "Board"))
        self.showcoordinates.setText(_translate("Preferences", "Show coordinates"))
        self.shownames.setText(_translate("Preferences", "Show player names"))
        self.autocolor.setText(_translate("Preferences", "Auto-change arrow color"))
        self.autorotate.setText(_translate("Preferences", "Auto-rotate"))

