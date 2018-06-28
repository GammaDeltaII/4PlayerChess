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
        self.setData(toFile, toRank, self.getData(fromFile, fromRank))
        self.setData(fromFile, fromRank, ' ')

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
