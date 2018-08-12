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

from PyQt5.QtCore import QObject, pyqtSignal

RED, BLUE, YELLOW, GREEN, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = range(10)


class Board(QObject):
    """The Board is the actual chess board and is the data structure shared between the View and the Algorithm."""
    boardReset = pyqtSignal()
    dataChanged = pyqtSignal(int, int)

    def __init__(self, files, ranks):
        super().__init__()
        self.files = files
        self.ranks = ranks
        self.boardData = []
        self.bitboard = []
        self.initBoard()

    def pieceSet(self, color, piece):
        """Gets set of pieces of one type and color."""
        return self.bitboard[color] & self.bitboard[piece]

    def square(self, file, rank):
        """Little-Endian Rank-File (LERF) mapping for 16x16 bitboard (14x14 with "padding" to fit 256 bits)."""
        return (rank + 1) << 4 | (file + 1)

    def flipVertical(self, bitboard):
        """Flips bitboard vertically (parallel prefix approach, 4 delta swaps)."""
        k1 = 0x0000ffff0000ffff0000ffff0000ffff0000ffff0000ffff0000ffff0000ffff
        k2 = 0x00000000ffffffff00000000ffffffff00000000ffffffff00000000ffffffff
        k3 = 0x0000000000000000ffffffffffffffff0000000000000000ffffffffffffffff
        bitboard = ((bitboard >> 16) & k1) | ((bitboard & k1) << 16)
        bitboard = ((bitboard >> 32) & k2) | ((bitboard & k2) << 32)
        bitboard = ((bitboard >> 64) & k3) | ((bitboard & k3) << 64)
        bitboard = (bitboard >> 128) | (bitboard << 128)
        return bitboard

    def flipHorizontal(self, bitboard):
        """Flips bitboard horizontally (parallel prefix approach, 4 delta swaps)."""
        k1 = 0x5555555555555555555555555555555555555555555555555555555555555555
        k2 = 0x3333333333333333333333333333333333333333333333333333333333333333
        k3 = 0x0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f
        k4 = 0x00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff00ff
        bitboard = ((bitboard >> 1) & k1) | ((bitboard & k1) << 1)
        bitboard = ((bitboard >> 2) & k2) | ((bitboard & k2) << 2)
        bitboard = ((bitboard >> 4) & k3) | ((bitboard & k3) << 4)
        bitboard = ((bitboard >> 8) & k4) | ((bitboard & k4) << 8)
        return bitboard

    def flipDiagonal(self, bitboard):
        """Flips bitboard about diagonal from lower left to upper right (parallel prefix approach, 4 delta swaps)."""
        k1 = 0x5555000055550000555500005555000055550000555500005555000055550000
        k2 = 0x3333333300000000333333330000000033333333000000003333333300000000
        k3 = 0x0f0f0f0f0f0f0f0f00000000000000000f0f0f0f0f0f0f0f0000000000000000
        k4 = 0x00ff00ff00ff00ff00ff00ff00ff00ff00000000000000000000000000000000
        t = k4 & (bitboard ^ (bitboard << 120))
        bitboard ^= t ^ (t >> 120)
        t = k3 & (bitboard ^ (bitboard << 60))
        bitboard ^= t ^ (t >> 60)
        t = k2 & (bitboard ^ (bitboard << 30))
        bitboard ^= t ^ (t >> 30)
        t = k1 & (bitboard ^ (bitboard << 15))
        bitboard ^= t ^ (t >> 15)
        return bitboard

    def flipAntiDiagonal(self, bitboard):
        """Flips bitboard about diagonal from upper left to lower right (parallel prefix approach, 4 delta swaps)."""
        k1 = 0xaaaa0000aaaa0000aaaa0000aaaa0000aaaa0000aaaa0000aaaa0000aaaa0000
        k2 = 0xcccccccc00000000cccccccc00000000cccccccc00000000cccccccc00000000
        k3 = 0xf0f0f0f0f0f0f0f00000000000000000f0f0f0f0f0f0f0f00000000000000000
        k4 = 0xff00ff00ff00ff00ff00ff00ff00ff0000ff00ff00ff00ff00ff00ff00ff00ff
        t = bitboard ^ (bitboard << 136)
        bitboard ^= k4 & (t ^ (bitboard >> 136))
        t = k3 & (bitboard ^ (bitboard << 68))
        bitboard ^= t ^ (t >> 68)
        t = k2 & (bitboard ^ (bitboard << 34))
        bitboard ^= t ^ (t >> 34)
        t = k1 & (bitboard ^ (bitboard << 17))
        bitboard ^= t ^ (t >> 17)
        return bitboard

    def rotate(self, bitboard, degrees):
        """Rotates bitboard +90 (clockwise), -90 (counterclockwise) or 180 degrees using two flips."""
        if degrees == 90:
            return self.flipVertical(self.flipDiagonal(bitboard))
        elif degrees == -90:
            return self.flipVertical(self.flipAntiDiagonal(bitboard))
        elif degrees == 180:
            return self.flipHorizontal(self.flipVertical(bitboard))
        else:
            pass

    def printBB(self, bitboard):
        """Prints bitboard in easily readable format (for debugging)."""
        bitstring = ''
        for rank in reversed(range(14)):
            for file in range(14):
                if not ((file < 3 and rank < 3) or (file < 3 and rank > 10) or
                        (file > 10 and rank < 3) or (file > 10 and rank > 10)):
                    bitstring += '1 ' if (bitboard & (1 << self.square(file, rank))) else '. '
                else:
                    bitstring += '  '
            bitstring += '\n'
        print(bitstring)

    def getPieceColor(self, char):
        """Returns piece type and color from two character identifier."""
        if char[0] == 'r':
            color = RED
        elif char[0] == 'b':
            color = BLUE
        elif char[0] == 'y':
            color = YELLOW
        elif char[0] == 'g':
            color = GREEN
        else:
            color = None
        if char[1] == 'P':
            piece = PAWN
        elif char[1] == 'N':
            piece = KNIGHT
        elif char[1] == 'B':
            piece = BISHOP
        elif char[1] == 'R':
            piece = ROOK
        elif char[1] == 'Q':
            piece = QUEEN
        elif char[1] == 'K':
            piece = KING
        else:
            piece = None
        return piece, color

    def initBoard(self):
        """Initializes board with empty squares."""
        self.boardData = [' '] * self.files * self.ranks
        self.bitboard = [0] * 10
        self.boardReset.emit()

    def getData(self, file, rank):
        """Gets board data from square (file, rank)."""
        return self.boardData[file + rank * self.files]

    def setData(self, file, rank, data):
        """Sets board data at square (file, rank) to data."""
        index = file + rank * self.files
        if self.boardData[index] == data:
            return
        self.boardData[index] = data
        self.dataChanged.emit(file, rank)

    def movePiece(self, fromFile, fromRank, toFile, toRank):
        """Moves piece from square (fromFile, fromRank) to square (toFile, toRank)."""
        char = self.getData(fromFile, fromRank)
        captured = self.getData(toFile, toRank)
        self.setData(toFile, toRank, char)
        self.setData(fromFile, fromRank, ' ')
        # Update bitboards
        piece, color = self.getPieceColor(char)
        fromBB = 1 << self.square(fromFile, fromRank)
        toBB = 1 << self.square(toFile, toRank)
        fromToBB = fromBB ^ toBB
        self.bitboard[color] ^= fromToBB
        self.bitboard[piece] ^= fromToBB
        if captured != ' ':
            piece_, color_ = self.getPieceColor(captured)
            self.bitboard[color_] ^= toBB
            self.bitboard[piece_] ^= toBB

    def undoMove(self, fromFile, fromRank, toFile, toRank, char, captured):
        """Takes back move and restores captured piece."""
        self.setData(fromFile, fromRank, char)
        self.setData(toFile, toRank, captured)
        # Update bitboards
        piece, color = self.getPieceColor(char)
        fromBB = 1 << self.square(toFile, toRank)
        toBB = 1 << self.square(fromFile, fromRank)
        fromToBB = fromBB ^ toBB
        self.bitboard[color] ^= fromToBB
        self.bitboard[piece] ^= fromToBB
        if captured != ' ':
            piece_, color_ = self.getPieceColor(captured)
            self.bitboard[color_] ^= fromBB
            self.bitboard[piece_] ^= fromBB

    def parseFen4(self, fen4):
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
                # Set bitboards
                if char != ' ':
                    piece, color = self.getPieceColor(char)
                    self.bitboard[color] |= 1 << self.square(file, rank)
                    self.bitboard[piece] |= 1 << self.square(file, rank)
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
