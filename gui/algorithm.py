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

from PyQt5.QtCore import QObject, pyqtSignal, QSettings
from PyQt5.QtGui import QColor
from collections import deque
from datetime import datetime
from re import split
from gui.board import Board
from gui.settings import Settings

# Load settings
COM = '4pc'
APP = '4PlayerChess'
SETTINGS = Settings()


class Algorithm(QObject):
    """The Algorithm is the underlying logic responsible for changing the current state of the board."""
    boardChanged = pyqtSignal(Board)
    gameOver = pyqtSignal(str)
    currentPlayerChanged = pyqtSignal(str)
    newGameCreated = pyqtSignal()
    fen4Generated = pyqtSignal(str)
    pgn4Generated = pyqtSignal(str)
    moveTextChanged = pyqtSignal(str)
    selectMove = pyqtSignal(tuple)
    removeMoveSelection = pyqtSignal()
    removeHighlight = pyqtSignal(QColor)
    addHighlight = pyqtSignal(int, int, int, int, QColor)
    playerNamesChanged = pyqtSignal(str, str, str, str)
    playerRatingChanged = pyqtSignal(str, str, str, str)
    cannotReadPgn4 = pyqtSignal()

    NoResult, Team1Wins, Team2Wins, Draw = ['*', '1-0', '0-1', '1/2-1/2']  # Results
    NoPlayer, Red, Blue, Yellow, Green = ['?', 'r', 'b', 'y', 'g']  # Players
    playerQueue = deque([Red, Blue, Yellow, Green])

    startFen4 = '3yRyNyByKyQyByNyR3/3yPyPyPyPyPyPyPyP3/14/bRbP10gPgR/bNbP10gPgN/bBbP10gPgB/bKbP10gPgQ/' \
                'bQbP10gPgK/bBbP10gPgB/bNbP10gPgN/bRbP10gPgR/14/3rPrPrPrPrPrPrPrP3/3rRrNrBrQrKrBrNrR3 ' \
                'r rKrQbKbQyKyQgKgQ - 0 1'

    # chess.com: [player to move] - [dead 1/0] - [kingside castle 1/0] - [queenside castle 1/0] - [points] - [ply] -
    chesscomStartFen4 = 'R-0,0,0,0-1,1,1,1-1,1,1,1-0,0,0,0-0-3,yR,yN,yB,yK,yQ,yB,yN,yR,3/3,yP,yP,yP,yP,yP,yP,yP,yP,3/' \
                        '14/bR,bP,10,gP,gR/bN,bP,10,gP,gN/bB,bP,10,gP,gB/bK,bP,10,gP,gQ/bQ,bP,10,gP,gK/bB,bP,10,gP,gB/'\
                        'bN,bP,10,gP,gN/bR,bP,10,gP,gR/14/3,rP,rP,rP,rP,rP,rP,rP,rP,3/3,rR,rN,rB,rQ,rK,rB,rN,rR,3'

    def __init__(self):
        super().__init__()
        self.variant = '?'
        self.board = Board(14, 14)
        self.result = self.NoResult
        self.currentPlayer = self.NoPlayer
        self.moveNumber = 0
        self.currentMove = self.Node('root', [], None)
        self.currentMove.fen4 = self.startFen4
        self.redName = self.NoPlayer
        self.blueName = self.NoPlayer
        self.yellowName = self.NoPlayer
        self.greenName = self.NoPlayer
        self.redRating = '?'
        self.blueRating = '?'
        self.yellowRating = '?'
        self.greenRating = '?'
        self.chesscomMoveText = ''
        self.moveText = ''
        self.moveDict = dict()
        self.inverseMoveDict = dict()
        self.index = 0  # Used by getMoveText() method
        self.fenMoveNumber = 1

    class Node:
        """Generic node class. Basic element of a tree."""
        def __init__(self, name, children, parent):
            self.name = name
            self.children = children
            self.parent = parent
            self.fen4 = None
            self.comment = None

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

        def pathFromRoot(self, actions=None):
            """Returns a list of nextMove() actions to reach the current node from the root."""
            if not actions:
                actions = []
            if self.parent is None:
                return actions
            else:
                var = self.parent.children.index(self)
                actions.insert(0, 'nextMove(' + str(var) + ')')
            return self.parent.pathFromRoot(actions)

        def getMoveNumber(self):
            """Returns the move number in the format (ply, variation, move). NOTE: does NOT support subvariations."""
            varNum = [int(a.strip('nextMove()')) for a in self.pathFromRoot()]
            ply, var, move = (0, 0, 0)
            plyCount = True
            i = 0
            while i < len(varNum):
                if varNum[i] != 0:
                    var = varNum[i]
                    plyCount = False
                else:
                    if plyCount:
                        ply += 1
                    else:
                        move += 1
                i += 1
            return str(ply + 1) + '-' + str(var) + '-' + str(move + 1) if var != 0 else str(ply)

    def updatePlayerNames(self, red, blue, yellow, green):
        """Sets player names to names entered in the player name labels."""
        self.redName = red if not (red == 'Player Name' or red == '') else '?'
        self.blueName = blue if not (blue == 'Player Name' or blue == '') else '?'
        self.yellowName = yellow if not (yellow == 'Player Name' or yellow == '') else '?'
        self.greenName = green if not (green == 'Player Name' or green == '') else '?'
        self.getPgn4()  # Update PGN4

    def updatePlayerRating(self, red, blue, yellow, green):
        """Sets player rating to rating entered in the player name labels."""
        self.redRating = red
        self.blueRating = blue
        self.yellowRating = yellow
        self.greenRating = green

    def setResult(self, value):
        """Updates game result, if changed."""
        if self.result == value:
            return
        if self.result == self.NoResult:
            self.result = value
            self.gameOver.emit(self.result)
        else:
            self.result = value
        self.getPgn4()  # Update PGN4

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
        if SETTINGS.checkSetting('chesscom'):
            fen4 = self.chesscomStartFen4
        else:
            fen4 = self.startFen4
        self.setBoardState(fen4)
        self.fen4Generated.emit(fen4)

    def getFen4(self, emitSignal=True):
        """Gets FEN4 from current board state."""
        if SETTINGS.checkSetting('chesscom'):
            chesscomPrefix = self.currentPlayer.upper() + '-0,0,0,0' + \
                             self.toChesscomCastling(self.board.castlingAvailability()) + '-0,0,0,0-' + \
                             str(self.moveNumber) + '-'
            fen4 = chesscomPrefix + self.board.getChesscomFen4()
        else:
            fen4 = self.board.getFen4()
            # Append character for current player
            fen4 += self.currentPlayer + ' '
            fen4 += self.board.castlingAvailability() + ' '
            fen4 += '- '  # En passant target square, n/a
            fen4 += str(self.moveNumber) + ' '  # Number of quarter-moves
            fen4 += str(self.moveNumber // 4 + 1)  # Number of full moves, starting from 1
        if emitSignal:
            self.fen4Generated.emit(fen4)
        return fen4

    def toChesscomCastling(self, castling):
        """Converts castling availability string to chess.com compatible format."""
        s = '-'
        s += '1,' if 'rK' in castling else '0,'
        s += '1,' if 'bK' in castling else '0,'
        s += '1,' if 'yK' in castling else '0,'
        s += '1' if 'gK' in castling else '0'
        s += '-'
        s += '1,' if 'rQ' in castling else '0,'
        s += '1,' if 'bQ' in castling else '0,'
        s += '1,' if 'yQ' in castling else '0,'
        s += '1' if 'gQ' in castling else '0'
        return s

    def setCastlingAvailability(self, fen4):
        """Sets castling availability according to FEN4."""
        castling = fen4.split(' ')[2]
        RED, BLUE, YELLOW, GREEN = range(4)
        QUEENSIDE, KINGSIDE = (0, 1)
        self.board.castle[RED][KINGSIDE] = (1 << self.square(10, 0)) if 'rK' in castling else 0
        self.board.castle[RED][QUEENSIDE] = (1 << self.square(3, 0)) if 'rQ' in castling else 0
        self.board.castle[BLUE][KINGSIDE] = (1 << self.square(0, 10)) if 'bK' in castling else 0
        self.board.castle[BLUE][QUEENSIDE] = (1 << self.square(0, 3)) if 'bQ' in castling else 0
        self.board.castle[YELLOW][KINGSIDE] = (1 << self.square(3, 13)) if 'yK' in castling else 0
        self.board.castle[YELLOW][QUEENSIDE] = (1 << self.square(10, 13)) if 'yQ' in castling else 0
        self.board.castle[GREEN][KINGSIDE] = (1 << self.square(13, 3)) if 'gK' in castling else 0
        self.board.castle[GREEN][QUEENSIDE] = (1 << self.square(13, 10)) if 'gQ' in castling else 0

    def setBoardState(self, fen4):
        """Sets board according to FEN4."""
        if not fen4:
            return
        # if self.getFen4(False) == fen4:  # Do not emit fen4Generated signal
        #     return
        self.newGameCreated.emit()
        self.setupBoard()
        self.board.parseFen4(fen4)
        self.setResult(self.NoResult)
        if SETTINGS.checkSetting('chesscom'):
            self.setCurrentPlayer(fen4[0].lower())
            self.moveNumber = 0
            self.fenMoveNumber = 1
        else:
            self.setCurrentPlayer(fen4.split(' ')[1])
            self.moveNumber = int(fen4.split(' ')[-2])
            self.fenMoveNumber = int(fen4.split(' ')[-2]) + 1
        self.currentMove = self.Node('root', [], None)
        self.currentMove.fen4 = fen4
        self.chesscomMoveText = ''
        self.moveText = ''
        self.moveDict.clear()
        self.getPgn4()  # Update PGN4

    def toChesscomMove(self, moveString):
        """Converts move string to chess.com move notation."""
        moveString = moveString.split()
        if moveString[0][1] == 'P':
            moveString.pop(0)
            if len(moveString) == 3:
                piece = moveString[1][1]
                if piece != 'P':
                    moveString[1] = 'x' + piece
                else:
                    moveString[1] = 'x'
            else:
                moveString.insert(1, '-')
        elif len(moveString) == 4:
            # Castling move
            shortCastle = ['rK h1 rR k1', 'bK a8 bR a11', 'yK g14 yR d14', 'gK n7 gR n4']
            longCastle = ['rK h1 rR d1', 'bK a8 bR a4', 'yK g14 yR k14', 'gK n7 gR n11']
            if ' '.join(moveString) in shortCastle:
                moveString = 'O-O'
            elif ' '.join(moveString) in longCastle:
                moveString = 'O-O-O'
            else:
                moveString[0] = moveString[0][1]
                piece = moveString[2][1]
                if piece != 'P':
                    moveString[2] = 'x' + piece
                else:
                    moveString[2] = 'x'
        else:
            if moveString != 'O-O' and moveString != 'O-O-O':
                # castling moves by castling square
                shortCastle = ['rK h1 j1', 'bK a8 a10', 'yK g14 e14', 'gK n7 n5']
                longCastle = ['rK h1 f1', 'bK a8 a6', 'yK g14 i14', 'gK n7 n9']
                if ' '.join(moveString) in shortCastle:
                    moveString = 'O-O'
                elif ' '.join(moveString) in longCastle:
                    moveString = 'O-O-O'
                else:
                    moveString[0] = moveString[0][1]
                    moveString.insert(2, '-')
        moveString = ''.join(moveString)
        return moveString

    def fromChesscomMove(self, move, player):
        """Returns fromFile, fromRank, toFile, toRank from chess.com move."""
        if move == 'O-O':
            if player == self.Red:
                fromFile, fromRank, toFile, toRank = (7, 0, 10, 0)
            elif player == self.Blue:
                fromFile, fromRank, toFile, toRank = (0, 7, 0, 10)
            elif player == self.Yellow:
                fromFile, fromRank, toFile, toRank = (6, 13, 3, 13)
            elif player == self.Green:
                fromFile, fromRank, toFile, toRank = (13, 6, 13, 3)
            else:
                fromFile, fromRank, toFile, toRank = [None] * 4
        elif move == 'O-O-O':
            if player == self.Red:
                fromFile, fromRank, toFile, toRank = (7, 0, 3, 0)
            elif player == self.Blue:
                fromFile, fromRank, toFile, toRank = (0, 7, 0, 3)
            elif player == self.Yellow:
                fromFile, fromRank, toFile, toRank = (6, 13, 10, 13)
            elif player == self.Green:
                fromFile, fromRank, toFile, toRank = (13, 6, 13, 10)
            else:
                fromFile, fromRank, toFile, toRank = [None] * 4
        else:
            for c in reversed(move):
                if c.isupper():
                    move = move.replace(c, '')
            move = move.replace('x', '')
            move = move.replace('-', '')
            move = move.replace('+', '')
            move = move.replace('#', '')
            prev = ''
            i = 0
            for char in move:
                if (not char.isdigit()) and prev.isdigit():
                    move = [move[:i], move[i:]]
                    break
                prev = char
                i += 1
            fromFile = ord(move[0][0]) - 97
            fromRank = int(move[0][1:]) - 1
            toFile = ord(move[1][0]) - 97
            toRank = int(move[1][1:]) - 1
        return fromFile, fromRank, toFile, toRank

    def toAlgebraic(self, moveString):
        """Converts move string to algebraic notation."""
        moveString = moveString.split()
        if moveString[0][1] == 'P':
            moveString.pop(0)
            if len(moveString) == 3:
                moveString[1] = 'x'
        elif len(moveString) == 4:
            # Castling move
            shortCastle = ['rK h1 rR k1', 'bK a8 bR a11', 'yK g14 yR d14', 'gK n7 gR n4']
            longCastle = ['rK h1 rR d1', 'bK a8 bR a4', 'yK g14 yR k14', 'gK n7 gR n11']
            if ' '.join(moveString) in shortCastle:
                moveString = 'O-O'
            elif ' '.join(moveString) in longCastle:
                moveString = 'O-O-O'
            else:
                moveString[0] = moveString[0][1]
                moveString[2] = 'x'
        else:
            if moveString != 'O-O' and moveString != 'O-O-O':
                shortCastle = ['rK h1 j1', 'bK a8 a10', 'yK g14 e14', 'gK n7 n5']
                longCastle = ['rK h1 f1', 'bK a8 a6', 'yK g14 i14', 'gK n7 n9']
                if ' '.join(moveString) in shortCastle:
                    moveString = 'O-O'
                elif ' '.join(moveString) in longCastle:
                    moveString = 'O-O-O'
                else:
                    moveString[0] = moveString[0][1]
        moveString = ''.join(moveString)
        return moveString

    def fromAlgebraic(self, move, player):
        """Returns fromFile, fromRank, toFile, toRank from algebraic move."""
        if move == 'O-O':
            if player == self.Red:
                fromFile, fromRank, toFile, toRank = (7, 0, 10, 0)
            elif player == self.Blue:
                fromFile, fromRank, toFile, toRank = (0, 7, 0, 10)
            elif player == self.Yellow:
                fromFile, fromRank, toFile, toRank = (6, 13, 3, 13)
            elif player == self.Green:
                fromFile, fromRank, toFile, toRank = (13, 6, 13, 3)
            else:
                fromFile, fromRank, toFile, toRank = [None] * 4
        elif move == 'O-O-O':
            if player == self.Red:
                fromFile, fromRank, toFile, toRank = (7, 0, 3, 0)
            elif player == self.Blue:
                fromFile, fromRank, toFile, toRank = (0, 7, 0, 3)
            elif player == self.Yellow:
                fromFile, fromRank, toFile, toRank = (6, 13, 10, 13)
            elif player == self.Green:
                fromFile, fromRank, toFile, toRank = (13, 6, 13, 10)
            else:
                fromFile, fromRank, toFile, toRank = [None] * 4
        else:
            if move[0].isupper():
                move = move[1:]
            move = move.replace('x', '')
            prev = ''
            i = 0
            for char in move:
                if (not char.isdigit()) and prev.isdigit():
                    move = [move[:i], move[i:]]
                    break
                prev = char
                i += 1
            fromFile = ord(move[0][0]) - 97
            fromRank = int(move[0][1:]) - 1
            toFile = ord(move[1][0]) - 97
            toRank = int(move[1][1:]) - 1
        return fromFile, fromRank, toFile, toRank

    def strMove(self, fromFile, fromRank, toFile, toRank):
        """Returns move in string form, separated by spaces, i.e. '<piece> <from> <captured piece> <to>'."""
        piece: str = self.board.getData(fromFile, fromRank)
        captured: str = self.board.getData(toFile, toRank)
        char = (piece + ' ' + chr(97 + fromFile) + str(fromRank + 1) + ' ' + captured * (captured != ' ') + ' ' +
                chr(97 + toFile) + str(toRank + 1))  # chr(97) = 'a'
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
            captured = moveString[2]
            toFile = ord(moveString[3][0]) - 97
            toRank = int(moveString[3][1:]) - 1
        else:
            captured = ' '
            toFile = ord(moveString[2][0]) - 97
            toRank = int(moveString[2][1:]) - 1
        self.board.undoMove(fromFile, fromRank, toFile, toRank, piece, captured)
        self.currentMove = self.currentMove.parent
        self.moveNumber -= 1
        self.playerQueue.rotate(1)
        self.setCurrentPlayer(self.playerQueue[0])
        # Signal View to remove last move highlight
        if self.currentPlayer == self.Red:
            color = QColor('#33bf3b43')
        elif self.currentPlayer == self.Blue:
            color = QColor('#334185bf')
        elif self.currentPlayer == self.Yellow:
            color = QColor('#33c09526')
        elif self.currentPlayer == self.Green:
            color = QColor('#334e9161')
        else:
            color = QColor('#00000000')
        self.removeHighlight.emit(color)
        if not self.currentMove.name == 'root':
            key = self.inverseMoveDict[self.currentMove]
            self.selectMove.emit(key)
        else:
            self.removeMoveSelection.emit()
        self.getFen4()  # Update FEN4
        self.getPgn4()  # Update PGN4

    def nextMove(self, var=0):
        """Sets board state to next move. Follows main variation by default (var=0)."""
        if not self.currentMove.children:
            return
        moveString = self.currentMove.children[var].name
        moveString = moveString.split()
        fromFile = ord(moveString[1][0]) - 97  # chr(97) = 'a'
        fromRank = int(moveString[1][1:]) - 1
        if len(moveString) == 4:
            toFile = ord(moveString[3][0]) - 97
            toRank = int(moveString[3][1:]) - 1
        else:
            toFile = ord(moveString[2][0]) - 97
            toRank = int(moveString[2][1:]) - 1
        self.board.makeMove(fromFile, fromRank, toFile, toRank)
        self.currentMove = self.currentMove.children[var]
        self.moveNumber += 1
        # Signal View to add move highlight and remove highlights of next player
        if self.currentPlayer == self.Red:
            color = QColor('#33bf3b43')
        elif self.currentPlayer == self.Blue:
            color = QColor('#334185bf')
        elif self.currentPlayer == self.Yellow:
            color = QColor('#33c09526')
        elif self.currentPlayer == self.Green:
            color = QColor('#334e9161')
        else:
            color = QColor('#00000000')
        self.addHighlight.emit(fromFile, fromRank, toFile, toRank, color)
        self.playerQueue.rotate(-1)
        self.setCurrentPlayer(self.playerQueue[0])
        if self.currentPlayer == self.Red:
            color = QColor('#33bf3b43')
        elif self.currentPlayer == self.Blue:
            color = QColor('#334185bf')
        elif self.currentPlayer == self.Yellow:
            color = QColor('#33c09526')
        elif self.currentPlayer == self.Green:
            color = QColor('#334e9161')
        else:
            color = QColor('#00000000')
        self.removeHighlight.emit(color)
        key = self.inverseMoveDict[self.currentMove]
        self.selectMove.emit(key)
        self.getFen4()  # Update FEN4
        self.getPgn4()  # Update PGN4

    def firstMove(self):
        """Sets board state to first move."""
        while self.currentMove.name != 'root':
            self.prevMove()

    def lastMove(self):
        """Sets board state to last move."""
        self.firstMove()
        while self.currentMove.children:
            self.nextMove()

    def makeMove(self, fromFile, fromRank, toFile, toRank):
        """This method must be implemented to define the proper logic corresponding to the game type (Teams or FFA)."""
        return False

    def getPgn4(self):
        """Generates PGN4 from current game."""
        pgn4 = ''

        # Tags: "?" if data unknown, "-" if not applicable
        pgn4 += '[Variant "' + self.variant + '"]\n'
        pgn4 += '[Site "www.chess.com/4-player-chess"]\n'
        pgn4 += '[Date "' + datetime.utcnow().strftime('%a %b %d %Y %H:%M:%S (UTC)') + '"]\n'
        # pgn4 += '[Event "-"]\n'
        # pgn4 += '[Round "-"]\n'
        pgn4 += '[Red "' + self.redName + '"]\n' if not self.redName == '?' else ''
        pgn4 += '[RedElo "' + self.redRating + '"]\n' if not self.redRating == '?' else ''
        pgn4 += '[Blue "' + self.blueName + '"]\n' if not self.blueName == '?' else ''
        pgn4 += '[BlueElo "' + self.blueRating + '"]\n' if not self.blueRating == '?' else ''
        pgn4 += '[Yellow "' + self.yellowName + '"]\n' if not self.yellowName == '?' else ''
        pgn4 += '[YellowElo "' + self.yellowRating + '"]\n' if not self.yellowRating == '?' else ''
        pgn4 += '[Green "' + self.greenName + '"]\n' if not self.greenName == '?' else ''
        pgn4 += '[GreenElo "' + self.greenRating + '"]\n' if not self.greenRating == '?' else ''
        # pgn4 += '[Result "' + self.result + '"]\n'  # 1-0 (r & y win), 0-1 (b & g win), 1/2-1/2 (draw), * (no result)
        # pgn4 += '[Mode "ICS"]\n'  # ICS = Internet Chess Server, OTB = Over-The-Board
        pgn4 += '[TimeControl "G/1 d15"]\n'  # 1-minute game with 15 seconds delay per move
        pgn4 += '[PlyCount "' + str(self.moveNumber) + '"]\n'  # Total number of quarter-moves
        startFen4 = self.currentMove.getRoot().fen4
        if SETTINGS.checkSetting('chesscom'):
            if startFen4 != self.chesscomStartFen4:
                pgn4 += '[SetUp "1"]\n'
                pgn4 += '[StartFen4 "' + startFen4 + '"]\n'
        else:
            if startFen4 != self.startFen4:
                pgn4 += '[SetUp "1"]\n'
                pgn4 += '[StartFen4 "' + startFen4 + '"]\n'
        pgn4 += '[CurrentMove "' + self.currentMove.getMoveNumber() + '"]\n'
        pgn4 += '[CurrentPosition "' + self.getFen4() + '"]\n\n'

        # Movetext
        if SETTINGS.checkSetting('chesscom'):
            pgn4 = pgn4[:-1]  # remove newline
            pgn4 += self.chesscomMoveText
        else:
            pgn4 += self.moveText

            # Append result
            pgn4 += self.result

        self.pgn4Generated.emit(pgn4)

    def updateMoveText(self):
        """Updates movetext and dictionary."""
        self.chesscomMoveText = ''
        self.moveText = ''
        self.moveDict.clear()
        self.index = 0
        self.getMoveText(self.currentMove.getRoot(), self.fenMoveNumber)
        self.inverseMoveDict = {value: key for key, value in self.moveDict.items()}
        self.moveTextChanged.emit(self.moveText)
        if self.currentMove.name != 'root':
            key = self.inverseMoveDict[self.currentMove]
            self.selectMove.emit(key)

    def getMoveText(self, node, move=1, var=0):
        """Traverses move tree to generate movetext and updates move dictionary to keep track of the nodes associated
        with the movetext."""
        if node.children:
            main = node.children[0]
            if len(node.children) > 1:
                variations = node.children[1:]
            else:
                variations = None
        else:
            main = None
            variations = None
        # If different FEN4 starting position used, insert move number if needed
        if node.name == 'root' and move != 1 and (move - 1) % 4:
            token = str((move - 1) // 4 + 1) + '.'
            self.chesscomMoveText += token
            self.moveText += token + ' '
            self.moveDict[(self.index, token)] = None
            self.index += 1
            token = '.' * ((move - 1) % 4)
            if token:
                self.moveText += token
                self.moveDict[(self.index, token)] = None
                self.index += 1
            if (move - 1) % 4:
                self.chesscomMoveText += ' '
                self.moveText += ' '
        # Main move has variations
        if main and variations:
            if not (move - 1) % 4:
                token = str(move // 4 + 1) + '.'
                self.chesscomMoveText += '\n' + token + ' '
                self.moveText += token + ' '
                self.moveDict[(self.index, token)] = None
                self.index += 1
            else:
                self.chesscomMoveText += '.. '
            # Add main move to movetext before expanding variations, but do not expand main move yet
            chesscomToken = self.toChesscomMove(main.name)
            self.chesscomMoveText += chesscomToken + ' '
            token = self.toAlgebraic(main.name)
            self.moveText += token + ' '
            self.moveDict[(self.index, token)] = main
            self.index += 1
            if main.comment:
                self.chesscomMoveText += '{ ' + main.comment + ' } '
                self.moveText += '{ ' + main.comment + ' } '
            # Expand variations
            for variation in variations:
                if self.moveText[-2] == ')':
                    self.index += 1
                token = '('
                self.chesscomMoveText += token + ' '
                self.moveText += token + ' '
                self.moveDict[(self.index, token)] = None
                self.index += 1
                token = str(move // 4 + 1)
                self.chesscomMoveText += token
                self.moveText += token + ' '
                self.moveDict[(self.index, token)] = None
                self.index += 1
                token = '.' * ((move - 1) % 4)
                if token:
                    self.moveText += token
                    self.moveDict[(self.index, token)] = None
                    self.index += 1
                if (move - 1) % 4:
                    self.chesscomMoveText += '.. '
                    self.moveText += ' '
                else:
                    self.chesscomMoveText += '. '
                chesscomToken = self.toChesscomMove(variation.name)
                self.chesscomMoveText += chesscomToken + ' '
                token = self.toAlgebraic(variation.name)
                self.moveText += token + ' '
                self.moveDict[(self.index, token)] = variation
                self.index += 1
                if variation.comment:
                    self.chesscomMoveText += '{ ' + variation.comment + ' } '
                    self.moveText += '{ ' + variation.comment + ' } '
                self.getMoveText(variation, move + 1, var + 1)
            # Expand main move
            self.index += 1
            self.getMoveText(main, move + 1, var)
        # Main move has no variations
        elif main and not variations:
            if not (move - 1) % 4:
                token = str(move // 4 + 1) + '.'
                self.chesscomMoveText += '\n' + token + ' '
                self.moveText += token + ' '
                self.moveDict[(self.index, token)] = None
                self.index += 1
            else:
                self.chesscomMoveText += '.. '
            chesscomToken = self.toChesscomMove(main.name)
            self.chesscomMoveText += chesscomToken + ' '
            token = self.toAlgebraic(main.name)
            self.moveText += token + ' '
            self.moveDict[(self.index, token)] = main
            self.index += 1
            if main.comment:
                self.chesscomMoveText += '{ ' + main.comment + ' } '
                self.moveText += '{ ' + main.comment + ' } '
            self.getMoveText(main, move + 1, var)
        # Node is leaf node (i.e. end of variation or main line)
        else:
            if var != 0:
                token = ')'
                self.chesscomMoveText += token + ' '
                self.moveText += token + ' '
                self.moveDict[(self.index, token)] = None

    def split_(self, movetext):
        """Splits movetext into tokens."""
        x = split('\s+(?={)|(?<=})\s+', movetext)  # regex: one or more spaces followed by { or preceded by }
        movetext = []
        for y in x:
            if y:
                if y[0] != '{':
                    for z in y.split():
                        movetext.append(z)
                else:
                    movetext.append(y)
        return movetext

    def parseChesscomPgn4(self, pgn4):
        """Parses chess.com PGN4 and sets game state accordingly."""
        startPosition = None
        currentMove = None
        lines = pgn4.split('\n')
        movetext = ''
        for line in lines:
            if line == '':
                continue
            elif line[0] == '[' and line[-1] == ']':
                tag = line.strip('[]').split('"')[:-1]
                tag[0] = tag[0].strip()
                if tag[0] == 'Variant' and tag[1] == 'FFA':
                    self.cannotReadPgn4.emit()
                    return False
                elif tag[0] == 'Red':
                    self.redName = tag[1]
                elif tag[0] == 'RedElo':
                    self.redRating = tag[1]
                elif tag[0] == 'Blue':
                    self.blueName = tag[1]
                elif tag[0] == 'BlueElo':
                    self.blueRating = tag[1]
                elif tag[0] == 'Yellow':
                    self.yellowName = tag[1]
                elif tag[0] == 'YellowElo':
                    self.yellowRating = tag[1]
                elif tag[0] == 'Green':
                    self.greenName = tag[1]
                elif tag[0] == 'GreenElo':
                    self.greenRating = tag[1]
                elif tag[0] == 'Result':
                    self.result = tag[1]
                elif tag[0] == 'StartFen4':
                    startPosition = tag[1]
                elif tag[0] == 'CurrentMove':
                    currentMove = tag[1]
                else:
                    # Irrelevant tags
                    pass
            else:
                if not currentMove:
                    self.cannotReadPgn4.emit()
                    return False
                movetext += line + ' '
        # Generate game from movetext
        self.newGame()
        tokens = self.split_(movetext)
        for token in tokens:
            if token[0] == '(' and len(token) > 1:
                index = tokens.index(token)
                tokens.insert(index + 1, token[1:])
                tokens[index] = token[0]
        roots = []
        prev = None
        i = 0
        for token in tokens:
            try:
                next_ = tokens[i + 1]
            except IndexError:
                next_ = None
            if (token[0].isdigit() and token[-1] == '.') or token in '..RT#':
                pass
            elif token[0] == '{':
                # Comment
                self.currentMove.comment = token[1:-1].strip()
            elif token == '(':
                # Next move is variation
                if not prev == ')':
                    self.prevMove()
                    roots.append(self.currentMove)
                else:
                    roots.append(self.currentMove)
            elif token == ')':
                # End of variation
                root = roots.pop()
                while self.currentMove.name != root.name:
                    self.prevMove()
                if next_ != '(':
                    # Continue with previous line
                    self.nextMove()
            else:
                fromFile, fromRank, toFile, toRank = self.fromChesscomMove(token, self.currentPlayer)
                self.makeMove(fromFile, fromRank, toFile, toRank)
            prev = token
            i += 1
        # Set game position to CurrentMove ("ply-variation-move")
        self.firstMove()
        currentMove = [int(c) for c in currentMove.split('-')]
        if len(currentMove) == 1:
            ply = currentMove[0]
            for _ in range(ply):
                self.nextMove()
        else:
            ply, variation, move = currentMove
            for _ in range(ply - 1):
                self.nextMove()
            self.nextMove(variation)
            for _ in range(move - 1):
                self.nextMove()
        # Emit signal to update player names and rating
        self.playerNamesChanged.emit(self.redName, self.blueName, self.yellowName, self.greenName)
        self.playerRatingChanged.emit(self.redRating, self.blueRating, self.yellowRating, self.greenRating)
        return True

    def parsePgn4(self, pgn4):
        """Parses PGN4 and sets game state accordingly."""
        currentPosition = None
        lines = pgn4.split('\n')
        for line in lines:
            if line == '':
                continue
            elif line[0] == '[' and line[-1] == ']':
                tag = line.strip('[]').split('"')[:-1]
                tag[0] = tag[0].strip()
                if tag[0] == 'Variant' and tag[1] == 'FFA':
                    self.cannotReadPgn4.emit()
                    return False
                elif tag[0] == 'Red':
                    self.redName = tag[1]
                elif tag[0] == 'Blue':
                    self.blueName = tag[1]
                elif tag[0] == 'Yellow':
                    self.yellowName = tag[1]
                elif tag[0] == 'Green':
                    self.greenName = tag[1]
                elif tag[0] == 'Result':
                    self.result = tag[1]
                elif tag[0] == 'CurrentPosition':
                    currentPosition = tag[1]
                else:
                    # Irrelevant tags
                    pass
            else:
                if not currentPosition:
                    self.cannotReadPgn4.emit()
                    return False
                # Generate game from movetext
                self.newGame()
                line = line.replace(' *', '')
                line = line.replace(' 1-0', '')
                line = line.replace(' 0-1', '')
                line = line.replace(' 1/2-1/2', '')
                if line == '*':
                    # No movetext to process
                    break
                roots = []
                tokens = self.split_(line)
                prev = None
                i = 0
                for token in tokens:
                    try:
                        next_ = tokens[i + 1]
                    except IndexError:
                        next_ = None
                    if token[0].isdigit() or token[0] == '.':
                        pass
                    elif token[0] == '{':
                        # Comment
                        self.currentMove.comment = token[1:-1].strip()
                    elif token == '(':
                        # Next move is variation
                        if not prev == ')':
                            self.prevMove()
                            roots.append(self.currentMove)
                        else:
                            roots.append(self.currentMove)
                    elif token == ')':
                        # End of variation
                        root = roots.pop()
                        while self.currentMove.name != root.name:
                            self.prevMove()
                        if next_ != '(':
                            # Continue with previous line
                            self.nextMove()
                    else:
                        fromFile, fromRank, toFile, toRank = self.fromAlgebraic(token, self.currentPlayer)
                        self.makeMove(fromFile, fromRank, toFile, toRank)
                    prev = token
                    i += 1
        # Set game position to FEN4
        self.firstMove()
        node = None
        for node in self.traverse(self.currentMove, self.currentMove.children):
            if node.fen4 == currentPosition:
                break
        if node:
            actions = node.pathFromRoot()
            for action in actions:
                exec('self.' + action)
        # Emit signal to update player names
        self.playerNamesChanged.emit(self.redName, self.blueName, self.yellowName, self.greenName)
        return True

    def traverse(self, tree, children):
        """Traverses nodes of tree in breadth-first order."""
        yield tree
        last = tree
        for node in self.traverse(tree, children):
            for child in node.children:
                yield child
                last = child
            if last == node:
                return


class Teams(Algorithm):
    """A subclass of Algorithm for the 4-player chess Teams variant."""
    def __init__(self):
        super().__init__()
        self.variant = 'Teams'

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

        color = ['r', 'b', 'y', 'g'].index(fromData[0])
        piece = ['P', 'N', 'B', 'R', 'Q', 'K'].index(fromData[1]) + 4
        origin = self.board.square(fromFile, fromRank)
        target = self.board.square(toFile, toRank)

        if not (1 << target) & self.board.legalMoves(piece, origin, color):
            return False

        # Check if move already exists
        moveString = self.strMove(fromFile, fromRank, toFile, toRank)
        if not (self.currentMove.children and (moveString in (child.name for child in self.currentMove.children))):
            # Make move child of current move and update current move (i.e. previous move is parent of current move)
            move = self.Node(moveString, [], self.currentMove)
            self.currentMove.add(move)
            self.currentMove = move
            # Update movetext and move dictionary and select current move in move list
            self.updateMoveText()
        else:
            # Move already exists. Update current move, but do not change the move tree
            for child in self.currentMove.children:
                if child.name == moveString:
                    self.currentMove = child
                    self.updateMoveText()  # Make current move selected in move list

        # Make the move
        self.board.makeMove(fromFile, fromRank, toFile, toRank)

        # Increment move number
        self.moveNumber += 1

        # Rotate player queue and get next player from the queue (first element)
        self.playerQueue.rotate(-1)
        self.setCurrentPlayer(self.playerQueue[0])

        # Update FEN4 and PGN4
        fen4 = self.getFen4()
        self.getPgn4()

        # Store FEN4 in current node
        self.currentMove.fen4 = fen4

        #################
        # TODO grayout player that got checkmated
        self.board.canPreventCheckmate = [False]*4
        for color in range(4):
            if self.board.kingInCheckmate(color, self.currentPlayer):
                color_name = ['red', 'blue', 'yellow', 'green']
                print(f'{color_name[color]} lost!')
        #################

        return True


class FFA(Algorithm):
    """A subclass of Algorithm for the 4-player chess Free-For-All (FFA) variant."""
    # TODO implement FFA class
    def __init__(self):
        super().__init__()
        self.variant = 'Free-For-All'
