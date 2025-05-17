from search import Problem, Node, depth_first_tree_search
from helpers import *

PIECES = {
    'L': [[1, 0], [1, 0], [1, 1]],
    'I': [[1], [1], [1], [1]],
    'T': [[1, 1, 1], [0, 1, 0]],
    'S': [[0, 1, 1], [1, 1, 0]]
}

ORIENTATION_CACHE = {
    piece: get_all_orientations(shape) for piece, shape in PIECES.items()
}

class NuruominoState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NuruominoState.state_id
        NuruominoState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

class Board:
    def __init__(self, matrix, region_map=None):
        self.matrix = matrix
        self.size = len(matrix)
        self.region_map = region_map if region_map else [[cell for cell in row] for row in matrix]
        self.regions = self._build_regions()
        self.region_filled = {region_id: False for region_id in self.regions}

    def _build_regions(self):
        from collections import defaultdict
        regions = defaultdict(list)
        for r in range(self.size):
            for c in range(self.size):
                region_id = self.region_map[r][c]
                regions[region_id].append((r, c))
        return regions

    def adjacent_positions(self, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        return [(row+dr, col+dc) for dr, dc in directions 
                if 0 <= row+dr < self.size and 0 <= col+dc < self.size]

    def print_instance(self):
        for row in self.matrix:
            print("\t".join(str(cell) for cell in row))

    @staticmethod
    def parse_instance():
        from sys import stdin
        return Board([line.strip().split() for line in stdin])

class Nuruomino(Problem):
    def __init__(self, board):
        self.initial = NuruominoState(board)

    def actions(self, state):
        board = state.board

        has_existing_pieces = any(cell in PIECES for row in board.matrix for cell in row)

        # Find unfilled regions
        unfilled_regions = [r for r in board.regions if not board.region_filled[r]]
        if not unfilled_regions:
            return []

        # Heuristic: choose the region with the fewest total placement options
        region_id = min(
            unfilled_regions,
            key=lambda r: sum(
                len(get_all_valid_coords(orient, board.regions[r]))
                for piece in PIECES
                for orient in ORIENTATION_CACHE[piece]
            )
        )
        region_cells = board.regions[region_id]

        connected_actions = []
        disconnected_actions = []

        for piece in PIECES:
            for orientation in ORIENTATION_CACHE[piece]:
                for coords in get_all_valid_coords(orientation, region_cells):

                    # Skip if overlapping existing pieces
                    if any(board.matrix[r][c] in PIECES for r, c in coords):
                        print(f"[DEBUG] ❌ Skipping action: {piece} at {coords} — overlaps existing pieces.")
                        continue


                    # Skip if would create an invalid 2x2 block
                    if has_filled_2x2_block_after(coords, board, piece):
                        print(f"[DEBUG] ❌ Skipping action: {piece} at {coords} — 2x2 block would be created.")
                        continue

                    # Simulate the board state after placing the piece
                    new_matrix = [row[:] for row in board.matrix]
                    for r, c in coords:
                        new_matrix[r][c] = piece

                    temp_board = Board(new_matrix, board.region_map)
                    temp_board.region_filled = board.region_filled.copy()
                    temp_board.region_filled[str(region_id)] = True

                    # Reject if it causes duplicate adjacent pieces across regions
                    if has_duplicate_adjacent_pieces(temp_board):
                        print(f"[DEBUG] ❌ Skipping action: {piece} at {coords} — causes adjacent duplicate.")
                        continue

                    # Reject if it blocks another region from being completed
                    if any(
                        is_region_blocked(rid, temp_board.regions[rid], temp_board)
                        for rid in temp_board.regions
                        if not is_region_filled(rid, temp_board)
                    ):
                        print(f"[DEBUG] ❌ Skipping action: {piece} at {coords} — blocks another region.")
                        continue

                    connects = connects_to_existing(coords, board)
                    if connects or not has_existing_pieces:
                        connected_actions.append((region_id, piece, orientation, coords))
                    else:
                        disconnected_actions.append((region_id, piece, orientation, coords))

        return disconnected_actions + connected_actions



    def result(self, state, action):
        from copy import deepcopy
        region_id, piece, _, coords = action
        new_matrix = deepcopy(state.board.matrix)
        for r, c in coords:
            new_matrix[r][c] = piece
        new_board = Board(new_matrix, deepcopy(state.board.region_map))
        new_board.region_filled = state.board.region_filled.copy()
        new_board.region_filled[str(region_id)] = True
        return NuruominoState(new_board)

    def goal_test(self, state):
        board = state.board
        return (is_filled_correctly(board) and
                not has_duplicate_adjacent_pieces(board) and
                is_connected(board) and
                not has_filled_2x2_block(board))

def apply_forced_moves(problem, state):
    changed = True
    while changed:
        changed = False
        board = state.board
        for region_id, region_cells in board.regions.items():
            if is_region_filled(region_id, board):
                continue
            valid_moves = []
            for piece_letter in PIECES:
                for orientation in ORIENTATION_CACHE[piece_letter]:
                    for coords in get_all_valid_coords(orientation, region_cells):
                        if any(board.matrix[r][c] in PIECES for r, c in coords):
                            continue
                        temp_state = problem.result(state, (region_id, piece_letter, orientation, coords))
                        if (not has_filled_2x2_block(temp_state.board) and
                            not has_duplicate_adjacent_pieces(temp_state.board)):
                            valid_moves.append((region_id, piece_letter, orientation, coords))
            if len(valid_moves) == 1:
                region_id, letter, shape, coords = valid_moves[0]
                state = problem.result(state, (region_id, letter, shape, coords))
                changed = True
                break
    return state



def is_region_blocked(region_id, region_cells, board):
    region_set = set(region_cells)

    for piece in PIECES:
        for orientation in ORIENTATION_CACHE[piece]:
            for coords in get_all_valid_coords(orientation, region_cells):
                # Must fit only on empty cells
                if all(board.matrix[r][c] not in PIECES for r, c in coords):
                    if not has_filled_2x2_block_after(coords, board, piece):
                        # 💡 Check for adjacency conflicts *now*, not later
                        new_matrix = [row[:] for row in board.matrix]
                        for r, c in coords:
                            new_matrix[r][c] = piece
                        temp_board = Board(new_matrix, board.region_map)
                        temp_board.region_filled = board.region_filled.copy()
                        temp_board.region_filled[str(region_id)] = True
                        if not has_duplicate_adjacent_pieces(temp_board):
                            return False  # Still possible
    return True  


if __name__ == "__main__":
    board = Board.parse_instance()
    problem = Nuruomino(board)
    s_forced = apply_forced_moves(problem, NuruominoState(board))
    print("📌 Após aplicar movimentos forçados:")
    s_forced.board.print_instance()
    print("\n---")
    problem.initial = s_forced
    goal_node = depth_first_tree_search(problem)
    goal_node.state.board.print_instance()
