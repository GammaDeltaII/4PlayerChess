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

from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit
from PyQt5.QtCore import Qt, QSize, QRect, QRectF, QPoint, pyqtSignal, QEvent
from PyQt5.QtGui import QPainter, QPalette, QColor, QFont
from gui.board import Board


class View(QWidget):
    """The View is responsible for rendering the current state of the board and signalling user interaction to the
    underlying logic."""
    clicked = pyqtSignal(QPoint)
    squareSizeChanged = pyqtSignal(QSize)
    playerNameEdited = pyqtSignal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.squareSize = QSize(50, 50)
        self.board = Board(14, 14)
        self.pieces = {}
        # self.clickedPiece = None
        # self.clickedPieceIcon = None
        # self.mouseRect = None
        self.highlights = []
        self.playerHighlights = {'r': self.PlayerHighlight(12, 1, QColor('#bf3b43')),
                                 'b': self.PlayerHighlight(1, 1, QColor('#4185bf')),
                                 'y': self.PlayerHighlight(1, 12, QColor('#c09526')),
                                 'g': self.PlayerHighlight(12, 12, QColor('#4e9161'))}
        self.redName = None
        self.redNameEdit = None
        self.blueName = None
        self.blueNameEdit = None
        self.yellowName = None
        self.yellowNameEdit = None
        self.greenName = None
        self.greenNameEdit = None
        self.createPlayerLabels()

    class SquareHighlight:
        """A square highlight type."""
        Type = 1

        def __init__(self, file, rank, color):
            self.file = file
            self.rank = rank
            self.color = color

    class PlayerHighlight(SquareHighlight):
        """A player highlight type. Same as square highlight, just renamed for convenience (unaltered subclass)."""
        pass

    def setBoard(self, board):
        """Updates board, if changed. Disconnects signals from old board and connects them to new board."""
        if self.board == board:
            return
        if self.board:
            try:
                self.board.disconnect()
            # If there are no signal-slot connections, TypeError is raised
            except TypeError:
                pass
        self.board = board
        if board:
            board.dataChanged.connect(self.update)
            board.boardReset.connect(self.update)
            board.boardReset.connect(self.resetHighlights)
        self.updateGeometry()

    def setSquareSize(self, size):
        """Sets size of board squares and updates geometry accordingly."""
        if self.squareSize == size:
            return
        self.squareSize = size
        self.squareSizeChanged.emit(size)
        self.updateGeometry()

    def sizeHint(self):
        """Implements sizeHint() method. Computes and returns size based on size of board squares."""
        return QSize(self.squareSize.width()*self.board.files, self.squareSize.height()*self.board.ranks)

    def squareRect(self, file, rank):
        """Returns square of type QRect at position (file, rank)."""
        sqSize = self.squareSize
        return QRect(QPoint(file*sqSize.width(), (self.board.ranks-(rank+1))*sqSize.height()), sqSize)

    def paintEvent(self, event):
        """Implements paintEvent() method. Draws squares and pieces on the board."""
        painter = QPainter()
        painter.begin(self)
        # Draw squares
        for rank in range(self.board.ranks):
            for file in range(self.board.files):
                # Do not paint 3x3 sub-grids at the corners
                if not ((file < 3 and rank < 3) or (file < 3 and rank > 10) or
                        (file > 10 and rank < 3) or (file > 10 and rank > 10)):
                    self.drawSquare(painter, file, rank)
        # Draw highlights
        self.drawHighlights(painter)
        painter.fillRect(self.squareRect(12, 1), QColor('#40bf3b43'))
        painter.fillRect(self.squareRect(1, 1), QColor('#404185bf'))
        painter.fillRect(self.squareRect(1, 12), QColor('#40c09526'))
        painter.fillRect(self.squareRect(12, 12), QColor('#404e9161'))
        # Draw pieces
        for rank in range(self.board.ranks):
            for file in range(self.board.files):
                self.drawPiece(painter, file, rank)
        # if self.clickedPieceIcon and self.mouseRect:
        #     self.clickedPieceIcon.paint(painter, self.mouseRect, Qt.AlignCenter)
        # Draw coordinates
        for rank in range(self.board.ranks):
            file = 0 if 2 < rank < 11 else 3
            square = self.squareRect(file, rank)
            square.moveTopLeft(QPoint(square.x() + 1, square.y() + 1))
            square = QRectF(square)  # Only works with QRectF, so convert
            color = self.palette().color(QPalette.Midlight) if not (file + rank) % 2 \
                else self.palette().color(QPalette.Mid)
            font = QFont('Trebuchet MS', 10, QFont.Bold)
            painter.setPen(color)
            painter.setFont(font)
            painter.drawText(square, str(rank + 1))
        for file in range(self.board.files):
            rank = 0 if 2 < file < 11 else 3
            square = self.squareRect(file, rank)
            square.moveTopLeft(QPoint(square.x() - 1, square.y() - 1))
            square = QRectF(square)  # Only works with QRectF, so convert
            color = self.palette().color(QPalette.Midlight) if not (file + rank) % 2 \
                else self.palette().color(QPalette.Mid)
            font = QFont('Trebuchet MS', 10, QFont.Bold)
            painter.setPen(color)
            painter.setFont(font)
            painter.drawText(square, Qt.AlignBottom | Qt.AlignRight, chr(file + 97))
        painter.end()

    def drawSquare(self, painter, file, rank):
        """Draws dark or light square at position (file, rank) using painter."""
        rect = self.squareRect(file, rank)
        fillColor = self.palette().color(QPalette.Midlight) if (file + rank) % 2 else self.palette().color(QPalette.Mid)
        painter.fillRect(rect, fillColor)

    def setPiece(self, char, icon):
        """Sets piece icon corresponding to algebraic piece name."""
        self.pieces[char] = icon
        self.update()

    def piece(self, char):
        """Returns piece icon corresponding to algebraic piece name."""
        return self.pieces[char]

    def drawPiece(self, painter, file, rank):
        """Draws piece at square (file, rank) using painter."""
        rect = self.squareRect(file, rank)
        char = self.board.getData(file, rank)
        if char != ' ':
            icon = self.piece(char)
            # draggablePiece = QLabel(self)
            # iconPixmap = icon.pixmap(QSize(50, 50))
            # QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
            # draggablePiece.setPixmap(iconPixmap)
            # draggablePiece.move(rect.x(), rect.y())
            # draggablePiece.show()
            if not icon.isNull():
                icon.paint(painter, rect, Qt.AlignCenter)

    def squareAt(self, point):
        """Returns square (file, rank) of type QPoint that contains point."""
        sqSize = self.squareSize
        file = point.x() / sqSize.width()
        rank = point.y() / sqSize.height()
        if (file < 0) or (file > self.board.files) or (rank < 0) or (rank > self.board.ranks):
            return QPoint()
        return QPoint(file, self.board.ranks - rank)

    def mouseReleaseEvent(self, event):
        """Implements mouseReleaseEvent() method. Emits signal with clicked square of type QPoint as value."""
        point = self.squareAt(event.pos())
        if point.isNull():
            return
        self.clicked.emit(point)
        # self.clickedPiece = None
        # self.clickedPieceIcon = None
        # self.mouseRect = None

    # def mousePressEvent(self, event):
    #     point = self.squareAt(event.pos())
    #     if point.isNull():
    #         return
    #     self.clickedPiece = self.board.getData(point.x(), point.y())
    #
    # def mouseMoveEvent(self, event):
    #     position = event.pos()
    #     offset = QPoint(self.squareSize.width() / 2, self.squareSize.height() / 2)
    #     self.mouseRect = QRect(position - offset, self.squareSize)
    #     if self.clickedPiece and self.clickedPiece != ' ':
    #         self.clickedPieceIcon = self.piece(self.clickedPiece)
    #         if not self.clickedPieceIcon.isNull():
    #             self.update()

    def addHighlight(self, highlight):
        """Adds highlight to the list and redraws view."""
        self.highlights.append(highlight)
        self.update()

    def removeHighlight(self, highlight):
        """Removes highlight from the list and redraws view."""
        try:
            self.highlights.remove(highlight)
            self.update()
        except ValueError:
            pass

    def removeHighlightsOfColor(self, color):
        """Removes all highlights of color."""
        # NOTE: Need to loop through the reversed list, otherwise an element will be skipped if an element was removed
        # in the previous iteration.
        for highlight in reversed(self.highlights):
            if highlight.color == color:
                self.removeHighlight(highlight)

    def drawHighlights(self, painter):
        """Draws all recognized highlights stored in the list."""
        for highlight in self.highlights:
            if highlight.Type == self.SquareHighlight.Type:
                rect = self.squareRect(highlight.file, highlight.rank)
                painter.fillRect(rect, highlight.color)

    def highlightPlayer(self, player):
        """Adds highlight for player to indicate turn. Removes highlights for other players if they exist."""
        self.addHighlight(self.playerHighlights[player])
        for otherPlayer in self.playerHighlights:
            if otherPlayer != player:
                try:
                    self.removeHighlight(self.playerHighlights[otherPlayer])
                except ValueError:
                    pass

    def resetHighlights(self):
        """Clears list of highlights and redraws view."""
        self.highlights = []
        self.update()

    class PlayerName(QPushButton):
        """Editable player name label."""
        def __init__(self):
            super().__init__()
            self.setFixedSize(150, 50)
            self.setText('Player Name')
            self.setStyleSheet("""
            QPushButton {border: none; font-weight: bold;}
            QPushButton[player='red'] {color: #bf3b43;}
            QPushButton[player='blue'] {color: #4185bf;}
            QPushButton[player='yellow'] {color: #c09526;}
            QPushButton[player='green'] {color: #4e9161;}
            """)

    class PlayerNameEdit(QLineEdit):
        """Player name edit field."""
        focusOut = pyqtSignal()

        def __init__(self):
            super().__init__()
            self.setFixedSize(150, 50)
            self.setAlignment(Qt.AlignCenter)
            self.setFrame(False)
            self.setAttribute(Qt.WA_MacShowFocusRect, 0)
            self.installEventFilter(self)
            self.setStyleSheet("""
            QLineEdit {font-weight: bold;}
            QLineEdit[player='red'] {color: #bf3b43;}
            QLineEdit[player='blue'] {color: #4185bf;}
            QLineEdit[player='yellow'] {color: #c09526;}
            QLineEdit[player='green'] {color: #4e9161;}
            """)

        def eventFilter(self, object, event):
            """Handles focusOut event."""
            if event.type() == QEvent.FocusOut:
                self.focusOut.emit()
            return False

    def createPlayerLabels(self):
        """Adds editable player name labels to board view."""
        # Red player
        self.redName = self.PlayerName()
        self.redName.setProperty('player', 'red')
        self.redName.move(550, 650)
        self.redName.setParent(self)
        self.redName.show()
        self.redName.clicked.connect(lambda: self.editPlayerName(self.redNameEdit))
        self.redNameEdit = self.PlayerNameEdit()
        self.redNameEdit.setProperty('player', 'red')
        self.redNameEdit.move(550, 650)
        self.redNameEdit.setParent(self)
        self.redNameEdit.show()
        self.redNameEdit.setHidden(True)
        self.redNameEdit.returnPressed.connect(lambda: self.setPlayerName(self.redName))
        self.redNameEdit.focusOut.connect(lambda: self.setPlayerName(self.redName))
        # Blue player
        self.blueName = self.PlayerName()
        self.blueName.setProperty('player', 'blue')
        self.blueName.move(0, 650)
        self.blueName.setParent(self)
        self.blueName.show()
        self.blueName.clicked.connect(lambda: self.editPlayerName(self.blueNameEdit))
        self.blueNameEdit = self.PlayerNameEdit()
        self.blueNameEdit.setProperty('player', 'blue')
        self.blueNameEdit.move(0, 650)
        self.blueNameEdit.setParent(self)
        self.blueNameEdit.show()
        self.blueNameEdit.setHidden(True)
        self.blueNameEdit.returnPressed.connect(lambda: self.setPlayerName(self.blueName))
        self.blueNameEdit.focusOut.connect(lambda: self.setPlayerName(self.blueName))
        # Yellow player
        self.yellowName = self.PlayerName()
        self.yellowName.setProperty('player', 'yellow')
        self.yellowName.move(0, 0)
        self.yellowName.setParent(self)
        self.yellowName.show()
        self.yellowName.clicked.connect(lambda: self.editPlayerName(self.yellowNameEdit))
        self.yellowNameEdit = self.PlayerNameEdit()
        self.yellowNameEdit.setProperty('player', 'yellow')
        self.yellowNameEdit.move(0, 0)
        self.yellowNameEdit.setParent(self)
        self.yellowNameEdit.show()
        self.yellowNameEdit.setHidden(True)
        self.yellowNameEdit.returnPressed.connect(lambda: self.setPlayerName(self.yellowName))
        self.yellowNameEdit.focusOut.connect(lambda: self.setPlayerName(self.yellowName))
        # Green player
        self.greenName = self.PlayerName()
        self.greenName.setProperty('player', 'green')
        self.greenName.move(550, 0)
        self.greenName.setParent(self)
        self.greenName.show()
        self.greenName.clicked.connect(lambda: self.editPlayerName(self.greenNameEdit))
        self.greenNameEdit = self.PlayerNameEdit()
        self.greenNameEdit.setProperty('player', 'green')
        self.greenNameEdit.move(550, 0)
        self.greenNameEdit.setParent(self)
        self.greenNameEdit.show()
        self.greenNameEdit.setHidden(True)
        self.greenNameEdit.returnPressed.connect(lambda: self.setPlayerName(self.greenName))
        self.greenNameEdit.focusOut.connect(lambda: self.setPlayerName(self.greenName))

    def editPlayerName(self, nameEdit):
        """Activates player name edit field."""
        name = self.sender()
        name.setHidden(True)
        nameEdit.setHidden(False)
        nameEdit.setFocus(True)

    def setPlayerName(self, name):
        """Updates player name label and deactivates player name edit field."""
        nameEdit = self.sender()
        name.setText(nameEdit.text())
        nameEdit.setHidden(True)
        name.setHidden(False)
        self.playerNameEdited.emit(self.redName.text(), self.blueName.text(), self.yellowName.text(),
                                   self.greenName.text())

    def setPlayerNames(self, red, blue, yellow, green):
        """Sets player names to names obtained from PGN4 file."""
        if red == '?':
            red = 'Player Name'
        if blue == '?':
            blue = 'Player Name'
        if yellow == '?':
            yellow = 'Player Name'
        if green == '?':
            green = 'Player Name'
        self.redName.setText(red)
        self.blueName.setText(blue)
        self.yellowName.setText(yellow)
        self.greenName.setText(green)
