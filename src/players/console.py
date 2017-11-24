from .interface import AbstractPlayer


class ConsolePlayer(AbstractPlayer):
    def __init__(self, board_size, player_num):
        self._name = input("Enter your player name:")

    def move(self, board, time_limit, ret_val):
        while True:
            user_input = input("Enter you move in the format 'from_row,from_col;to_row,to_col':")
            try:
                ret_val.extend(tuple(tuple(int(x.strip()) for x in loc.split(',')) for loc in user_input.split(';')))
                break
            except ValueError:
                print("Invalid move!")

    def get_name(self):
        return self._name
