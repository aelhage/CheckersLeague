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
        root_node = ProcessingNode(board, self._player)
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
    def __init__(self, board, player, move=None):
        """Inits a ProcessingNode with the specified parameters.

        :param board: CheckerBoard representation at this node.
        :param player: Player whose optimal move the game tree is solving for. 'w' for white, 'b' for black.
        :param move: Move which resulted in reaching this node.
        """
        self._children = []
        self._player = player
        self._board = board
        self.move = move

    def calculate_utility(self):
        """Calculate the utility of the move represented by this node."""
        if len(self._children) == 0:
            # If there are no children, this is leaf node. Utility based on pieces on the board.
            return sum([(1 if i.lower() == self._player else -1) * (1 if i.islower() else 3)
                        for row in self._board for i in row if i != 0 and i != '_'])
        elif self._board.current_player == self._player:
            # If this node represents a move by this player, the optimal move will be chosen, so return max of children
            return max([c.calculate_utility() for c in self._children])
        else:
            # If this node represents a move by opponent, assume opponent will play optimally, so return min of children
            return min([c.calculate_utility() for c in self._children])

    def generate_child_nodes(self):
        """Creates children nodes in the game tree.

        :return list: List of ProcessingNode descendants of this node.
        """
        self._children.clear()
        pieces = self._board.get_locations_by_color(self._board.current_player)
        for piece in pieces:
            _, moves = self._board.generate_moves(piece)
            for move in moves:
                # Execute move on copy of board and create new node
                board_copy = copy.deepcopy(self._board)
                board_copy.execute_move(move)
                self._children.append(ProcessingNode(board_copy, self._player, move))
        return self._children

    def get_best_move(self):
        """Returns the move corresponding to the child node with the highest utility."""
        return max(self._children, key=lambda c: c.calculate_utility()).move
