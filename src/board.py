from random import shuffle
from players.interface import AbstractPlayer
from players.console import ConsolePlayer
from threading import Thread
import copy
from random import choice


class CheckerBoard:
    """The CheckerBoard manages a Checkers match between two players."""
    def __init__(self, player1, player2, board_size, time_limit):
        """Inits a CheckerBoard with the specified parameters.

        :param player1: Class to initialize first player from.
        :param player2: Class to initialize second player from.
        :param board_size: Size of the square board to be used. Must be even.
        :param time_limit: Time in seconds each player has to act
        :raises TypeError: if player1 or player2 not subclass of AbstractPlayer
        :raises ValueError: if board_size is not an even number
        """
        if not issubclass(player1, AbstractPlayer):
            raise TypeError("Player 1 did not implement AbstractPlayer")
        elif not issubclass(player2, AbstractPlayer):
            raise TypeError("Player 2 did not implement AbstractPlayer")
        if not board_size % 2 == 0:
            raise ValueError("Board size must be divisible by 2")

        # Randomly select player 1, ie, which goes first
        players = [player1, player2]
        shuffle(players)
        self._white_player = players[0](board_size, 1)
        self._black_player = players[1](board_size, 2)
        # TODO: Log player names, pieces

        self._time_limit = time_limit
        self._board_size = board_size

        """
        Build board to desired size.
        
        The board is represented by a 2D array of characters. Each element is
        either a 'b', 'B', 'w', 'W', 0, or '_'. These represent a black pawn,
        black king, white pawn, white king, empty space, or invalid space. 
        """
        self._board = []
        player_rows = (board_size / 2) - 1
        # Add white player rows
        row_ind = 0
        while row_ind < player_rows:
            row = ['_' if (j + (row_ind % 2)) % 2 == 0 else 'w' for j in range(board_size)]
            self._board.append(row)
            row_ind += 1
        # Add neutral rows
        while row_ind < player_rows + 2:
            row = ['_' if (j + (row_ind % 2)) % 2 == 0 else 0 for j in range(board_size)]
            self._board.append(row)
            row_ind += 1
        # Add black player rows
        while row_ind < board_size:
            row = ['_' if (j + (row_ind % 2)) % 2 == 0 else 'b' for j in range(board_size)]
            self._board.append(row)
            row_ind += 1

    def play(self):
        """Starts a Checkers match and returns the name of the winner.

        :returns string: Name of winning player.
        """
        players = [('w', self._white_player), ('b', self._black_player)]
        move_ind = 0
        # Until end game conditions met
        while not self._check_end_game():
            self.print()
            player_piece, player = players[move_ind % 2]
            # Start a new thread to wait for Player move
            ret_val = []  # list representing move returned from player
            t = Thread(target=player.move, args=(copy.copy(self._board), self._time_limit, ret_val))
            t.start()
            t.join(self._time_limit)
            if not self._execute_move(player_piece, ret_val):
                print("Invalid move {} by player {}"
                      .format(ret_val, player.name))
                # Choose random valid move, taking into account forced capture
                pieces = self._get_pieces(player_piece)
                moves = []
                jumps = []
                for piece in pieces:
                    is_jump, piece_moves = self._generate_moves(piece)
                    piece_moves = [[piece] + move for move in piece_moves]
                    if is_jump:
                        jumps.extend(piece_moves)
                    else:
                        moves.extend(piece_moves)
                move = choice(jumps) if len(jumps) > 0 else choice(moves)
                self._execute_move(player_piece, move)
                print("Playing random move instead: {}".format(move))
            move_ind += 1
        # TODO: Log and print winner

    def print(self):
        print('\n'.join([''.join(['{:^3}'.format(item) for item in row])
                         for row in self._board]))

    def _execute_move(self, player, move):
        """Executes specified move if valid.

        :param player: Character representing which player is moving, 'w' or 'b'
        :param move: Move to execute
        :returns bool: true if move is executed successfully, false otherwise
        """
        # TODO: Check whether move is valid format
        valid_move = False
        # Create temp backup of board in case moves need to be undone
        temp_board = copy.deepcopy(self._board)
        # Group moves into pairs to handle multiple jumps
        move_pairs = [[move[i], move[i+1]] for i in range(len(move) - 1)]
        for pair in move_pairs:
            if self._validate_move(player, pair):
                valid_move = True
                self._board[pair[1][0]][pair[1][1]] = self._board[pair[0][0]][pair[0][1]]
                self._board[pair[0][0]][pair[0][1]] = 0
                # A pawn is promoted when it reaches the last row
                if (pair[1][0] == self._board_size - 1 and player == 'w') or (pair[1][0] == 0 and player == 'b'):
                    self._board[pair[1][0]][pair[1][1]] = self._board[pair[1][0]][pair[1][1]].upper()
                # A piece is removed if jumped over
                if abs(pair[1][0] - pair[0][0]) == 2:
                    xp = (pair[0][0] + pair[1][0]) // 2
                    yp = (pair[0][1] + pair[1][1]) // 2
                    self._board[xp][yp] = 0
            else:
                valid_move = False
                break
        # If full move was invalid, restore board to state prior to executing any moves
        if not valid_move:
            self._board = temp_board
        # TODO: Log each move
        return valid_move

    def _validate_move(self, player, move):
        """Determines whether the move *to* location is a valid end position for piece in *from* location

        :param player: Character representing which player is moving, 'w' or 'b'
        :param move: Move to validate. Tuple in form ((x1,y1),(x2,y2)
        :returns bool: true if move is valid, false otherwise
        """
        if player == self._board[move[0][0]][move[0][1]].lower():
            _, available_moves = self._generate_moves(move[0])
            return move[1:] in available_moves
        else:
            return False

    def _check_end_game(self):
        """Checks for end game status and returns winner

        :returns str: 'w' if white wins, 'b' if black wins, None otherwise
        """
        # TODO: Implement other end game conditions besides no moves available
        black_pieces = self._get_pieces('b')
        black_move_count = sum([len(self._generate_moves(piece)[1]) for piece in black_pieces])
        if black_move_count == 0:
            return 'w'
        white_pieces = self._get_pieces('w')
        white_move_count = sum([len(self._generate_moves(piece)[1]) for piece in white_pieces])
        if white_move_count == 0:
            return 'b'
        return None

    def _generate_moves(self, loc, start_board=None):
        """Generates list of valid moves for the piece at loc.

        Valid moves for the piece at loc. Moves are represented as a list of locations, eg, [(x1,y1),(x2,y2)]. Note
        that this does not include the starting location. Also note that if the move is a single jump, eg, from (loc[0],
        loc[1]) to (x1,y1), the end location will still be in a list, ie, [(x1,y1)].

        If a board is not provided, only valid jumps (not all moves) will be returned. The intention is a board is only
        provided when this is called recursively, checking for multiple jumps.

        :param loc: Location of piece to check
        :param start_board: Board to generate moves for. If not provided, current board state is used.
        :return tuple: First element is boolean indicating whether the moves are jumps or not. Second element is a list
        of location tuples which the piece at loc can move to.
        """
        jumps_only = True
        if start_board is None:
            start_board = self._board
            jumps_only = False
        moves = []
        jumps = []
        move_piece = start_board[loc[0]][loc[1]].lower()
        for step in self._generate_steps(loc, start_board):
            board = copy.deepcopy(start_board)  # create copy to test jumps on
            x, y = loc[0] + step[0], loc[1] + step[1]
            if 0 <= x < self._board_size and 0 <= y < self._board_size:
                if isinstance(board[x][y], str) and board[x][y].lower() == ('w' if move_piece == 'b' else 'b'):
                    xp, yp = x + step[0], y + step[1]
                    if (0 <= xp < self._board_size and 0 <= yp < self._board_size and
                            board[xp][yp] == 0):
                        # Move starting piece to end location
                        board[xp][yp] = board[loc[0]][loc[1]]
                        # Set starting and jumped piece to empty
                        board[loc[0]][loc[1]] = board[x][y] = 0
                        # A pawn is promoted when it reaches the last row
                        if (xp == self._board_size - 1 and move_piece == 'w') or (xp == 0 and move_piece == 'b'):
                            board[xp][yp] = board[xp][yp].upper()

                        jumps.append([(xp, yp)])
                        jumps.extend([[(xp, yp)] + jump_extension for jump_extension in self._generate_moves((xp, yp), board)[1]])
                elif board[x][y] == 0 and not jumps_only:
                    moves.append([(x, y)])
        return (True, jumps) if len(jumps) or jumps_only > 0 else (False, moves)

    @staticmethod
    def _generate_steps(loc, board):
        char = board[loc[0]][loc[1]]
        white_steps = [(1, -1), (1, 1)]
        black_steps = [(-1, -1), (-1, 1)]
        steps = []
        if char != 'b':
            steps.extend(white_steps)
        if char != 'w':
            steps.extend(black_steps)
        return steps

    def _get_pieces(self, w_or_b):
        """Gets a list of piece locations for the specified players

        :param w_or_b: 'w' for white player pieces, 'b' for black player pieces. Other values invalid.
        :returns list: List of location tuples
        """
        return [(ix, iy) for ix, row in enumerate(self._board) for iy, i in enumerate(row) if isinstance(i, str) and i.lower() == w_or_b]


def main():
    cb = CheckerBoard(ConsolePlayer, ConsolePlayer, 8, 1)
    cb.play()


if __name__ == '__main__':
    main()
