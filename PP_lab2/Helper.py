from Constants import *
from Board import Player


class MasterMessage:
    """
    Class MasterMessage represents a message which is sent from the master to the workers.
    """
    def __init__(self, board, column, column2, depth):
        """
        Initialization method.
        :param board: a game board
        :param column: Move from the pc
        :param column2: Move from the player
        :param depth: The depth of the search
        """
        self._board = board
        self._col1 = column
        self._col2 = column2
        self._depth = depth

    @property
    def board(self):
        """
        Property getter.
        :return: The board
        """
        return self._board

    @property
    def col1(self):
        """
        Property getter.
        :return: The column of the computers move
        """
        return self._col1

    @property
    def col2(self):
        """
        Property getter.
        :return: The column of the players move
        """
        return self._col2

    @property
    def depth(self):
        """
        Property getter.
        :return: The depth
        """
        return self._depth


class WorkerMessage:
    """
    Class WorkerMessage represents a message which is sent from the workers to the master.
    """
    def __init__(self, column, evaluation):
        """
        Initialization method.
        :param column: Column for which worker calculated the evaluation
        :param evaluation: Evaluation for the column
        """
        self._col = column
        self._eval = evaluation

    @property
    def col(self):
        """
        Property getter.
        :return: Evaluated column
        """
        return self._col

    @property
    def eval(self):
        """
        Property getter.
        :return: Evaluation of the column
        """
        return self._eval


def is_game_finished(board, last_move_column):
    """
    Method which checks if the game is finished.
    :param board: Current board state
    :param last_move_column: Column where the last token has been put
    :return: True if game is finished, False otherwise
    """
    if board.last_player == Player.HUMAN:
        token = HUMAN
    else:
        token = COMPUTER

    # check if win is vertical
    is_vertical = check_vertically(board, last_move_column, token)
    # check if win is horizontal
    is_horizontal = check_horizontally(board, last_move_column, token)
    # check if win is on the left diagonal
    is_left_diagonal = check_left_diagonal(board, last_move_column, token)
    # check if win is on the right diagonal
    is_right_diagonal = check_right_diagonal(board, last_move_column, token)

    return is_vertical or is_horizontal or is_left_diagonal or is_right_diagonal


def check_vertically(board, last_move_column, token):
    """
    Check if four tokens are aligned vertically.
    :param board: Board
    :param last_move_column: Column where the last token has been put
    :param token: From computer or human
    :return: True if there are four, False otherwise
    """
    start_row = find_row(board, last_move_column)
    counter = 0

    for row in range(start_row, BOARD_SIZE):
        if board.board[row][last_move_column] == token:
            counter += 1
        else:
            break

    return counter == 4


def check_horizontally(board, last_move_column, token):
    """
    Check if four tokens are aligned horizontally.
    :param board: Board
    :param last_move_column: Column where the last token has been put
    :param token: From computer or human
    :return: True if there are four, False otherwise
    """
    start_row = find_row(board, last_move_column)
    counter = 0

    # check right
    for col in range(last_move_column, BOARD_SIZE):
        if board.board[start_row][col] == token:
            counter += 1
        else:
            break

    if counter == 4:
        return True

    # check left
    for col in range(last_move_column+1)[::-1]:
        if col == last_move_column:
            continue
        if board.board[start_row][col] == token:
            counter += 1
        else:
            break

    return counter == 4


def check_left_diagonal(board, last_move_column, token):
    """
    Check if four tokens are aligned diagonally.
    :param board: Board
    :param last_move_column: Column where the last token has been put
    :param token: From computer or human
    :return: True if there are four, False otherwise
    """
    start_row = find_row(board, last_move_column)
    counter = 0
    temp = 0

    # check right
    for row in range(start_row, BOARD_SIZE):
        if last_move_column + temp <= MAX_COLUMN_SIZE and board.board[row][last_move_column + temp] == token:
            counter += 1
        else:
            break
        temp += 1

    if counter == 4:
        return True

    temp = 0

    # check left
    for row in range(start_row + 1)[::-1]:
        if row == start_row:
            temp += 1
            continue
        if last_move_column - temp >= MIN_COLUMN_SIZE and board.board[row][last_move_column - temp] == token:
            counter += 1
        else:
            break
        temp += 1

    return counter == 4


def check_right_diagonal(board, last_move_column, token):
    """
    Check if four tokens are aligned diagonally.
    :param board: Board
    :param last_move_column: Column where the last token has been put
    :param token: From computer or human
    :return: True if there are four, False otherwise
    """
    start_row = find_row(board, last_move_column)
    counter = 0
    temp = 0

    # check right
    for row in range(start_row, BOARD_SIZE):
        if last_move_column - temp >= MIN_COLUMN_SIZE and board.board[row][last_move_column - temp] == token:
            counter += 1
        else:
            break
        temp += 1

    if counter == 4:
        return True

    temp = 0

    # check left
    for row in range(start_row + 1)[::-1]:
        if row == start_row:
            temp += 1
            continue
        if last_move_column + temp <= MAX_COLUMN_SIZE and board.board[row][last_move_column + temp] == token:
            counter += 1
        else:
            break
        temp += 1

    return counter == 4


def find_row(board, column):
    """
    Finds the row where the token is put.
    :param board: Board
    :param column: Column where the token is put
    :return: Row of the current token
    """
    for row in range(BOARD_SIZE):
        if board.board[row][column] != DEFAULT_VALUE:
            return row


def is_move_legal(board, column):
    """
    Check if the token can be put into the given column.
    :param board: The game board
    :param column: Column in which the token should be put
    :return: True if move is legal, False otherwise
    """
    for row in range(BOARD_SIZE):
        if board.board[row][column] == DEFAULT_VALUE:
            return True

    return False


def evaluate(board, column, depth):
    """
    Recursive function which tests out possible moves for the given board.
    :param board: The game board
    :param column: Column of the last move
    :param depth: Depth of the search
    """

    all_lose = True
    all_win = True

    # if the game is finished
    if is_game_finished(board, column):
        if board.last_player == Player.COMPUTER:
            return COMPUTER_WIN
        else:
            return PLAYER_WIN

    if depth == 0:
        return TIE

    # next level
    depth -= 1
    total = 0
    moves = 0

    for col in range(BOARD_SIZE):
        if is_move_legal(board, col):
            moves = moves + 1
            board.make_a_move(col)
            result = evaluate(board, col, depth)
            board.undo_last_move(col)
            if result > -1:
                all_lose = False
            if result != 1:
                all_win = False
            if result == 1 and board.last_player == Player.HUMAN:
                return COMPUTER_WIN
            if result == -1 and board.last_player == Player.COMPUTER:
                return PLAYER_WIN
            total = total + result

    if all_win:
        return COMPUTER_WIN

    if all_lose:
        return PLAYER_WIN

    return total/moves


def get_max_evaluation(evaluate_results, board):
    """
    Finds maximum evaluation amongst the all.
    :param board: The board
    :param evaluate_results: Dictionary of the evaluations by the column
    :return: max evaluation
    """
    results = [FULL_COLUMN]*7

    for column, evaluations in evaluate_results.items():
        temp = 0.0
        cnt = 0
        # if the end of the board is reached, continue
        if FULL_COLUMN in evaluations and not is_move_legal(board, column):
            continue
        else:
            for evaluation in evaluations:
                if evaluation != FULL_COLUMN:
                    cnt += 1
                    temp += evaluation

            results[column] = temp / cnt

    return results


