from .interface import AbstractPlayer


class SimpleAI(AbstractPlayer):
    def __init__(self, board_size, player_num):
        self._board_size = board_size

    def move(self, board, time_limit, ret_val):
        pass

    def get_name(self):
        return "SimpleAI"
