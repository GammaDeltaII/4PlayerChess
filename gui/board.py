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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QFont, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt, QRectF

# Square and piece size
SIZE = 50

# Colors
DARK = Qt.gray
LIGHT = Qt.lightGray
RED = QColor('#bf3b43')
YELLOW = QColor('#c09526')
BLUE = QColor('#4185bf')
GREEN = QColor('#4e9161')


class Board(QWidget):
    def __init__(self):
        super().__init__()
        self.size = 14
        self.squares = []

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_board(qp)
        self.draw_pieces(qp)
        qp.end()

    def draw_board(self, qp):
        # Draw squares
        for i in range(14):
            for j in range(14):
                if (i + j) % 2:
                    color = DARK
                else:
                    color = LIGHT
                qp.fillRect(i * SIZE, j * SIZE, SIZE, SIZE, color)
        # Remove corners of the board
        qp.eraseRect(0, 0, 3 * SIZE, 3 * SIZE)
        qp.eraseRect(11 * SIZE, 0, 3 * SIZE, 3 * SIZE)
        qp.eraseRect(0, 11 * SIZE, 3 * SIZE, 3 * SIZE)
        qp.eraseRect(11 * SIZE, 11 * SIZE, 3 * SIZE, 3 * SIZE)
        # Draw color squares in the corners
        qp.fillRect(12 * SIZE, 12 * SIZE, SIZE, SIZE, RED)
        qp.fillRect(1 * SIZE, 12 * SIZE, SIZE, SIZE, BLUE)
        qp.fillRect(1 * SIZE, 1 * SIZE, SIZE, SIZE, YELLOW)
        qp.fillRect(12 * SIZE, 1 * SIZE, SIZE, SIZE, GREEN)

    def draw_pieces(self, qp):
        # Red pieces
        for i in range(8):
            _ = QSvgRenderer('resources/img/rP.svg').render(qp, QRectF((3 + i) * SIZE, 12 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/rK.svg').render(qp, QRectF(7 * SIZE, 13 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/rQ.svg').render(qp, QRectF(6 * SIZE, 13 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/rB.svg').render(qp, QRectF(5 * SIZE, 13 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/rB.svg').render(qp, QRectF(8 * SIZE, 13 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/rN.svg').render(qp, QRectF(4 * SIZE, 13 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/rN.svg').render(qp, QRectF(9 * SIZE, 13 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/rR.svg').render(qp, QRectF(3 * SIZE, 13 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/rR.svg').render(qp, QRectF(10 * SIZE, 13 * SIZE, SIZE, SIZE))
        # Yellow pieces
        for i in range(8):
            _ = QSvgRenderer('resources/img/yP.svg').render(qp, QRectF((3 + i) * SIZE, 1 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/yK.svg').render(qp, QRectF(6 * SIZE, 0 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/yQ.svg').render(qp, QRectF(7 * SIZE, 0 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/yB.svg').render(qp, QRectF(5 * SIZE, 0 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/yB.svg').render(qp, QRectF(8 * SIZE, 0 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/yN.svg').render(qp, QRectF(4 * SIZE, 0 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/yN.svg').render(qp, QRectF(9 * SIZE, 0 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/yR.svg').render(qp, QRectF(3 * SIZE, 0 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/yR.svg').render(qp, QRectF(10 * SIZE, 0 * SIZE, SIZE, SIZE))
        # Blue pieces
        for i in range(8):
            _ = QSvgRenderer('resources/img/bP.svg').render(qp, QRectF(1 * SIZE, (3 + i) * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/bK.svg').render(qp, QRectF(0 * SIZE, 6 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/bQ.svg').render(qp, QRectF(0 * SIZE, 7 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/bB.svg').render(qp, QRectF(0 * SIZE, 5 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/bB.svg').render(qp, QRectF(0 * SIZE, 8 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/bN.svg').render(qp, QRectF(0 * SIZE, 4 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/bN.svg').render(qp, QRectF(0 * SIZE, 9 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/bR.svg').render(qp, QRectF(0 * SIZE, 3 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/bR.svg').render(qp, QRectF(0 * SIZE, 10 * SIZE, SIZE, SIZE))
        # Green pieces
        for i in range(8):
            _ = QSvgRenderer('resources/img/gP.svg').render(qp, QRectF(12 * SIZE, (3 + i) * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/gK.svg').render(qp, QRectF(13 * SIZE, 7 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/gQ.svg').render(qp, QRectF(13 * SIZE, 6 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/gB.svg').render(qp, QRectF(13 * SIZE, 5 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/gB.svg').render(qp, QRectF(13 * SIZE, 8 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/gN.svg').render(qp, QRectF(13 * SIZE, 4 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/gN.svg').render(qp, QRectF(13 * SIZE, 9 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/gR.svg').render(qp, QRectF(13 * SIZE, 3 * SIZE, SIZE, SIZE))
        _ = QSvgRenderer('resources/img/gR.svg').render(qp, QRectF(13 * SIZE, 10 * SIZE, SIZE, SIZE))
