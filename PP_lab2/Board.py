from Constants import *


class Player:
    """
    Helper enum for the type of the player.
    """
    COMPUTER = 1
    HUMAN = 2


class Board:
    """
    Class Board represents a board for Connect4 game.
    It contains methods for the manipulation of a board.
    """
    def __init__(self):
        """
        Initialization method.
        """
        self._rows = BOARD_SIZE
        self._columns = BOARD_SIZE
        self._board = self.init_board()
        # first move should be done by the player
        self._last_player = Player.COMPUTER

    def init_board(self):
        """
        Initializes a board.
        :return: Empty board
        """
        return [[DEFAULT_VALUE for x in range(self._columns)] for y in range(self._rows)]

    def print_out_board(self):
        """
        Prints out the current state of the board.
        """
        print('\n'.join([''.join(['{:1}'.format(item) for item in row]) for row in self._board]))

    def make_a_move(self, column):
        """
        Represents one move for the Connect4 game.
        :param column: Column to which token will be put
        :return: void
        """
        if column < MIN_COLUMN_SIZE or column > MAX_COLUMN_SIZE:
            raise IndexError('Wrong column index!')

        for row in range(BOARD_SIZE)[::-1]:
            if self._board[row][column] == DEFAULT_VALUE:
                if self._last_player == Player.COMPUTER:
                    self._board[row][column] = HUMAN
                    self._last_player = Player.HUMAN
                else:
                    self._board[row][column] = COMPUTER
                    self._last_player = Player.COMPUTER
                break

    def undo_last_move(self, column):
        """
        Undo the last move of the game from the given column.
        :param column: Column from which the token should be removed
        """
        for row in range(BOARD_SIZE):
            if self._board[row][column] != DEFAULT_VALUE:
                self._board[row][column] = DEFAULT_VALUE
                if self._last_player == Player.COMPUTER:
                    self._last_player = Player.HUMAN
                else:
                    self._last_player = Player.COMPUTER
                break

    @property
    def last_player(self):
        """
        Getter for the last_player property.
        :return: Last player enum
        """
        return self._last_player

    @property
    def board(self):
        """
        Getter for the board property.
        :return: Board as 2D array
        """
        return self._board
