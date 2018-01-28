"""
board_gui.py
    - Main callable method for executing a local simulation with a PyGame GUI.

Alex Elhage
11 Nov 2017

CHANGE LOG:
    - 16 Dec 2017 trezza - Updated

"""

from board import CheckerBoard
from players.interface import AbstractPlayer
from players.simple_ai import SimpleAI
from threading import Thread
import copy
from random import choice
import pygame


# Predefined Color Templates for the GUI
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
CREAM = (255, 245, 180)


class CheckerBoardGUI:
    def __init__(self, board_size, time_limit, player1, player2):
        """ Inits a CheckerBoardGUI with the specified parameters.

        :param board_size: Size of the square board to be used. Must be even and >= 4.
        :param time_limit: Time in seconds each player has to act
        :param player1: Class to initialize first player from.
        :param player2: Class to initialize second player from.
        :raises TypeError: if player1 or player2 not subclass of AbstractPlayer
        :raises ValueError: if board_size is not an even number or less than 4
        """

        # 0. Input Checking
        if not issubclass(player1, AbstractPlayer):
            raise TypeError('Player 1 did not implement AbstractPlayer')
        elif not issubclass(player2, AbstractPlayer):
            raise TypeError('Player 2 did not implement AbstractPlayer')
        if not board_size % 2 == 0:
            raise ValueError('Board size must be divisible by 2')
        if board_size < 4:
            raise ValueError("Board size must be at least 4")

        # 1. Initialize the input class parameters
        self._board_size = board_size
        self._time_limit = time_limit
        self._players = [('w', player1(self._board_size, 1)), ('b', player2(self._board_size, 2))]

        # 3. Setup the Checker Board
        self._cb = CheckerBoard(self._board_size)

        # 2. Setup the gui
        self._setup_window()

    def play(self):
        move_ind = 0
        # Loop until end game conditions met
        while not self._cb.get_winner():
            self._update()
            player_piece, player = self._players[move_ind % 2]
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

    def _setup_window(self):
        pygame.init()
        window_size = 600
        self._square_size = window_size // self._board_size
        self._screen = pygame.display.set_mode((window_size, window_size))
        font = pygame.font.Font(None, 28)
        self._white_king_text = font.render('K', True, BLACK)
        self._black_king_text = font.render('K', True, WHITE)

    def _update(self):
        # Draw board background
        for row in range(self._board_size):
            for col in range(self._board_size):
                color = CREAM if (col + (row % 2)) % 2 == 0 else GREEN
                self._screen.fill(color, pygame.Rect(col * self._square_size,
                                                     row * self._square_size,
                                                     self._square_size, self._square_size))

        # Draw pieces
        for piece in self._cb.get_pieces():
            color = WHITE if piece[0].lower() == 'w' else BLACK
            x = piece[1][1] * self._square_size + self._square_size // 2
            y = piece[1][0] * self._square_size + self._square_size // 2
            pygame.draw.circle(self._screen, color, (x, y), self._square_size // 4)
            # If king, draw 'K' in the middle of piece
            if piece[0].isupper():
                self._screen.blit(self._white_king_text if piece[0].lower() == 'w' else self._black_king_text,
                                  (x - self._white_king_text.get_width() // 2,
                                   y - self._white_king_text.get_height() // 2))

        pygame.display.update()


def main():
    """ main()
        - Simply instantiates the CheckerBoardGUI and runs it
    :param: void
    :return: void
    """
    cb_gui = CheckerBoardGUI(10, 1, SimpleAI, SimpleAI)
    cb_gui.play()
    pygame.display.quit()
    pygame.quit()


if __name__ == '__main__':
    main()
