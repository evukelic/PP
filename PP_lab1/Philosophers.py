from mpi4py import MPI
import time
import sys
import numpy as np


def print_tabs(rank):
    """
    Helper function for printing out messages; it generates tabs regarding the rank of the process.
    :param rank: rank of the process
    :return: tabs
    """
    tabs = ''
    for i in range(rank):
        tabs += '\t'
    return tabs


class Fork:
    """
    Class Fork represents a fork.
    """

    def __init__(self):
        """
        Initializes one Fork object which can be clean or dirty.
        Initially, fork is dirty.
        """
        self._clean = False

    def use_fork(self):
        """
        When fork is used, it becomes dirty.
        """
        self._clean = False

    def clean_fork(self):
        """
        Function which cleans fork.
        """
        self._clean = True

    @property
    def clean(self):
        return self._clean


class Philosopher:
    """
    Class Philosopher represents one Philosopher.
    It solves 'The drinking Philosophers problem' by running the function 'run'.
    """

    def __init__(self, comm, think, eat):
        """
        Initializes one Philosopher object.
        :param comm: communicator
        :param think: thinking duration
        :param eat: eating duration
        """
        # communicator
        self._comm = comm
        # number of processes
        self._size = self._comm.Get_size()
        # rank of the process
        self._rank = self._comm.Get_rank()
        # thinking duration
        self._thinking_time = think
        # eating duration
        self._eating_time = eat
        # True if Philosopher has both forks
        self._has_both_forks = False
        # left fork
        self._left_fork = None
        # right fork
        self._right_fork = None
        self.init_forks()
        # queued requests
        self._requests = []

    def init_forks(self):
        """
        Initializes forks. Process with rank 0 will have both forks, n-th process won't have any,
        and the rest will have only one fork.
        """
        if self._rank == 0:
            self._left_fork = Fork()
            self._right_fork = Fork()
            self._has_both_forks = True
        elif self._rank != self._size-1:
            self._right_fork = Fork()

    def think(self, left, right):
        """
        Function 'think' represents one thinking period of the Philosopher.
        Messages are represented as a tuple '(message_type(request or response), rank_of_the_sender)'
        :param left: rank of the Philosopher who sits left of the current one
        :param right: rank of the Philosopher who sits right of the current one
        """
        # listen for the requests
        if not self._comm.Iprobe(source=int(left)) and not self._comm.Iprobe(source=int(right)):
            time.sleep(1)
        # receive request from the left process, and send back the response
        if self._comm.Iprobe(source=int(left)):
            message_left, sender_left = self._comm.recv(source=int(left))
            self.send_response(sender_left)
            self._left_fork = None
        # receive request from the right process, and send back the response
        if self._comm.Iprobe(source=int(right)):
            message_right, sender_right = self._comm.recv(source=int(right))
            self.send_response(sender_right, False)
            self._right_fork = None

    def send_response(self, rank, left=True):
        """
        Function which sends a response (a fork) from one Philosopher to another.
        :param rank: rank of the Philosopher to whom response will be sent
        :param left: is the Philosopher left of the current one?
        """
        # Remove the fork which has been sent to another Philosopher
        if left is True:
            self._left_fork = None
        else:
            self._right_fork = None
        if self._left_fork is None or self._right_fork is None:
            self._has_both_forks = False

        self._comm.send(('response', self._rank), dest=int(rank))
        time.sleep(0.5)

    def send_request(self, rank):
        """
        Function which sends a request for the fork to another Philosopher.
        :param rank: rank of the Philosopher to whom request will be sent
        """
        self._comm.send(('request', self._rank), dest=int(rank))

    def request_fork(self, rank, left=True):
        """
        Function 'request_fork' represents a behaviour of a Philosopher while requesting the fork.
        :param rank: rank of the Philosopher to whom request will be sent
        :param left: is the Philosopher left of the current one?
        """
        print(print_tabs(self._rank) + '(' + str(self._rank) + '): trazim vilicu')
        sys.stdout.flush()
        self.send_request(rank)

        while True:
            # receive the message
            message, sender = self._comm.recv(source=int(rank))
            # if message is 'response', update the forks
            if str(message) == 'response':
                if left is True:
                    self._left_fork = Fork()
                    self._left_fork.clean_fork()
                else:
                    self._right_fork = Fork()
                    self._right_fork.clean_fork()
                return
            # if message is 'request' and if wanted fork is dirty, send it, and if not - store the request for later
            else:
                if left is True:
                    if self._left_fork.clean is False:
                        self.send_response(rank)
                    else:
                        self._requests.append((message, sender))
                else:
                    if self._right_fork.clean is False:
                        self.send_response(rank, False)
                    else:
                        self._requests.append((message, sender))

    def eat(self):
        """
        Function 'eat' represents one eating period for the Philosopher.
        """
        print(print_tabs(self._rank) + '(' + str(self._rank) + '): jedem')
        sys.stdout.flush()
        time.sleep(self._eating_time)
        # when done, forks are dirty
        self._left_fork.use_fork()
        self._right_fork.use_fork()

    def run(self):
        """
        Function 'run' starts the algorithm for every Philosopher.
        Algorithm runs until it's interrupted by the user.
        """
        while True:
            print(print_tabs(self._rank) + '(' + str(self._rank) + '): mislim')
            sys.stdout.flush()

            start = MPI.Wtime()

            # find rank of the Philosopher who sits left of the current one
            left_rank = (self._rank - 1) % self._size
            # find rank of the Philosopher who sits right of the current one
            right_rank = (self._rank + 1) % self._size

            # timer for the thinking period
            while MPI.Wtime() - start < self._thinking_time:
                self.think(left_rank, right_rank)

            # if Philosopher doesn't have both forks
            while self._has_both_forks is False:
                if self._left_fork is None:
                    # if left one is missing, send the request
                    self.request_fork(left_rank)
                if self._right_fork is None:
                    # if right one is missing, send the request
                    self.request_fork(right_rank, False)
                if self._left_fork is not None and self._right_fork is not None:
                    self._has_both_forks = True

            self.eat()

            # send the remaining requests which have been stored
            for msg, rnk in self._requests:
                if int(rnk) == int(left_rank):
                    self.send_response(rnk)
                else:
                    self.send_response(rnk, False)


if __name__ == '__main__':
    world_size = MPI.COMM_WORLD.Get_size()
    if world_size < 2:
        print('Invalid number of processes! Number has to be greater than 1.')
        exit()

    thinking_time = np.random.randint(1, 10)
    eating_time = np.random.randint(1, 10)

    Philosopher(MPI.COMM_WORLD, thinking_time, eating_time).run()
