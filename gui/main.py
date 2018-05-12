#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of the Four-Player Chess project, a four-player chess GUI.
#
# Copyright (C) 2018, GammaDeltaII
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction
from PyQt5.QtCore import Qt
from gui.board import Board


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.width = 1000
        self.height = 800
        self.backgroundColor = Qt.darkGray
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Four-Player Team Chess Analysis Board')
        self.resize(self.width, self.height)
        self.center()
        p = self.palette()
        p.setColor(self.backgroundRole(), self.backgroundColor)
        self.setPalette(p)

        quitAct = QAction('Quit', self)
        quitAct.setStatusTip('Quit application')
        quitAct.triggered.connect(self.close)
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        mainMenu = menubar.addMenu('&File')
        mainMenu.addAction(quitAct)
        toolbar = self.addToolBar('Quit')
        toolbar.addAction(quitAct)
        board = Board()
        self.setCentralWidget(board)
        self.statusBar()

    def center(self):
        frame = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(cp)
        self.move(frame.topLeft())
