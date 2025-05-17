# helpers.py - Funções auxiliares otimizadas para Nuruomino

PIECES = {
    'L': [[1, 0], [1, 0], [1, 1]],
    'I': [[1], [1], [1], [1]],
    'T': [[1, 1, 1], [0, 1, 0]],
    'S': [[0, 1, 1], [1, 1, 0]]
}

def is_filled_correctly(board):
    return all(board.region_filled[region_id] for region_id in board.region_filled)

def is_region_filled(region_id, board):
    return board.region_filled.get(str(region_id), False)

def has_duplicate_adjacent_pieces(board):
    for r in range(board.size):
        for c in range(board.size):
            piece = board.matrix[r][c]

            if piece in PIECES:
                current_region = board.region_map[r][c]

                # Only check orthogonal neighbors
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < board.size and 0 <= nc < board.size:
                        neighbor_piece = board.matrix[nr][nc]
                        neighbor_region = board.region_map[nr][nc]

                        if neighbor_piece == piece and neighbor_region != current_region:
                            print(f"❌ Conflict detected:")
                            print(f"  - Piece '{piece}' at ({r}, {c}) in region {current_region}")
                            print(f"  - Adjacent piece '{neighbor_piece}' at ({nr}, {nc}) in region {neighbor_region}")
                            return True
    return False



def is_connected(board):
    from collections import deque
    filled = [(r, c) for r in range(board.size) for c in range(board.size) if board.matrix[r][c] in PIECES]
    if not filled:
        return False
    queue, visited = deque([filled[0]]), {filled[0]}
    while queue:
        r, c = queue.popleft()
        for nr, nc in board.adjacent_positions(r, c):
            if (nr, nc) not in visited and board.matrix[nr][nc] in PIECES:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return len(visited) == len(filled)



def connects_to_existing(coords, board):
    for r, c in coords:
        for nr, nc in board.adjacent_positions(r, c):
            if board.matrix[nr][nc] in PIECES:
                return True
    return False




def has_filled_2x2_block(board):
    for r in range(board.size - 1):
        for c in range(board.size - 1):
            if all(board.matrix[r+i][c+j] in PIECES for i in range(2) for j in range(2)):
                return True
    return False

def rotate(piece):
    return [list(row) for row in zip(*piece[::-1])]

def flip(piece):
    return [row[::-1] for row in piece]

def matrix_to_tuple(matrix):
    return tuple(tuple(row) for row in matrix)

def get_all_orientations(piece):
    seen, result = set(), []
    current = piece
    for _ in range(4):
        for variant in (current, flip(current)):
            key = matrix_to_tuple(variant)
            if key not in seen:
                seen.add(key)
                result.append(variant)
        current = rotate(current)
    return result

def get_all_valid_coords(shape, region_cells):
    blocks = [(i, j) for i, row in enumerate(shape) for j, v in enumerate(row) if v == 1]
    region_set = set(region_cells)
    results = []
    for base_r, base_c in region_cells:
        dr0, dc0 = blocks[0]
        coords = [(base_r + (dr - dr0), base_c + (dc - dc0)) for dr, dc in blocks]
        if all((r, c) in region_set for r, c in coords):
            results.append(coords)
    return results



def has_filled_2x2_block_after(coords, board, piece_letter):
    """Verifica se a colocação de uma peça criaria um bloco 2x2 inválido."""
    affected = set()
    for r, c in coords:
        for dr in (-1, 0):
            for dc in (-1, 0):
                if 0 <= r+dr < board.size - 1 and 0 <= c+dc < board.size - 1:
                    affected.add((r+dr, c+dc))
    for r, c in affected:
        count = 0
        for i in range(2):
            for j in range(2):
                rr, cc = r+i, c+j
                if (rr, cc) in coords:
                    count += 1
                elif board.matrix[rr][cc] in PIECES:
                    count += 1
        if count == 4:
            print(f"❌ Placing '{piece_letter}' would create 2x2 block at ({r}, {c})")
            return True
    return False