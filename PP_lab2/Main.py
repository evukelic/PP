from Board import Board
from Constants import *

import Helper
from Helper import WorkerMessage
from Helper import MasterMessage

from mpi4py import MPI

import sys
import time


if __name__ == "__main__":
    """
    Main method which tests out the Connect4 game.
    The game runs by entering 'mpiexec -n <processes_number> python Main.py' into the terminal.
    """
    communicator = MPI.COMM_WORLD
    size = communicator.size
    rank = communicator.rank

    # the master
    if rank == 0:
        # initialize the board
        board = Board()

        while True:
            depth = DEFAULT_DEPTH
            # get the players move, and if the column is full, enter it again
            players_move = input()
            if not Helper.is_move_legal(board, int(players_move)):
                continue
            board.make_a_move(int(players_move))
            board.print_out_board()
            sys.stdout.flush()

            # if the game is finished, done
            if Helper.is_game_finished(board, int(players_move)):
                exit()

            best_move = -2
            evaluate_results = {}
            worker_rank = 1
            tasks = 0

            # start the timer
            # start = time.time()

            # create the MasterMessage and send them to the workers "in a circle", so they can start with a task
            # there will be 49 of them
            for col in range(BOARD_SIZE):
                for col2 in range(BOARD_SIZE):
                    msg = MasterMessage(board, col, col2, depth)
                    communicator.send(msg, dest=worker_rank % size)
                    tasks += 1
                    worker_rank += 1
                    # skip the master
                    if worker_rank % size == 0:
                        worker_rank += 1

            for i in range(tasks):
                # get the WorkerMessage
                evaluation = communicator.recv(source=MPI.ANY_SOURCE)
                if evaluation.col not in evaluate_results:
                    evaluate_results[evaluation.col] = []
                # put it into the dictionary of evaluations by the column
                evaluate_results[evaluation.col].append(evaluation.eval)

            # calculate the best evaluations
            results = Helper.get_max_evaluation(evaluate_results, board)

            best_col = -1

            # get the best column for the next move
            for index, value in enumerate(results):
                if value != FULL_COLUMN and value > best_move:
                    best_move = value
                    best_col = index

            # format and print out the results
            results = [FULL_COLUMN if res == FULL_COLUMN else FORMATTING.format(res) for res in results]
            print(', '.join(results))
            sys.stdout.flush()

            # pc makes the move
            board.make_a_move(best_col)
            board.print_out_board()

            # stop the timer and print the time
            # end = time.time()
            # print(end-start)

            # if the game is finished, done
            if Helper.is_game_finished(board, best_col):
                exit()

    # the workers
    else:
        while True:
            # get the MasterMessage
            message = communicator.recv(source=0)
            # if the column is not full make a move, and check if the game can be finished
            if Helper.is_move_legal(message.board, message.col1):
                message.board.make_a_move(message.col1)
                if Helper.is_game_finished(message.board, message.col1):
                    res = COMPUTER_WIN
                else:
                    # if the column is not full make a move, and check if the game can be finished
                    if Helper.is_move_legal(message.board, message.col2):
                        message.board.make_a_move(message.col2)
                        if Helper.is_game_finished(message.board, message.col2):
                            res = PLAYER_WIN
                        else:
                            # if the game is not yet finished, evaluate the next move
                            res = Helper.evaluate(message.board, message.col1, message.depth)
                        message.board.undo_last_move(message.col2)
                message.board.undo_last_move(message.col1)
            else:
                # the column is full
                res = FULL_COLUMN
            # send the WorkerMessage
            communicator.send(WorkerMessage(message.col1, res), dest=0)
