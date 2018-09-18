# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
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
        self.board = QtWidgets.QGroupBox(Preferences)
        self.board.setGeometry(QtCore.QRect(10, 10, 371, 161))
        self.board.setObjectName("board")
        self.layoutWidget = QtWidgets.QWidget(self.board)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 30, 378, 125))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.showcoordinates = QtWidgets.QCheckBox(self.layoutWidget)
        self.showcoordinates.setObjectName("showcoordinates")
        self.verticalLayout.addWidget(self.showcoordinates)
        self.showlegalmoves = QtWidgets.QCheckBox(self.layoutWidget)
        self.showlegalmoves.setObjectName("showlegalmoves")
        self.verticalLayout.addWidget(self.showlegalmoves)
        self.coordinatehelp = QtWidgets.QCheckBox(self.layoutWidget)
        self.coordinatehelp.setObjectName("coordinatehelp")
        self.verticalLayout.addWidget(self.coordinatehelp)
        self.shownames = QtWidgets.QCheckBox(self.layoutWidget)
        self.shownames.setObjectName("shownames")
        self.verticalLayout.addWidget(self.shownames)
        self.autocolor = QtWidgets.QCheckBox(self.layoutWidget)
        self.autocolor.setObjectName("autocolor")
        self.verticalLayout.addWidget(self.autocolor)
        self.autorotate = QtWidgets.QCheckBox(self.layoutWidget)
        self.autorotate.setObjectName("autorotate")
        self.verticalLayout.addWidget(self.autorotate)
        self.general = QtWidgets.QGroupBox(Preferences)
        self.general.setGeometry(QtCore.QRect(10, 180, 371, 51))
        self.general.setObjectName("general")
        self.layoutWidget_3 = QtWidgets.QWidget(self.general)
        self.layoutWidget_3.setGeometry(QtCore.QRect(20, 20, 341, 31))
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.chesscom = QtWidgets.QCheckBox(self.layoutWidget_3)
        self.chesscom.setObjectName("chesscom")
        self.verticalLayout_3.addWidget(self.chesscom)

        self.retranslateUi(Preferences)
        self.buttonBox.accepted.connect(Preferences.accept)
        self.buttonBox.rejected.connect(Preferences.reject)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        _translate = QtCore.QCoreApplication.translate
        Preferences.setWindowTitle(_translate("Preferences", "Preferences"))
        self.board.setTitle(_translate("Preferences", "Board"))
        self.showcoordinates.setText(_translate("Preferences", "Show coordinates"))
        self.showlegalmoves.setText(_translate("Preferences", "Show legal moves"))
        self.coordinatehelp.setText(_translate("Preferences", "Show mouseover coordinate"))
        self.shownames.setText(_translate("Preferences", "Show player names"))
        self.autocolor.setText(_translate("Preferences", "Auto-change arrow color"))
        self.autorotate.setText(_translate("Preferences", "Auto-rotate"))
        self.general.setTitle(_translate("Preferences", "General"))
        self.chesscom.setText(_translate("Preferences", "Use chess.com FEN4 and PGN4"))

