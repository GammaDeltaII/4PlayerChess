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

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QRect
from gui.main import MainWindow


def main():
    """Creates application and main window and sets application icon."""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('resources/img/icon.svg'))
    window = MainWindow()
    screen = QRect(app.desktop().availableGeometry())
    x = screen.left() + (screen.width() - window.width()) / 2
    y = screen.top() + (screen.height() - window.height()) / 2
    window.move(x, y)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
