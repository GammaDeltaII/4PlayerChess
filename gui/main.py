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

from PyQt5.QtWidgets import QWidget, QMainWindow, QSizePolicy, QLayout
from PyQt5.QtCore import Qt, QObject, QSize, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QPalette, QIcon, QColor
from collections import deque
from ui.mainwindow import Ui_mainWindow


class MainWindow(QMainWindow, Ui_mainWindow):
    """The GUI main window."""
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Create view and algorithm instances
        self.view = View()
        self.gridLayout.addWidget(self.view, 0, 0, 3, 1)
        self.algorithm = Teams()

        # Set piece icons
        pieces = ['rP', 'rN', 'rR', 'rB', 'rQ', 'rK',
                  'bP', 'bN', 'bR', 'bB', 'bQ', 'bK',
                  'yP', 'yN', 'yR', 'yB', 'yQ', 'yK',
                  'gP', 'gN', 'gR', 'gB', 'gQ', 'gK']
        for piece in pieces:
            self.view.setPiece(piece, QIcon('resources/img/pieces/'+piece+'.svg'))

        # Set view size based on board square size
        self.view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.view.setSquareSize(QSize(50, 50))
        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        # Connect signals
        self.view.clicked.connect(self.viewClicked)
        self.algorithm.boardChanged.connect(self.view.setBoard)  # If algorithm changes board, view must update board
        self.algorithm.currentPlayerChanged.connect(self.view.highlightPlayer)

        # Connect actions
        self.actionQuit.triggered.connect(self.close)
        self.actionNew_Game.triggered.connect(self.algorithm.newGame)
        self.boardResetButton.clicked.connect(self.algorithm.newGame)
        self.boardResetButton.clicked.connect(self.view.repaint)    # Immediate repaint as opposed to scheduled update

        # Start new game
        self.algorithm.newGame()

        # Initialize clicked point and highlighted square
        self.clickPoint = QPoint()
        self.selectedSquare = 0

    def viewClicked(self, square):
        """Handles user click event to move clicked piece to clicked square."""
        if self.clickPoint.isNull():
            if self.view.board.getData(square.x(), square.y()) != ' ':
                self.clickPoint = square
                self.selectedSquare = self.view.SquareHighlight(square.x(), square.y(), QColor(255, 255, 0, 50))
                self.view.addHighlight(self.selectedSquare)
        else:
            if square != self.clickPoint:
                self.algorithm.move(self.clickPoint.x(), self.clickPoint.y(), square.x(), square.y())
            self.clickPoint = QPoint()
            self.view.removeHighlight(self.selectedSquare)
            self.selectedSquare = 0


class Board(QObject):
    """The Board is the actual chess board and is the data structure shared between the View and the Algorithm."""
    boardReset = pyqtSignal()
    dataChanged = pyqtSignal(int, int)

    def __init__(self, files, ranks):
        super().__init__()
        self.files = files
        self.ranks = ranks
        self.boardData = []
        self.initBoard()

    def initBoard(self):
        """Initializes board with empty squares."""
        self.boardData = [' '] * self.files * self.ranks
        self.boardReset.emit()

    def getData(self, file, rank):
        """Gets board data from square (file, rank)."""
        return self.boardData[file+rank*self.files]

    def setData(self, file, rank, data):
        """Sets board data at square (file, rank) to data."""
        index = file+rank*self.files
        if self.boardData[index] == data:
            return
        self.boardData[index] = data
        self.dataChanged.emit(file, rank)

    def movePiece(self, fromFile, fromRank, toFile, toRank):
        """Moves piece from square (fromFile, fromRank) to square (toFile, toRank)."""
        self.setData(toFile, toRank, self.getData(fromFile, fromRank))
        self.setData(fromFile, fromRank, ' ')

    def setFen4(self, fen4):
        """Sets board position according to the FEN4 string fen4."""
        index = 0
        skip = 0
        for rank in reversed(range(self.ranks)):
            for file in range(self.files):
                if skip > 0:
                    char = ' '
                    skip -= 1
                else:
                    # Pieces are always two characters, skip value can be single or double digit
                    char = fen4[index]
                    index += 1
                    if char.isdigit():
                        # Check if next is also digit. If yes, treat as single number
                        next_ = fen4[index]
                        if next_.isdigit():
                            char += next_
                            index += 1
                        skip = int(char)
                        char = ' '
                        skip -= 1
                    # If not digit, then it is a two-character piece. Add next character
                    else:
                        char += fen4[index]
                        index += 1
                self.setData(file, rank, char)
            next_ = fen4[index]
            if next_ != '/' and next_ != ' ':
                # If no slash or space after rank, reset board
                self.initBoard()
                return
            else:   # Skip the slash
                index += 1

        self.boardReset.emit()


