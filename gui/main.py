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

from PyQt5.QtWidgets import QWidget, QMainWindow, QSizePolicy, QLayout, QListWidget, QListWidgetItem, QListView, \
    QFrame, QAbstractItemView
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
        self.algorithm.fen4Generated.connect(self.fenField.setPlainText)
        self.algorithm.moveTreeChanged.connect(self.updateMoveTree)

        # Connect actions
        self.actionQuit.triggered.connect(self.close)
        self.actionNew_Game.triggered.connect(self.algorithm.newGame)
        self.actionNew_Game.triggered.connect(self.moveListWidget.clear)
        self.actionCopy_FEN4.triggered.connect(self.fenField.selectAll)
        self.actionCopy_FEN4.triggered.connect(self.fenField.copy)
        self.actionPaste_FEN4.triggered.connect(self.fenField.clear)
        self.actionPaste_FEN4.triggered.connect(self.fenField.paste)

        self.boardResetButton.clicked.connect(self.algorithm.newGame)
        self.boardResetButton.clicked.connect(self.view.repaint)  # Forced repaint
        self.boardResetButton.clicked.connect(self.moveListWidget.clear)
        self.getFenButton.clicked.connect(self.algorithm.getBoardState)
        self.getFenButton.clicked.connect(self.fenField.repaint)
        self.setFenButton.clicked.connect(self.setFen4)
        self.prevMoveButton.clicked.connect(self.algorithm.prevMove)
        self.prevMoveButton.clicked.connect(self.view.repaint)
        self.nextMoveButton.clicked.connect(self.algorithm.nextMove)
        self.nextMoveButton.clicked.connect(self.view.repaint)
        self.firstMoveButton.clicked.connect(self.algorithm.firstMove)
        self.firstMoveButton.clicked.connect(self.view.repaint)
        self.lastMoveButton.clicked.connect(self.algorithm.lastMove)
        self.lastMoveButton.clicked.connect(self.view.repaint)

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
                self.algorithm.makeMove(self.clickPoint.x(), self.clickPoint.y(), square.x(), square.y())
            self.clickPoint = QPoint()
            self.view.removeHighlight(self.selectedSquare)
            self.selectedSquare = 0

    def keyPressEvent(self, event):
        """Handles arrow key press events to go to previous, next, first or last move."""
        if event.key() == Qt.Key_Left:
            self.algorithm.prevMove()
        if event.key() == Qt.Key_Right:
            self.algorithm.nextMove()
        if event.key() == Qt.Key_Up:
            self.algorithm.firstMove()
        if event.key() == Qt.Key_Down:
            self.algorithm.lastMove()

    def setFen4(self):
        """Gets FEN4 from the text field to set the board accordingly."""
        fen4 = self.fenField.toPlainText()
        self.algorithm.setBoardState(fen4)
        self.view.repaint()  # Forced repaint

    def updateMoveTree(self, node):
        """Constructs the move list based on the move tree."""
        # Custom QListWidget class for rows in main list
        class Row(QListWidget):
            def __init__(self):
                super().__init__()
                self.setFlow(QListView.LeftToRight)
                self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.setWrapping(True)
                self.setFrameShape(QFrame.NoFrame)
                self.setSelectionMode(QAbstractItemView.NoSelection)
                self.setStyleSheet("color: rgb(0, 0, 0); font-weight: bold; font-size: 12; padding: 2px;")

            def sizeHint(self):
                """Overrides sizeHint() method."""
                # TODO implement more accurate sizeHint
                return QSize(300, 20 * (self.count()//7+1))  # Based on estimated number of moves per line

        # FIXME debug move list, when moving back and playing the same moves
        # List moves with move number and variation root and number (tuple), i.e. [(moveNum, move, root, var), (...)]
        moves = self.traverse(node)
        self.moveListWidget.clear()
        row = Row()
        prev = 0
        i = 0
        while i < len(moves):
            # Same variation -> continue
            if moves[i][-1] == prev:
                flag = (moves[i][0] - 1) % 4
                if flag == 0:
                    moveNum = str((moves[i][0] - 1) // 4 + 1) + '. '
                else:
                    moveNum = ''
                move = QListWidgetItem(moveNum + moves[i][1] + ' ')
                row.addItem(move)
            # New variation
            elif moves[i][-1] > prev:
                item = QListWidgetItem(self.moveListWidget)
                item.setSizeHint(row.sizeHint())
                self.moveListWidget.addItem(item)
                self.moveListWidget.setItemWidget(item, row)
                # Start of variation -> prepend opening bracket and three dots if no move number displayed
                flag = ((moves[i][0] - 1) % 4)
                if flag == 0:  # Red's move
                    moveNum = str((moves[i][0] - 1) // 4 + 1) + '. '
                elif flag == 1:  # Blue's move, add one dot
                    moveNum = str((moves[i][0] - 1) // 4 + 1) + '. . '
                elif flag == 2:  # Yellow's move, add two dots
                    moveNum = str((moves[i][0] - 1) // 4 + 1) + '. .. '
                else:  # Green's move, add three dots
                    moveNum = str((moves[i][0] - 1) // 4 + 1) + '. ... '
                move = QListWidgetItem('(' + moveNum + moves[i][1] + ' ')
                row = Row()
                if moves[i][-1] > 1:
                    row.setStyleSheet("color: rgb(150, 150, 150); font-weight: bold; font-size: 12; "
                                      "background-color: rgb(240, 240, 240); padding: 2px;")
                else:
                    row.setStyleSheet("color: rgb(100, 100, 100); font-weight: bold; font-size: 12; "
                                      "background-color: rgb(240, 240, 240); padding: 2px;")
                row.addItem(move)
            # End of variation, returning to previous variation
            elif moves[i][-1] < prev:
                # End of variation -> remove last space and append closing brackets
                row.item(row.count() - 1).setText(row.item(row.count() - 1).text()[:-1] + ')' * (prev - moves[i][-1]))
                item = QListWidgetItem(self.moveListWidget)
                item.setSizeHint(row.sizeHint())
                self.moveListWidget.addItem(item)
                self.moveListWidget.setItemWidget(item, row)
                flag = ((moves[i][0] - 1) % 4 == 0)
                if flag:
                    moveNum = str((moves[i][0] - 1) // 4 + 1) + '. '
                else:
                    moveNum = ''
                move = QListWidgetItem(moveNum + moves[i][1] + ' ')
                row = Row()
                if moves[i][-1] == 0:
                    pass  # Keep black color for main line
                elif moves[i][-1] > 1:
                    row.setStyleSheet("color: rgb(150, 150, 150); font-weight: bold; font-size: 12; "
                                      "background-color: rgb(240, 240, 240); padding: 2px;")
                else:
                    row.setStyleSheet("color: rgb(100, 100, 100); font-weight: bold; font-size: 12; "
                                      "background-color: rgb(240, 240, 240); padding: 2px;")
                row.addItem(move)
            # End of move list -> append rest of main line moves
            if i+1 == len(moves):
                item = QListWidgetItem(self.moveListWidget)
                item.setSizeHint(row.sizeHint())
                self.moveListWidget.addItem(item)
                self.moveListWidget.setItemWidget(item, row)
            prev = moves[i][-1]
            i += 1

    def traverse(self, node, moves=[], moveNum=0, root=None, var=0):
        """Traverses move tree to create list of moves, sorted by move number and variation (incl. variation root)."""
        # The tree is represented as a nested list with move strings, i.e. node = ['parent', [children]]
        parent = node[0]
        if not root:
            root = parent
        children = node[1]
        if children:
            for child in children:
                self.traverse(child, moves, moveNum + 1, root, var)
                var += 1
                root = parent
        elif not moves.count((moveNum, parent, root, var)):
            moves.append((moveNum, parent, root, var))
        # Sort moves: insert variations after the main line move
        i = 0
        while i < len(moves):
            variations = [var for var in moves if var[2] == moves[i][1]]
            # Sort variations by move and variation number
            variations = sorted(variations, key=lambda element: (element[-1], element[0]))
            moves = moves[:i+2] + variations + moves[i+2:]
            # Remove duplicate elements from the back
            moves.reverse()
            for move in moves:
                while moves.count(move) > 1:
                    moves.remove(move)
            moves.reverse()
            i += 1
        return moves


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
                # If no slash or space after rank, the FEN4 is invalid, so reset board
                self.initBoard()
                return
            else:  # Skip the slash
                index += 1
        self.boardReset.emit()

    def getFen4(self):
        """Generates FEN4 from current board state."""
        fen4 = ''
        skip = 0
        prev = ' '
        for rank in reversed(range(self.ranks)):
            for file in range(self.files):
                char = self.getData(file, rank)
                # If current square is empty, increment skip value
                if char == ' ':
                    skip += 1
                    prev = char
                else:
                    # If current square is not empty, but previous square was empty, append skip value to FEN4 string,
                    # unless the previous square was on the previous rank
                    if prev == ' ' and file != 0:
                        fen4 += str(skip)
                        skip = 0
                    # Append algebraic piece name to FEN4 string
                    fen4 += char
                    prev = char
            # If skip is non-zero at end of rank, append skip and reset to zero
            if skip > 0:
                fen4 += str(skip)
                skip = 0
            # Append slash at end of rank and append space after last rank
            if rank == 0:
                fen4 += ' '
            else:
                fen4 += '/'
        return fen4


class Algorithm(QObject):
    """The Algorithm is the underlying logic responsible for changing the current state of the board."""
    boardChanged = pyqtSignal(Board)
    gameOver = pyqtSignal(str)
    currentPlayerChanged = pyqtSignal(str)
    fen4Generated = pyqtSignal(str)
    moveTreeChanged = pyqtSignal(list)

    NoResult, Team1Wins, Team2Wins, Draw = ['NoResult', 'Team1Wins', 'Team2Wins', 'Draw']  # Results
    NoPlayer, Red, Blue, Yellow, Green = ['NoPlayer', 'r', 'b', 'y', 'g']  # Players
    playerQueue = deque([Red, Blue, Yellow, Green])

    def __init__(self):
        super().__init__()
        self.board = Board(14, 14)
        self.result = self.NoResult
        self.currentPlayer = self.NoPlayer
        self.moveNumber = 0
        self.currentMove = self.Node('root', [], None)

    class Node:
        """Generic node class. Basic element of a tree."""
        def __init__(self, name, children, parent):
            self.name = name
            self.children = children
            self.parent = parent

        def add(self, node):
            """Adds node to children."""
            self.children.append(node)

        def pop(self):
            """Removes last child from node."""
            self.children.pop()

        def getRoot(self):
            """Backtracks tree and returns root node."""
            if self.parent is None:
                return self
            return self.parent.getRoot()

        def getTree(self):
            """Returns the (sub)tree starting from the current node."""
            tree = [self.name, [child.getTree() for child in self.children]]
            return tree

    def resetMoves(self):
        """Resets current move to root and move number to zero."""
        self.moveNumber = 0
        self.currentMove = self.Node('root', [], None)

    def setResult(self, value):
        """Updates game result, if changed."""
        if self.result == value:
            return
        if self.result == self.NoResult:
            self.result = value
            self.gameOver.emit(self.result)
        else:
            self.result = value

    def setCurrentPlayer(self, value):
        """Updates current player, if changed."""
        if self.currentPlayer == value:
            return
        self.currentPlayer = value
        self.setPlayerQueue(self.currentPlayer)
        self.currentPlayerChanged.emit(self.currentPlayer)

    def setPlayerQueue(self, currentPlayer):
        """Rotates player queue such that the current player is the first in the queue."""
        while self.playerQueue[0] != currentPlayer:
            self.playerQueue.rotate(-1)

    def setBoard(self, board):
        """Updates board, if changed."""
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
        self.resetMoves()

    def getBoardState(self):
        """Gets FEN4 from current board state."""
        fen4 = self.board.getFen4()
        # Append character for current player
        fen4 += self.currentPlayer
        self.fen4Generated.emit(fen4)

    def setBoardState(self, fen4):
        """Sets board according to FEN4."""
        if not fen4:
            return
        self.board.setFen4(fen4)
        self.setCurrentPlayer(fen4.split(' ')[1])

    def treeToAlgebraic(self, tree):
        if tree[0] == 'root':
            newTree = ['root', [self.treeToAlgebraic(subtree) for subtree in tree[1]]]
        else:
            newTree = [self.toAlgebraic(tree[0]), [self.treeToAlgebraic(subtree) for subtree in tree[1]]]
        return newTree

    def toAlgebraic(self, moveString):
        """Converts move string to algebraic notation."""
        moveString = moveString[1:]
        moveString = moveString.split()
        if moveString[0] == 'P':
            moveString.pop(0)
            if len(moveString) == 3:
                moveString[0] = moveString[0][0]
                moveString[1] = 'x'
            else:
                moveString.pop(0)
        elif len(moveString) == 4:
            moveString[2] = 'x'
            moveString.remove(moveString[1])
        else:
            moveString.remove(moveString[1])
        moveString = ''.join(moveString)
        return moveString

    def strMove(self, fromFile, fromRank, toFile, toRank):
        """Returns move in string form, separated by spaces, i.e. '<piece> <from> <captured piece> <to>'."""
        piece: str = self.board.getData(fromFile, fromRank)
        target: str = self.board.getData(toFile, toRank)
        char = (piece + ' ' + chr(97+fromFile) + str(fromRank+1) + ' ' + target*(target != ' ') + ' ' + chr(97+toFile) +
                str(toRank+1))  # chr(97) = 'a'
        return char

    def prevMove(self):
        """Sets board state to previous move."""
        if self.currentMove.name == 'root':
            return
        moveString = self.currentMove.name
        moveString = moveString.split()
        piece = moveString[0]
        fromFile = ord(moveString[1][0]) - 97  # chr(97) = 'a'
        fromRank = int(moveString[1][1:]) - 1
        if len(moveString) == 4:
            target = moveString[2]
            toFile = ord(moveString[3][0]) - 97
            toRank = int(moveString[3][1:]) - 1
        else:
            target = ' '
            toFile = ord(moveString[2][0]) - 97
            toRank = int(moveString[2][1:]) - 1
        self.board.setData(fromFile, fromRank, piece)
        self.board.setData(toFile, toRank, target)
        self.currentMove = self.currentMove.parent
        self.moveNumber -= 1
        self.playerQueue.rotate(1)
        self.setCurrentPlayer(self.playerQueue[0])

    def nextMove(self):
        """Sets board state to next move."""
        if not self.currentMove.children:
            return
        moveString = self.currentMove.children[-1].name  # Take last variation
        moveString = moveString.split()
        piece = moveString[0]
        fromFile = ord(moveString[1][0]) - 97  # chr(97) = 'a'
        fromRank = int(moveString[1][1:]) - 1
        if len(moveString) == 4:
            toFile = ord(moveString[3][0]) - 97
            toRank = int(moveString[3][1:]) - 1
        else:
            toFile = ord(moveString[2][0]) - 97
            toRank = int(moveString[2][1:]) - 1
        self.board.setData(fromFile, fromRank, ' ')
        self.board.setData(toFile, toRank, piece)
        self.currentMove = self.currentMove.children[-1]
        self.moveNumber += 1
        self.playerQueue.rotate(-1)
        self.setCurrentPlayer(self.playerQueue[0])

    def firstMove(self):
        while self.currentMove.name != 'root':
            self.prevMove()

    def lastMove(self):
        while self.currentMove.children:
            self.nextMove()

    def makeMove(self, fromFile, fromRank, toFile, toRank):
        """This method must be overridden to define the proper logic corresponding to the game type (Teams or FFA)."""
        return False


class Teams(Algorithm):
    """A subclass of Algorithm for the 4-player chess Teams variant."""
    def __init__(self):
        super().__init__()

    def makeMove(self, fromFile, fromRank, toFile, toRank):
        """Moves piece from square (fromFile, fromRank) to square (toFile, toRank), if the move is valid."""
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

        # TODO check if move is legal

        # If move already exists (in case of variations), do not change the move tree
        moveString = self.strMove(fromFile, fromRank, toFile, toRank)
        if not (self.currentMove.children and (moveString in (child.name for child in self.currentMove.children))):
            # Make move child of current move and update current move (i.e. previous move is parent of current move)
            move = self.Node(moveString, [], self.currentMove)
            self.currentMove.add(move)
            self.currentMove = move

            # Send signal to update the move list and pass the tree with moves in algebraic notation
            tree = self.treeToAlgebraic(self.currentMove.getRoot().getTree())
            self.moveTreeChanged.emit(tree)
        else:
            # Update current move, but do not change the move tree
            for child in self.currentMove.children:
                if child.name == moveString:
                    self.currentMove = child

        # Increment move number
        self.moveNumber += 1

        # Make the move
        self.board.movePiece(fromFile, fromRank, toFile, toRank)

        # Rotate player queue and get next player from the queue (first element)
        self.playerQueue.rotate(-1)
        self.setCurrentPlayer(self.playerQueue[0])

        return True


class FFA(Algorithm):
    """A subclass of Algorithm for the 4-player chess Free-For-All (FFA) variant."""
    # TODO implement FFA class
    def __init__(self):
        super().__init__()


class View(QWidget):
    """The View is responsible for rendering the current state of the board and signalling user interaction to the
    underlying logic."""
    clicked = pyqtSignal(QPoint)
    squareSizeChanged = pyqtSignal(QSize)

    def __init__(self):
        super().__init__()
        self.squareSize = QSize(50, 50)
        self.board = Board(14, 14)
        self.pieces = {}
        self.highlights = []
        self.playerHighlights = {'r': self.PlayerHighlight(12, 1, QColor('#bf3b43')),
                                 'b': self.PlayerHighlight(1, 1, QColor('#4185bf')),
                                 'y': self.PlayerHighlight(1, 12, QColor('#c09526')),
                                 'g': self.PlayerHighlight(12, 12, QColor('#4e9161'))}

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
        """Adds highlight to the list and redraws view."""
        self.highlights.append(highlight)
        self.update()

    def removeHighlight(self, highlight):
        """Adds highlight to the list and redraws view."""
        self.highlights.remove(highlight)
        self.update()

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
