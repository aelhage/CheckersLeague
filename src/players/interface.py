import abc


class AbstractPlayer:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, board_size, player_num):
        raise NotImplementedError("Derived class must implement __init__")

    @abc.abstractmethod
    def move(self, board, time_limit, ret_val):
        raise NotImplementedError("Derived class must implement move")

    @property
    @abc.abstractmethod
    def name(self):
        raise NotImplementedError("Derived class must implement name")
