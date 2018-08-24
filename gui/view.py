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

from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QPlainTextEdit, QFrame
from PyQt5.QtCore import Qt, QSize, QRect, QRectF, QPoint, pyqtSignal, QEvent, QByteArray, QDataStream, QIODevice, \
    QMimeData, QLineF, QSettings
from PyQt5.QtGui import QPainter, QPalette, QColor, QFont, QDrag, QIcon, QCursor, QPolygonF, QPainterPath, QPen, \
    QBrush, QGuiApplication
from collections import deque
from gui.board import Board

# Load settings
COM = '4pc'
APP = '4PlayerChess'
SETTINGS = QSettings(COM, APP)


class View(QWidget):
    """The View is responsible for rendering the current state of the board and signalling user interaction to the
    underlying logic."""
    clicked = pyqtSignal(QPoint)
    squareSizeChanged = pyqtSignal(QSize)
    playerNameEdited = pyqtSignal(str, str, str, str)
    pieceMoved = pyqtSignal(QPoint, QPoint)
    dragStarted = pyqtSignal(QPoint)

    def __init__(self, *_):
        super().__init__()
        self.squareSize = QSize(50, 50)
        self.board = Board(14, 14)
        self.pieces = {}
        self.highlights = []
        self.playerHighlights = {'r': self.PlayerHighlight(12, 1, QColor('#bf3b43')),
                                 'b': self.PlayerHighlight(1, 1, QColor('#4185bf')),
                                 'y': self.PlayerHighlight(1, 12, QColor('#c09526')),
                                 'g': self.PlayerHighlight(12, 12, QColor('#4e9161'))}
        # Player labels
        self.redName = None
        self.redNameEdit = None
        self.blueName = None
        self.blueNameEdit = None
        self.yellowName = None
        self.yellowNameEdit = None
        self.greenName = None
        self.greenNameEdit = None
        self.createPlayerLabels()
        # Drag-drop
        self.setAcceptDrops(True)
        self.dragStart = None
        self.clickedSquare = None
        self.maskedSquare = None
        self.mouseButton = None
        self.currentPlayer = None
        # Board orientation
        self.orientation = deque(['r', 'b', 'y', 'g'])
        # Arrows and square highlight
        self.arrowStart = None
        self.keyModifier = None
        self.arrowColor = None
        self.squareColor = None

    class SquareHighlight:
        """A square highlight."""
        Type = 1

        def __init__(self, file, rank, color):
            self.file = file
            self.rank = rank
            self.color = color

    class PlayerHighlight(SquareHighlight):
        """A player highlight. Same as square highlight, just renamed for convenience (unaltered subclass)."""
        pass

    class Arrow:
        """An arrow highlight, to show possible moves on the board."""
        Type = 2

        def __init__(self, origin, target, color):
            self.origin = origin
            self.target = target
            self.color = color

    def rotateBoard(self, rotation):
        """Rotates board view (clockwise +, counterclockwise -)."""
        self.orientation.rotate(rotation)
        self.movePlayerLabels(self.orientation[0])
        self.removeArrows()
        self.update()

    def autoRotate(self, rotation):
        """Automatically rotates board after move is made or undone."""
        if SETTINGS.value('autorotate'):
            self.rotateBoard(rotation)

    def setCurrentPlayer(self, player):
        """Updates current player, if changed."""
        if self.currentPlayer == player:
            return
        self.currentPlayer = player

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
            board.autoRotate.connect(self.autoRotate)
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
        return QSize(self.squareSize.width() * self.board.files, self.squareSize.height() * self.board.ranks)

    def squareRect(self, file, rank, orientation=None):
        """Returns square of type QRect at position (file, rank)."""
        sqSize = self.squareSize
        if orientation == 'b':
            return QRect(QPoint((self.board.ranks - (rank + 1)) * sqSize.width(),
                                (self.board.files - (file + 1)) * sqSize.height()), sqSize)
        elif orientation == 'y':
            return QRect(QPoint((self.board.files - (file + 1)) * sqSize.width(), rank * sqSize.height()), sqSize)
        elif orientation == 'g':
            return QRect(QPoint(rank * sqSize.width(), file * sqSize.height()), sqSize)
        else:  # red by default
            return QRect(QPoint(file * sqSize.width(), (self.board.ranks - (rank + 1)) * sqSize.height()), sqSize)

    def squareCenter(self, square):
        """Returns center of square as QPoint."""
        sqSize = self.squareSize
        file = square.x()
        rank = square.y()
        return QPoint(file * sqSize.width() + sqSize.width() / 2,
                      (self.board.ranks - (rank + 1)) * sqSize.height() + sqSize.height() / 2)

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
        # Draw square highlights
        self.drawSquareHighlights(painter)
        painter.fillRect(self.squareRect(12, 1, self.orientation[0]), QColor('#40bf3b43'))
        painter.fillRect(self.squareRect(1, 1, self.orientation[0]), QColor('#404185bf'))
        painter.fillRect(self.squareRect(1, 12, self.orientation[0]), QColor('#40c09526'))
        painter.fillRect(self.squareRect(12, 12, self.orientation[0]), QColor('#404e9161'))
        # Show or hide player names
        if SETTINGS.value('shownames'):
            self.showNames()
        else:
            self.hideNames()
        # Draw pieces
        for rank in range(self.board.ranks):
            for file in range(self.board.files):
                if not self.maskedSquare == QPoint(file, rank):  # When dragging a piece, don't paint it
                    self.drawPiece(painter, file, rank)
        # Draw coordinates
        if SETTINGS.value('showcoordinates'):
            for y in range(14):
                x = 0 if 2 < y < 11 else 3
                square = self.squareRect(x, y)
                square.moveTopLeft(QPoint(square.x() + 1, square.y() + 1))
                square = QRectF(square)  # Only works with QRectF, so convert
                if self.orientation[0] == 'b':
                    file = self.board.files - (y + 1)
                    rank = self.board.ranks - (x + 1)
                elif self.orientation[0] == 'y':
                    file = self.board.files - (x + 1)
                    rank = y
                elif self.orientation[0] == 'g':
                    file = y
                    rank = x
                else:  # red by default
                    file = x
                    rank = self.board.ranks - (y + 1)
                color = self.palette().color(QPalette.Light) if (file + rank) % 2 \
                    else self.palette().color(QPalette.Dark)
                font = QFont('Trebuchet MS', 10, QFont.Bold)
                painter.setPen(color)
                painter.setFont(font)
                if self.orientation[0] in 'ry':
                    painter.drawText(square, str(self.board.ranks - rank))
                else:
                    painter.drawText(square, chr(self.board.files - (file + 1) + 97))
            for x in range(14):
                y = 0 if 2 < x < 11 else 3
                square = self.squareRect(x, y)
                square.moveTopLeft(QPoint(square.x() - 1, square.y() - 1))
                square = QRectF(square)  # Only works with QRectF, so convert
                if self.orientation[0] == 'b':
                    file = self.board.files - (y + 1)
                    rank = self.board.ranks - (x + 1)
                elif self.orientation[0] == 'y':
                    file = self.board.files - (x + 1)
                    rank = y
                elif self.orientation[0] == 'g':
                    file = y
                    rank = x
                else:  # red by default
                    file = x
                    rank = self.board.ranks - (y + 1)
                color = self.palette().color(QPalette.Light) if (file + rank) % 2 \
                    else self.palette().color(QPalette.Dark)
                font = QFont('Trebuchet MS', 10, QFont.Bold)
                painter.setPen(color)
                painter.setFont(font)
                if self.orientation[0] in 'ry':
                    painter.drawText(square, Qt.AlignBottom | Qt.AlignRight, chr(file + 97))
                else:
                    painter.drawText(square, Qt.AlignBottom | Qt.AlignRight, str(rank + 1))
        # Draw arrows
        self.drawArrows(painter)
        painter.end()

    def drawSquare(self, painter, file, rank):
        """Draws dark or light square at position (file, rank) using painter."""
        rect = self.squareRect(file, rank, self.orientation[0])
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
        rect = self.squareRect(file, rank, self.orientation[0])
        char = self.board.getData(file, rank)
        if char != ' ':
            icon = self.piece(char)
            if not icon.isNull():
                icon.paint(painter, rect, Qt.AlignCenter)

    def squareAt(self, point, orientation=None):
        """Returns square (file, rank) of type QPoint that contains point."""
        sqSize = self.squareSize
        x = point.x() // sqSize.width()
        y = point.y() // sqSize.height()
        if (x < 0) or (x > 13) or (y < 0) or (y > 13):
            return QPoint()
        elif orientation == 'b':
            return QPoint(self.board.files - (y + 1), self.board.ranks - (x + 1))
        elif orientation == 'y':
            return QPoint(self.board.files - (x + 1), y)
        elif orientation == 'g':
            return QPoint(y, x)
        else:  # red by default
            return QPoint(x, self.board.ranks - (y + 1))

    def mouseReleaseEvent(self, event):
        """Implements mouseReleaseEvent() method. Emits signal with clicked square (QPoint) in case of a left-click.
        Adds arrows and square highlights in case of a right-click (drag)."""
        point = self.squareAt(event.pos(), self.orientation[0])
        arrowEnd = self.squareAt(event.pos())
        if self.mouseButton == Qt.RightButton:
            if self.keyModifier == Qt.Key_1:
                self.arrowColor = QColor('#ab272f')
                self.squareColor = QColor('#80ab272f')
            elif self.keyModifier == Qt.Key_2:
                self.arrowColor = QColor('#2d71ab')
                self.squareColor = QColor('#802d71ab')
            elif self.keyModifier == Qt.Key_3:
                self.arrowColor = QColor('#ac8112')
                self.squareColor = QColor('#80ac8112')
            elif self.keyModifier == Qt.Key_4:
                self.arrowColor = QColor('#3a7d4d')
                self.squareColor = QColor('#803a7d4d')
            elif self.keyModifier == Qt.Key_0:
                self.arrowColor = QColor('#ff8c00')
                self.squareColor = QColor('#80ff8c00')
            else:
                if SETTINGS.value('autocolor'):
                    if self.orientation[0] == 'r':
                        self.arrowColor = QColor('#ab272f')
                        self.squareColor = QColor('#80ab272f')
                    elif self.orientation[0] == 'b':
                        self.arrowColor = QColor('#2d71ab')
                        self.squareColor = QColor('#802d71ab')
                    elif self.orientation[0] == 'y':
                        self.arrowColor = QColor('#ac8112')
                        self.squareColor = QColor('#80ac8112')
                    elif self.orientation[0] == 'g':
                        self.arrowColor = QColor('#3a7d4d')
                        self.squareColor = QColor('#803a7d4d')
                else:
                    self.arrowColor = QColor('#ff8c00')
                    self.squareColor = QColor('#80ff8c00')
            origin = self.squareCenter(self.arrowStart)
            target = self.squareCenter(arrowEnd)
            if origin == target:
                sq = self.squareAt(origin)
                file = sq.x()
                rank = sq.y()
                color = self.squareColor
                square = self.SquareHighlight(file, rank, color)
                # If already exists, remove existing
                removed = 0
                for highlight in reversed(self.highlights):
                    if highlight.Type == self.SquareHighlight.Type and highlight.file == file and \
                            highlight.rank == rank and highlight.color == color:
                        self.removeHighlight(highlight)
                        removed += 1
                if not removed:
                    # Do not allow drawing outside board
                    if not ((file < 3 and rank < 3) or (file < 3 and rank > 10) or
                            (file > 10 and rank < 3) or (file > 10 and rank > 10)):
                        self.addHighlight(square)
            else:
                color = self.arrowColor
                arrow = self.Arrow(origin, target, color)
                # If already exists, remove existing
                removed = 0
                for highlight in reversed(self.highlights):
                    if highlight.Type == self.Arrow.Type and highlight.origin == origin and \
                            highlight.target == target and highlight.color == color:
                        self.removeHighlight(highlight)
                        removed += 1
                if not removed:
                    # Do not allow drawing outside board
                    fromSquare = self.squareAt(origin)
                    toSquare = self.squareAt(target)
                    fromFile = fromSquare.x()
                    fromRank = fromSquare.y()
                    toFile = toSquare.x()
                    toRank = toSquare.y()
                    if not ((fromFile < 3 and fromRank < 3) or (fromFile < 3 and fromRank > 10) or
                            (fromFile > 10 and fromRank < 3) or (fromFile > 10 and fromRank > 10)) and not \
                            ((toFile < 3 and toRank < 3) or (toFile < 3 and toRank > 10) or
                             (toFile > 10 and toRank < 3) or (toFile > 10 and toRank > 10)):
                        self.addHighlight(arrow)
            return
        elif self.mouseButton == Qt.LeftButton:
            if point.isNull():
                return
            self.clicked.emit(point)
        else:
            return

    def mousePressEvent(self, event):
        """Implements mousePressEvent() method. Records drag start position, origin square and mouse button."""
        self.dragStart = event.pos()
        self.clickedSquare = self.squareAt(event.pos(), self.orientation[0])
        self.mouseButton = event.buttons()
        self.arrowStart = self.squareAt(event.pos())
        # If empty square clicked with left mouse button, remove arrows
        if event.buttons() == Qt.LeftButton and \
                self.board.getData(self.clickedSquare.x(), self.clickedSquare.y()) == ' ':
            if self.keyModifier == Qt.Key_1:
                self.removeArrows([QColor('#80ab272f'), QColor('#ab272f')])
            elif self.keyModifier == Qt.Key_2:
                self.removeArrows([QColor('#802d71ab'), QColor('#2d71ab')])
            elif self.keyModifier == Qt.Key_3:
                self.removeArrows([QColor('#80ac8112'), QColor('#ac8112')])
            elif self.keyModifier == Qt.Key_4:
                self.removeArrows([QColor('#803a7d4d'), QColor('#3a7d4d')])
            elif self.keyModifier == Qt.Key_0:
                self.removeArrows([QColor('#80ff8c00'), QColor('#ff8c00')])
            else:
                self.removeArrows()

    def mouseMoveEvent(self, event):
        """Implements mouseMoveEvent() method. Executes drag action."""
        if not event.buttons() == Qt.LeftButton:
            return
        if not self.clickedSquare or not self.dragStart:
            return
        if (event.pos() - self.dragStart).manhattanLength() < 5:
            return
        char = self.board.getData(self.clickedSquare.x(), self.clickedSquare.y())
        if char[0] != self.currentPlayer:
            return
        if char != ' ':
            icon = self.piece(char)
            if icon.isNull():
                return
            iconPosition = self.squareRect(self.clickedSquare.x(), self.clickedSquare.y(),
                                           self.orientation[0]).topLeft()
            offset = QPoint(event.pos() - iconPosition)
            # Pixmap shown under cursor while dragging
            dpr = 2  # device pixel ratio
            pixmap = icon.pixmap(QSize(self.squareSize.width() * dpr, self.squareSize.height() * dpr))
            pixmap.setDevicePixelRatio(dpr)
            # Serialize drag-drop data into QByteArray
            data = QByteArray()
            dataStream = QDataStream(data, QIODevice.WriteOnly)
            dataStream << icon << offset
            # Custom MIME data
            mimeData = QMimeData()
            mimeData.setData('dragdrop', data)
            # Drag action
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(self.squareSize.width() / 2, self.squareSize.height() / 2))
            self.maskedSquare = self.clickedSquare
            self.dragStarted.emit(self.clickedSquare)
            drag.exec_()
            self.maskedSquare = None

    def dragEnterEvent(self, event):
        """Implements dragEnterEvent() method."""
        if event.mimeData().hasFormat('dragdrop'):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Implements dragMoveEvent() method."""
        if event.mimeData().hasFormat('dragdrop'):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Implements dragLeaveEvent() method."""
        # Keep cursor on the board while dragging
        cursor = QCursor()
        position = cursor.pos()
        topLeft = self.mapToGlobal(self.geometry().topLeft()) - self.geometry().topLeft()
        bottomRight = self.mapToGlobal(self.geometry().bottomRight()) - self.geometry().topLeft()
        bound = lambda x, l, u: l if x < l else u if x > u else x
        x = bound(position.x(), topLeft.x() + 1, bottomRight.x() - 1)
        y = bound(position.y(), topLeft.y() + 1, bottomRight.y() - 1)
        if x != position.x() or y != position.y():
            cursor.setPos(x, y)

    def dropEvent(self, event):
        """Implements dropEvent() method. Handles drop action."""
        if event.mimeData().hasFormat('dragdrop'):
            # Read data serialized from the QByteArray
            data = event.mimeData().data('dragdrop')
            dataStream = QDataStream(data, QIODevice.ReadOnly)
            icon = QIcon()
            offset = QPoint()
            dataStream >> icon >> offset
            # Send signal to make the move
            square = self.squareAt(event.pos(), self.orientation[0])
            self.pieceMoved.emit(self.clickedSquare, square)
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

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
        for highlight in reversed(self.highlights):  # reversed list, because modifying while looping
            if highlight.color == color:
                self.removeHighlight(highlight)

    def removeArrows(self, colors=None):
        """Removes all arrows and highlighted squares drawn on the board."""
        if colors:
            for color in colors:
                self.removeHighlightsOfColor(color)
        else:
            colors = [QColor('#80ff8c00'), QColor('#80ab272f'), QColor('#802d71ab'), QColor('#80ac8112'),
                      QColor('#803a7d4d')]
            for highlight in reversed(self.highlights):  # reversed list, because modifying while looping
                if highlight.Type == self.Arrow.Type:
                    self.removeHighlight(highlight)
                elif highlight.Type == self.SquareHighlight.Type and highlight.color in colors:
                    self.removeHighlight(highlight)

    def drawSquareHighlights(self, painter):
        """Draws all recognized highlights stored in the list."""
        for highlight in self.highlights:
            if highlight.Type == self.SquareHighlight.Type:
                colors = [QColor('#80ff8c00'), QColor('#80ab272f'), QColor('#802d71ab'), QColor('#80ac8112'),
                          QColor('#803a7d4d')]
                if highlight.color in colors:
                    rect = self.squareRect(highlight.file, highlight.rank)
                else:
                    rect = self.squareRect(highlight.file, highlight.rank, self.orientation[0])
                painter.fillRect(rect, highlight.color)

    def drawArrows(self, painter):
        """Draws arrows on the board."""
        for highlight in self.highlights:
            if highlight.Type == self.Arrow.Type:
                lineWidth = 10
                sqSize = self.squareSize
                painter.setPen(QPen(highlight.color, lineWidth, Qt.SolidLine, Qt.RoundCap))
                origin = highlight.origin
                target = highlight.target
                dx = target.x() - origin.x()
                dy = target.y() - origin.y()
                # Knight jumps
                if dx == sqSize.width() and dy == -2 * sqSize.height():
                    corner = QPoint(origin.x(), origin.y() - 2 * sqSize.height())
                    line = QLineF(origin, corner)
                    painter.drawLine(line)
                    origin = corner
                elif dx == 2 * sqSize.width() and dy == -sqSize.height():
                    corner = QPoint(origin.x() + 2 * sqSize.width(), origin.y())
                    line = QLineF(origin, corner)
                    painter.drawLine(line)
                    origin = corner
                elif dx == 2 * sqSize.width() and dy == sqSize.height():
                    corner = QPoint(origin.x() + 2 * sqSize.width(), origin.y())
                    line = QLineF(origin, corner)
                    painter.drawLine(line)
                    origin = corner
                elif dx == sqSize.width() and dy == 2 * sqSize.height():
                    corner = QPoint(origin.x(), origin.y() + 2 * sqSize.height())
                    line = QLineF(origin, corner)
                    painter.drawLine(line)
                    origin = corner
                elif dx == -sqSize.width() and dy == 2 * sqSize.height():
                    corner = QPoint(origin.x(), origin.y() + 2 * sqSize.height())
                    line = QLineF(origin, corner)
                    painter.drawLine(line)
                    origin = corner
                elif dx == -2 * sqSize.width() and dy == sqSize.height():
                    corner = QPoint(origin.x() - 2 * sqSize.width(), origin.y())
                    line = QLineF(origin, corner)
                    painter.drawLine(line)
                    origin = corner
                elif dx == -2 * sqSize.width() and dy == -sqSize.height():
                    corner = QPoint(origin.x() - 2 * sqSize.width(), origin.y())
                    line = QLineF(origin, corner)
                    painter.drawLine(line)
                    origin = corner
                elif dx == -sqSize.width() and dy == -2 * sqSize.height():
                    corner = QPoint(origin.x(), origin.y() - 2 * sqSize.height())
                    line = QLineF(origin, corner)
                    painter.drawLine(line)
                    origin = corner
                # Other moves (and second part of knight jump)
                line = QLineF(origin, target)
                angle = line.angle()
                tip = line.p2()
                line.setLength(line.length() - 2 * lineWidth)
                painter.drawLine(line)
                tipOffset = line.p2()
                leftBase = QLineF()
                leftBase.setP1(tipOffset)
                leftBase.setLength(lineWidth)
                leftBase.setAngle(angle - 90)
                left = leftBase.p2()
                rightBase = QLineF()
                rightBase.setP1(tipOffset)
                rightBase.setLength(lineWidth)
                rightBase.setAngle(angle + 90)
                right = rightBase.p2()
                arrowHead = QPolygonF([left, right, tip])
                path = QPainterPath()
                path.addPolygon(arrowHead)
                painter.fillPath(path, QBrush(highlight.color))

    def highlightPlayer(self, player):
        """Adds highlight for player to indicate turn. Removes highlights for other players if they exist."""
        self.addHighlight(self.playerHighlights[player])
        for otherPlayer in self.playerHighlights:
            if otherPlayer != player:
                try:
                    self.removeHighlight(self.playerHighlights[otherPlayer])
                except ValueError:
                    pass

    def highlightChecks(self):
        """Adds red square highlight for kings in check."""
        checkColor = QColor('#ccff0000')
        for highlight in reversed(self.highlights):  # reversed list, because modifying while looping
            if highlight.color == checkColor:
                self.removeHighlight(highlight)
        for color in range(4):
            inCheck, (file, rank) = self.board.kingInCheck(color)
            if inCheck:
                highlight = self.SquareHighlight(file, rank, checkColor)
                self.addHighlight(highlight)

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

        def eventFilter(self, object_, event):
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

    def movePlayerLabels(self, orientation):
        """Moves player labels when board orientation is changed."""
        if orientation == 'b':
            self.redName.move(550, 0)
            self.redNameEdit.move(550, 0)
            self.blueName.move(550, 650)
            self.blueNameEdit.move(550, 650)
            self.yellowName.move(0, 650)
            self.yellowNameEdit.move(0, 650)
            self.greenName.move(0, 0)
            self.greenNameEdit.move(0, 0)
        elif orientation == 'y':
            self.redName.move(0, 0)
            self.redNameEdit.move(0, 0)
            self.blueName.move(550, 0)
            self.blueNameEdit.move(550, 0)
            self.yellowName.move(550, 650)
            self.yellowNameEdit.move(550, 650)
            self.greenName.move(0, 650)
            self.greenNameEdit.move(0, 650)
        elif orientation == 'g':
            self.redName.move(0, 650)
            self.redNameEdit.move(0, 650)
            self.blueName.move(0, 0)
            self.blueNameEdit.move(0, 0)
            self.yellowName.move(550, 0)
            self.yellowNameEdit.move(550, 0)
            self.greenName.move(550, 650)
            self.greenNameEdit.move(550, 650)
        else:  # red by default
            self.redName.move(550, 650)
            self.redNameEdit.move(550, 650)
            self.blueName.move(0, 650)
            self.blueNameEdit.move(0, 650)
            self.yellowName.move(0, 0)
            self.yellowNameEdit.move(0, 0)
            self.greenName.move(550, 0)
            self.greenNameEdit.move(550, 0)

    def hideNames(self):
        """Hides player name labels."""
        self.redName.setHidden(True)
        self.blueName.setHidden(True)
        self.yellowName.setHidden(True)
        self.greenName.setHidden(True)

    def showNames(self):
        """Shows player name labels."""
        self.redName.setHidden(False)
        self.blueName.setHidden(False)
        self.yellowName.setHidden(False)
        self.greenName.setHidden(False)

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


class Comment(QPushButton):
    # TODO make comment wrap
    """Comment label."""
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 90)
        self.setStyleSheet("""
            border: 0px;
            padding: 4px;
            border-radius: 0px;
            background-color: white;
            text-align: top left;
            color: grey;
            font-family: Trebuchet MS;
            """)


class CommentEdit(QPlainTextEdit):
    """Comment edit field."""
    focusOut = pyqtSignal()

    def __init__(self, *_):
        super().__init__()
        self.setFixedSize(300, 90)
        self.setFrameShape(QFrame.NoFrame)
        self.installEventFilter(self)
        self.setFont(QFont('Trebuchet MS'))

    def eventFilter(self, object_, event):
        """Handles focusOut and returnPressed event."""
        if event.type() == QEvent.FocusOut:
            self.focusOut.emit()
        return False
