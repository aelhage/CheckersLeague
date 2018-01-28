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
from msgs.messages import *

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

# TODO: Kill Pygame after game completion, don't crash if someone exits (or crashes)!


class CheckerBoardServer(CheckerBoardGUI):
    def __init__(self, player_sockets, player_names, time_limit):
        """ Inits a CheckerBoardGUI with the specified parameters.

        :param player_socket: List of two client socket handles.
        :raises TypeError: if player1 or player2 not an instance of socket.socket
        :raises ValueError: if board_size is not an even number or less than 4
        """

        # 0. Input Checking
        if len(player_sockets) != 2:
            raise ValueError('Invalid number of players!')
        for player in player_sockets:
            if not isinstance(player, socket.socket):
                raise TypeError('player is not a socket handle')

        # 1. Initialize the input class parameters
        self.game_over = False
        self._board_size = 10
        self._time_limit = time_limit
        self._num_players = 2

        self._players = []
        self.player_names = player_names
        player_info = ['w', 'b']
        for idx, player in enumerate(player_sockets):
            self._players.append((player_info[idx], player))

        # 3. Setup the Checker Board
        self._cb = CheckerBoard(self._board_size)

        # 2. Setup the gui
        self._setup_window()

    def terminate_game(self):
        self.game_over = True
        pygame.display.quit()
        pygame.quit()

    def random_move(self, player_info):
        # Choose random valid move, taking into account forced capture
        pieces = self._cb.get_locations_by_color(player_info)
        moves = []
        jumps = []
        for piece in pieces:
            is_jump, piece_moves = self._cb.generate_moves(piece)
            if is_jump:
                jumps.extend(piece_moves)
            else:
                moves.extend(piece_moves)
        move = choice(jumps) if len(jumps) > 0 else choice(moves)
        print('[.] Playing random move: {}'.format(move))
        return move

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
        while not self.game_over:
            try:
                self._update()

                player_info, player = self._players[move_ind % 2]

                # Send the 'your turn' message
                json_send(player, dict(YourTurn()))

                move = Move()

                # Read the move
                data = json_recv(player)
                move.from_dict(data)
                for i in range(len(move.move_list)):
                    move.move_list[i] = tuple(move.move_list[i])

                if move is None or move.id != MESSAGE_IDS["MOVE"].value or len(move.move_list) == 0:
                    print("[!] Invalid Message Received from {}".format(player_info))
                    print("[.] Generating random move...")
                    move.move_list = self.random_move(player_info)

                    for tmp_player_info, tmp_player in self._players:
                        json_send(tmp_player, dict(move))

                    self._cb.execute_move(move.move_list)
                    move_ind += 1

                    winner = self._cb.get_winner()
                    if winner:
                        self.game_over = True
                        break
                    else:
                        continue

                # Make the move (unless it is invalid)
                if not self._cb.execute_move(move.move_list):
                    print("[!] Invalid move {}, received from {}, random move will be generated...".format(move.move_list, player_info))
                    move.move_list = self.random_move(player_info)

                    for tmp_player_info, tmp_player in self._players:
                        json_send(tmp_player, dict(move))

                    self._cb.execute_move(move.move_list)
                    move_ind += 1

                    winner = self._cb.get_winner()
                    if winner:
                        self.game_over = True
                        break
                    else:
                        continue

                # If it made it this far, then the move succeeded!
                # Send the official move to the players and continue!
                for tmp_player_info, tmp_player in self._players:
                    json_send(tmp_player, dict(move))

                move_ind += 1

                winner = self._cb.get_winner()
                if winner:
                    self.game_over = True
                    break
                else:
                    continue

            except KeyboardInterrupt:
                self.game_over = True

            except socket.timeout:
                # TODO: Reply with timeout message and send the random move to all players
                print('[!] Socket Timed Out - Random Move made for ' + player_info[0])
                move.move_list = self.random_move(player_info)

                for tmp_player_info, tmp_player in self._players:
                    json_send(tmp_player, dict(move))

                self._cb.execute_move(move.move_list)
                move_ind += 1

                winner = self._cb.get_winner()
                if winner:
                    self.game_over = True
                    break
                else:
                    continue

        print("[.] Congratulations {} You are the Winner!".format(winner))
        go = GameOver(winner)
        for tmp_player_info, tmp_player in self._players:
            json_send(tmp_player, dict(go))

        self.terminate_game()