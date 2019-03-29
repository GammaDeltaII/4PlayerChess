# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'promotedialog.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(70, 300)
        self.queenButton = QtWidgets.QPushButton(Dialog)
        self.queenButton.setGeometry(QtCore.QRect(0, 0, 70, 70))
        self.queenButton.setText("")
        self.queenButton.setIconSize(QtCore.QSize(70, 70))
        self.queenButton.setObjectName("queenButton")
        self.knightButton = QtWidgets.QPushButton(Dialog)
        self.knightButton.setGeometry(QtCore.QRect(0, 70, 70, 70))
        self.knightButton.setText("")
        self.knightButton.setObjectName("knightButton")
        self.rookButton = QtWidgets.QPushButton(Dialog)
        self.rookButton.setGeometry(QtCore.QRect(0, 140, 70, 70))
        self.rookButton.setText("")
        self.rookButton.setObjectName("rookButton")
        self.bishopButton = QtWidgets.QPushButton(Dialog)
        self.bishopButton.setGeometry(QtCore.QRect(0, 210, 70, 70))
        self.bishopButton.setText("")
        self.bishopButton.setObjectName("bishopButton")
        self.exitButton = QtWidgets.QPushButton(Dialog)
        self.exitButton.setGeometry(QtCore.QRect(0, 280, 70, 20))
        self.exitButton.setObjectName("exitButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.exitButton.setText(_translate("Dialog", "X"))


