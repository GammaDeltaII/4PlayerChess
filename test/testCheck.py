import unittest
from gui.board import *


class TestChecksAndCheckmate(unittest.TestCase):
    def setUp(self):
        self.board = Board(14, 14)

    @staticmethod
    def import_test_env(path):
        with open(path, 'r') as f:
            return f.read()

    def testQueenCheck(self):
        self.board.parseFen4(self.import_test_env('../data/testcases/queencheck.pgn4'))
