from .interface import AbstractPlayer
import time
import collections
import copy


class SimpleAI(AbstractPlayer):
    def __init__(self, board_size, player_num):
        self._player = 'w' if player_num == 1 else 'b'

    def move(self, board, time_limit, ret_val):
        start_time = time.monotonic()
        end_time = start_time + 0.95 * time_limit  # Only use a portion of allotted to account for overhead
        nodes = collections.deque()
        root_node = ProcessingNode(board, self._player, self._player)
        nodes.append(root_node)
        # Build game tree breadth-first until time expires
        while time.monotonic() < end_time and len(nodes) > 0:
            node = nodes.popleft()
            nodes.extend(node.generate_child_nodes())
        # Best move needs to be added to ret_val to return to caller since this will be running on a separate thread
        ret_val.extend(root_node.get_best_move())

    def get_name(self):
        return "SimpleAI"


class ProcessingNode:
    """A ProcessingNode represents a node in the game tree."""
    def __init__(self, board, player, mover, move=None):
        """Inits a ProcessingNode with the specified parameters.

        :param board: Board representation at this node.
        :param player: Player whose optimal move the game tree is solving for. 'w' for white, 'b' for black.
        :param mover: Player who moves next after reaching specified board. 'w' for white, 'b' for black.
        :param move: Move which resulted in reaching this node.
        """
        self._children = []
        self._player = player
        self._board = board
        self._mover = mover
        self.move = move

    def calculate_utility(self):
        """Calculate the utility of the move represented by this node."""
        if len(self._children) == 0:
            # If there are no children, this is leaf node. Utility based on pieces on the board.
            return sum([(1 if i.lower() == self._player else -1) * (1 if i.islower() else 3)
                        for row in self._board for i in row if i != 0 and i != '_'])
        elif self._mover == self._player:
            # If this node represents a move by this player, the optimal move will be chosen, so return max of children
            return max([c.calculate_utility() for c in self._children])
        else:
            # If this node represents a move by opponent, assume opponent will play optimally, so return min of children
            return min([c.calculate_utility() for c in self._children])

    def generate_child_nodes(self):
        """Creates children nodes in the game tree.

        :return list: List of ProcessingNode descendants of this node.
        """
        child_mover = 'b' if self._mover == 'w' else 'w'
        self._children.clear()
        pieces = self._get_pieces()
        for piece in pieces:
            moves = self._generate_moves(piece)
            for move in moves:
                # Execute move on copy of board and create new node
                board_copy = copy.deepcopy(self._board)
                move_pairs = [[move[i], move[i + 1]] for i in range(len(move) - 1)]
                for pair in move_pairs:
                    board_copy[pair[1][0]][pair[1][1]] = board_copy[pair[0][0]][pair[0][1]]
                    board_copy[pair[0][0]][pair[0][1]] = 0
                    # A pawn is promoted when it reaches the last row
                    if (pair[1][0] == len(board_copy) - 1 and child_mover == 'w') or (
                            pair[1][0] == 0 and child_mover == 'b'):
                        board_copy[pair[1][0]][pair[1][1]] = board_copy[pair[1][0]][pair[1][1]].upper()
                    # A piece is removed if jumped over
                    if abs(pair[1][0] - pair[0][0]) == 2:
                        xp = (pair[0][0] + pair[1][0]) // 2
                        yp = (pair[0][1] + pair[1][1]) // 2
                        board_copy[xp][yp] = 0
                self._children.append(ProcessingNode(board_copy, self._player, child_mover, move))
        return self._children

    def get_best_move(self):
        """Returns the move corresponding to the child node with the highest utility."""
        return max(self._children, key=lambda c: c.calculate_utility()).move

    def _get_pieces(self):
        """Gets a list of piece locations for the mover of this node.

        :returns list: List of location tuples
        """
        return [(ix, iy)
                for ix, row in enumerate(self._board)
                for iy, i in enumerate(row)
                if isinstance(i, str) and i.lower() == self._mover]

    def _generate_moves(self, loc, start_board=None):
        """Generates list of valid moves for the piece at loc.

        Valid moves for the piece at loc. Moves are represented as a list of locations, eg, [(x1,y1),(x2,y2)], including
        the starting location.

        If a board is provided, only valid jumps (not all moves) will be returned. The intention is a board is only
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
        board_size = len(start_board)
        move_piece = start_board[loc[0]][loc[1]].lower()
        for step in self._generate_steps(loc, start_board):
            board = copy.deepcopy(start_board)  # create copy to test jumps on
            x, y = loc[0] + step[0], loc[1] + step[1]
            if 0 <= x < board_size and 0 <= y < board_size:
                if isinstance(board[x][y], str) and board[x][y].lower() == ('w' if move_piece == 'b' else 'b'):
                    xp, yp = x + step[0], y + step[1]
                    if (0 <= xp < board_size and 0 <= yp < board_size and
                            board[xp][yp] == 0):
                        # Move starting piece to end location
                        board[xp][yp] = board[loc[0]][loc[1]]
                        # Set starting and jumped piece to empty
                        board[loc[0]][loc[1]] = board[x][y] = 0
                        # A pawn is promoted when it reaches the last row
                        if (xp == board_size - 1 and move_piece == 'w') or (xp == 0 and move_piece == 'b'):
                            board[xp][yp] = board[xp][yp].upper()

                        jumps.append([loc, (xp, yp)])
                        jumps.extend([[loc] + jump_extension
                                      for jump_extension in self._generate_moves((xp, yp), board)])
                elif board[x][y] == 0 and not jumps_only:
                    moves.append([loc, (x, y)])
        return jumps if len(jumps) or jumps_only > 0 else moves

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
