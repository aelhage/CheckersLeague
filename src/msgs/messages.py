"""
messages.py
    - This file defines the ONLY valid message types allowed to be used.

Anthony Trezza
15 Dec 2017

CHANGE LOG:
    - 15 Dec 2017 trezza - Software's Birthday! <(^.^)>
"""
from enum import Enum


# ---------------------------------------------------------------------------- #
# IMPORTANT ENUMERATIONS
# ---------------------------------------------------------------------------- #
class MESSAGE_IDS(Enum):
    CONNECTION_REQUEST = 1
    WAITING_FOR_OPPONENT = 2
    GAME_RULES = 3
    BEGIN_GAME = 4
    YOUR_TURN = 5
    MOVE = 6



    ERROR_MESSAGE = -99


class ERRORS(Enum):
    # COMMON ERRORS #
    INVALID_MSG = 1
    INVALID_MOVE = 2

    # SERVER -> CLIENT #
    OPPONENT_DISCONNECTED = 100


# ---------------------------------------------------------------------------- #
# ERROR MESSAGES
# ---------------------------------------------------------------------------- #
class ErrorMessage:
    """
        TODO
    """
    def __init__(self, error_id=None):
        self.id = MESSAGE_IDS['ERROR_MESSAGE'].value
        self.error_name = ERRORS(error_id).name

    def __iter__(self):
        yield 'id', self.id

        if self.error_name is None:
            raise Exception('error_name Field is Required!')
        else:
            yield 'error_name', self.error_name


# ---------------------------------------------------------------------------- #
# CLIENT <-> SERVER
# ---------------------------------------------------------------------------- #
class Move:
    """
        The Move message defines the fields for the client's move.
    """

    def __init__(self, move_list=[]):
        self.id = MESSAGE_IDS['MOVE'].value
        self.move_list = move_list

    def from_dict(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def __iter__(self):
        yield 'id', self.id

        if self.move_list is None or len(self.move_list) == 0:
            raise Exception('move_list Field is Required!')
        else:
            yield 'move_list', self.move_list


# ---------------------------------------------------------------------------- #
# CLIENT -> SERVER
# ---------------------------------------------------------------------------- #
class ConnectionRequest:
    """
        The ConnectionRequest message defines the mandatory fields for the initial
        message sent from the client to the server.

        MANDATORY FIELDS:
            client_name - the name of your program or team
        OPTIONAL FIELDS:
            none

        JSON FORMAT:
            { 'id': 0, 'name': 'string' }
    """
    def __init__(self, name=None):
        self.id = MESSAGE_IDS['CONNECTION_REQUEST'].value
        self.name = name

    def from_dict(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def __iter__(self):
        yield 'id', self.id

        if self.name is None:
            raise Exception('name Field is Required!')
        else:
            yield 'name', self.name


# ---------------------------------------------------------------------------- #
# SERVER -> CLIENT
# ---------------------------------------------------------------------------- #
class WaitingForOpponent:
    """
        The WaitingForOpponent message defines the message that the server will
        send to the client when the current client does not have a pair to play
        against.

        When "flag" is true -> the client should wait until they receive a "false"
        flag.

        MANDATORY FIELDS:
            flag
    """
    def __init__(self, flag=None):
        self.id = MESSAGE_IDS['WAITING_FOR_OPPONENT'].value
        self.flag = flag

    def from_dict(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def __iter__(self):
        yield 'id', self.id

        if self.flag is None:
            raise Exception('flag Field is Required!')
        else:
            yield 'flag', self.flag


class GameRules:
    """
        tmp
        MANDATORY FIELDS:

    """
    def __init__(self, player_color=None, num_players=None, time_limit=None, board_size=None):
        self.id = MESSAGE_IDS['GAME_RULES'].value
        self.player_color = player_color
        self.num_players = num_players
        self.time_limit = time_limit
        self.board_size = board_size

    def from_dict(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def __iter__(self):
        yield 'id', self.id

        if self.player_color is None:
            raise Exception('player_color Field is Required!')
        else:
            yield 'player_color', self.player_color

        if self.num_players is None:
            raise Exception('num_players Field is Required!')
        else:
            yield 'num_players', self.num_players

        if self.time_limit is None:
            raise Exception('time_limit Field is Required!')
        else:
            yield 'time_limit', self.time_limit

        if self.board_size is None:
            raise Exception('board_size Field is Required!')
        else:
            yield 'board_size', self.board_size


class BeginGame:
    """
        tmp
        MANDATORY FIELDS:

    """
    def __init__(self):
        self.id = MESSAGE_IDS['BEGIN_GAME'].value

    def from_dict(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def __iter__(self):
        yield 'id', self.id


class YourTurn:
    """
        tmp
        MANDATORY FIELDS:

    """
    def __init__(self):
        self.id = MESSAGE_IDS['YOUR_TURN'].value

    def from_dict(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def __iter__(self):
        yield 'id', self.id