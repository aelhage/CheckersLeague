"""
board_gui.py
    - Main callable method for executing a local simulation with a PyGame GUI.

Anthony Trezza
20 Dec 2017

CHANGE LOG:
    - 20 Dec 2017 trezza - Software Birthday <(^.^)>
"""

from board_gui import CheckerBoardGUI
from board import CheckerBoard
from utils.jsonsocket import *

from threading import Thread
import socket
import copy
import time
from random import choice
import pygame


# Predefined Color Templates for the GUI
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
CREAM = (255, 245, 180)


class CheckerBoardServer(CheckerBoardGUI):
    def __init__(self, board_size, time_limit, player_sockets, player_info):
        """ Inits a CheckerBoardGUI with the specified parameters.

        :param board_size: Size of the square board to be used. Must be even and >= 4.
        :param time_limit: Time in seconds each player has to act
        :param player_socket: List of two client socket handles.
        :raises TypeError: if player1 or player2 not an instance of socket.socket
        :raises ValueError: if board_size is not an even number or less than 4
        """

        # 0. Input Checking
        if player_sockets.size() != 2:
            raise ValueError('Invalid number of players!')
        for player in player_sockets:
            if not isinstance(player, socket.socket):
                raise TypeError('player is not a socket handle')
        if not board_size % 2 == 0:
            raise ValueError('Board size must be divisible by 2')
        if board_size < 4:
            raise ValueError('Board size must be at least 4')

        # 1. Initialize the input class parameters
        self.game_over = False
        self._board_size = board_size
        self._time_limit = time_limit
        self._num_players = 2

        self._players = []
        for idx, player in enumerate(player_sockets):
            self._players.append((player_info, player))

        # 3. Setup the Checker Board
        self._cb = CheckerBoard(self._board_size)

        # 2. Setup the gui
        self._setup_window()

    def terminate_game(self):
        # MUTEX STUFFFFFF
        self.game_over = True
        # END MUTEX

    def play(self):
        # Send the rules and the begin game messages!
        gr = GameRules(player_color=None, num_players=self._num_players, time_limit=self._time_limit, board_size=self._board_size)
        bg = BeginGame()
        for player_info, player in self._players:
            gr.player_color = player_info[0]
            json_send(player, dict(gr))
            json_send(player, dict(bg))

        move_ind = 0
        # Loop until end game conditions met
        while not self.game_over or not self._cb.get_winner():
            self._update()

            player_info, player = self._players[move_ind % 2]

            # Send the 'your turn' message
            json_send(player, dict(YourTurn))

            time.sleep(self._time_limit)

            # Send the 'time out' message
            json_send(player, dict(TimeOut()))

            # Read the move
            try:
                data = json_recv(player)
                moves = Moves()
                moves = moves.from_dict(data)

                if moves.id != MESSAGE_IDS["MOVES"].value:
                    raise Exception("Invalid Message.")

                if moves.moves.size() == 0:
                    raise Exception("No Moves Received!")

            except socket.timeout:
                print('[!] Socket Timed Out - Random Move made for ' + player_info[1])
                pass

            # Start a new thread to wait for Player move
            ret_val = []  # list representing move returned from player
            t = Thread(target=player.move, args=(copy.deepcopy(self._cb), self._time_limit, ret_val))
            t.start()
            t.join(self._time_limit)
            if not self._cb.execute_move(ret_val):
                print('Invalid move {} by player {}'
                      .format(ret_val, player.get_name()))
                # Choose random valid move, taking into account forced capture
                pieces = self._cb.get_locations_by_color(player_piece)
                moves = []
                jumps = []
                for piece in pieces:
                    is_jump, piece_moves = self._cb.generate_moves(piece)
                    if is_jump:
                        jumps.extend(piece_moves)
                    else:
                        moves.extend(piece_moves)
                move = choice(jumps) if len(jumps) > 0 else choice(moves)
                self._cb.execute_move(move)
                print('Playing random move instead: {}'.format(move))
            move_ind += 1