class Algorithm(QObject):
    """The Algorithm is the underlying logic responsible for changing the current state of the board."""
    boardChanged = pyqtSignal(Board)
    gameOver = pyqtSignal(str)
    currentPlayerChanged = pyqtSignal(str)

    NoResult, Team1Wins, Team2Wins, Draw = ['NoResult', 'Team1Wins', 'Team2Wins', 'Draw']   # Results
    NoPlayer, Red, Blue, Yellow, Green = ['NoPlayer', 'Red', 'Blue', 'Yellow', 'Green']     # Players
    playerQueue = deque([Red, Blue, Yellow, Green])

    def __init__(self):
        super().__init__()
        self.board = Board(14, 14)
        self.result = self.NoResult
        self.currentPlayer = self.NoPlayer

    def setResult(self, value):
        if self.result == value:
            return
        if self.result == self.NoResult:
            self.result = value
            self.gameOver.emit(self.result)
        else:
            self.result = value

    def setCurrentPlayer(self, value):
        if self.currentPlayer == value:
            return
        self.currentPlayer = value
        self.currentPlayerChanged.emit(self.currentPlayer)

    def setPlayerQueue(self, currentPlayer):
        while self.playerQueue[0] != currentPlayer:
            self.playerQueue.rotate(-1)

    def setBoard(self, board):
        """Sets board to new board."""
        if self.board == board:
            return
        self.board = board
        self.boardChanged.emit(self.board)

    def setupBoard(self):
        """Initializes board."""
        self.setBoard(Board(14, 14))

    def newGame(self):
        """Initializes board and sets starting position."""
        self.setupBoard()
        # Set starting position from FEN4
        self.board.setFen4('3yRyNyByKyQyByNyR3/3yPyPyPyPyPyPyPyP3/14/bRbP10gPgR/bNbP10gPgN/bBbP10gPgB/bKbP10gPgQ/'
                           'bQbP10gPgK/bBbP10gPgB/bNbP10gPgN/bRbP10gPgR/14/3rPrPrPrPrPrPrPrP3/3rRrNrBrQrKrBrNrR3 '
                           'r rKrQbKbQyKyQgKgQ - 0 1')
        self.setResult(self.NoResult)
        self.setCurrentPlayer(self.Red)
        self.setPlayerQueue(self.currentPlayer)

    def move(self, fromFile, fromRank, toFile, toRank):
        """This method must be overridden in each subclass to define the proper logic corresponding to Teams or FFA."""
        return False


class Teams(Algorithm):
    """A subclass of Algorithm for the 4-player chess Teams variant."""
    def __init__(self):
        super().__init__()

    def move(self, fromFile, fromRank, toFile, toRank):
        if self.currentPlayer == self.NoPlayer:
            return False
        # Check if square contains piece of current player. (A player may only move his own pieces.)
        fromData = self.board.getData(fromFile, fromRank)
        if self.currentPlayer == self.Red and fromData[0] != 'r':
            return False
        if self.currentPlayer == self.Blue and fromData[0] != 'b':
            return False
        if self.currentPlayer == self.Yellow and fromData[0] != 'y':
            return False
        if self.currentPlayer == self.Green and fromData[0] != 'g':
            return False

        # Check if move is within board
        if toFile < 0 or toFile > (self.board.files-1):
            return False
        if toRank < 0 or toRank > (self.board.ranks-1):
            return False
        if ((toFile < 3 and toRank < 3) or (toFile < 3 and toRank > 10) or
                (toFile > 10 and toRank < 3) or (toFile > 10 and toRank > 10)):
            return False

        # Check if target square is not occupied by friendly piece. (A player may not capture a friendly piece.)
        toData = self.board.getData(toFile, toRank)
        if self.currentPlayer == self.Red and (toData[0] == 'r' or toData[0] == 'y'):
            return False
        if self.currentPlayer == self.Blue and (toData[0] == 'b' or toData[0] == 'g'):
            return False
        if self.currentPlayer == self.Yellow and (toData[0] == 'y' or toData[0] == 'r'):
            return False
        if self.currentPlayer == self.Green and (toData[0] == 'g' or toData[0] == 'b'):
            return False

        # Make the move
        self.board.movePiece(fromFile, fromRank, toFile, toRank)

        # Rotate player queue and get next player from the queue (first element)
        self.playerQueue.rotate(-1)
        self.setCurrentPlayer(self.playerQueue[0])

        return True


# class FFA(Algorithm):
#     """A subclass of Algorithm for the 4-player chess Free-For-All (FFA) variant."""
#     def __init__(self):
#         super().__init__()


class View(QWidget):
    clicked = pyqtSignal(QPoint)
    squareSizeChanged = pyqtSignal(QSize)

    def __init__(self):
        super().__init__()
        self.squareSize = QSize(50, 50)
        self.board = Board(14, 14)
        self.pieces = {}
        self.highlights = []
        self.playerHighlights = {'Red': self.PlayerHighlight(12, 1, QColor('#bf3b43')),
                                 'Blue': self.PlayerHighlight(1, 1, QColor('#4185bf')),
                                 'Yellow': self.PlayerHighlight(1, 12, QColor('#c09526')),
                                 'Green': self.PlayerHighlight(12, 12, QColor('#4e9161'))}

    class SquareHighlight:
        Type = 1

        def __init__(self, file, rank, color):
            self.file = file
            self.rank = rank
            self.color = color

    class PlayerHighlight(SquareHighlight):
        pass

    def setBoard(self, board):
        """Sets board to new board."""
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
        self.updateGeometry()

    def setSquareSize(self, size):
        """Sets size of board squares and updates geometry accordingly."""
        if self.squareSize == size:
            return
        self.squareSize = size
        self.squareSizeChanged.emit(size)
        self.updateGeometry()

    def sizeHint(self):
        """Overrides QWidget sizeHint() method. Computes and returns size based on size of board squares."""
        return QSize(self.squareSize.width()*self.board.files, self.squareSize.height()*self.board.ranks)

    def squareRect(self, file, rank):
        """Returns square of type QRect at position (file, rank)."""
        sqSize = self.squareSize
        return QRect(QPoint(file*sqSize.width(), (self.board.ranks-(rank+1))*sqSize.height()), sqSize)

    def paintEvent(self, event):
        """Overrides QWidget paintEvent() method. Draws squares and pieces on the board."""
        painter = QPainter()
        painter.begin(self)
        # First draw squares, then highlights, then pieces
        for rank in range(self.board.ranks):
            for file in range(self.board.files):
                # Do not paint 3x3 sub-grids at the corners
                if not ((file < 3 and rank < 3) or (file < 3 and rank > 10) or
                        (file > 10 and rank < 3) or (file > 10 and rank > 10)):
                    self.drawSquare(painter, file, rank)
        self.drawHighlights(painter)
        painter.fillRect(self.squareRect(12, 1), QColor('#40bf3b43'))
        painter.fillRect(self.squareRect(1, 1), QColor('#404185bf'))
        painter.fillRect(self.squareRect(1, 12), QColor('#40c09526'))
        painter.fillRect(self.squareRect(12, 12), QColor('#404e9161'))
        for rank in range(self.board.ranks):
            for file in range(self.board.files):
                self.drawPiece(painter, file, rank)
        painter.end()

    def drawSquare(self, painter, file, rank):
        """Draws dark or light square at position (file, rank) using painter."""
        rect = self.squareRect(file, rank)
        fillColor = self.palette().color(QPalette.Midlight) if (file+rank) % 2 else self.palette().color(QPalette.Mid)
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
            if not icon.isNull():
                icon.paint(painter, rect, Qt.AlignCenter)

    def squareAt(self, point):
        """Returns square (file, rank) of type QPoint that contains point."""
        sqSize = self.squareSize
        file = point.x() / sqSize.width()
        rank = point.y() / sqSize.height()
        if (file < 0) or (file > self.board.files) or (rank < 0) or (rank > self.board.ranks):
            return QPoint()
        return QPoint(file, self.board.ranks-rank)

    def mouseReleaseEvent(self, event):
        """Overrides QWidget mouseReleaseEvent() method. Emits signal with clicked square of type QPoint as value."""
        point = self.squareAt(event.pos())
        if point.isNull():
            return
        self.clicked.emit(point)

    def addHighlight(self, highlight):
        self.highlights.append(highlight)
        self.update()

    def removeHighlight(self, highlight):
        self.highlights.remove(highlight)
        self.update()

    def drawHighlights(self, painter):
        for highlight in self.highlights:
            if highlight.Type == self.SquareHighlight.Type:
                rect = self.squareRect(highlight.file, highlight.rank)
                painter.fillRect(rect, highlight.color)

    def highlightPlayer(self, player):
        self.addHighlight(self.playerHighlights[player])
        for otherPlayer in self.playerHighlights:
            if otherPlayer != player:
                try:
                    self.removeHighlight(self.playerHighlights[otherPlayer])
                except ValueError:
                    pass

    def resetHighlights(self):
        self.highlights = []
        self.update()
