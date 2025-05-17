# nuruomino.py: Template para implementação do projeto de Inteligência Artificial 2024/2025.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2
from search import Problem, Node, depth_first_tree_search, astar_search
from helpers import *

PIECES = {
    'L': [
        [1, 0],
        [1, 0],
        [1, 1]
    ],
    'I': [
        [1],
        [1],
        [1],
        [1]
    ],
    'T': [
        [1, 1, 1],
        [0, 1, 0]
    ],
    'S': [
        [0, 1, 1],
        [1, 1, 0]
    ]
}


class NuruominoState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NuruominoState.state_id
        NuruominoState.state_id += 1

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro do Puzzle Nuruomino."""

    def __init__(self, matrix, region_map=None):
        self.matrix = matrix
        self.size = len(matrix)
        self.region_map = region_map if region_map is not None else [[cell for cell in row] for row in matrix]
        self.regions = self._build_regions()
        self.region_filled = {region_id: False for region_id in self.regions}

    def _build_regions(self):
        from collections import defaultdict
        regions = defaultdict(list)
        for r in range(self.size):
            for c in range(self.size):
                region_id = self.region_map[r][c]  # usar o mapa original
                regions[region_id].append((r, c))
        return regions

    def adjacent_regions(self, region:int) -> list:
        """Devolve uma lista das regiões que fazem fronteira com a região enviada no argumento."""
        
        result = set()
        for (r, c) in self.regions[str(region)]:
            for nr, nc in self.adjacent_positions(r, c):
                neighbor_region = self.region_map[nr][nc]
                if neighbor_region != str(region):
                    result.add(int(neighbor_region))
        return sorted(result)
    
    def adjacent_positions(self, row:int, col:int) -> list:
        """Devolve as posições adjacentes à região, em todas as direções, incluindo diagonais."""
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]
        adj = []
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.size and 0 <= c < self.size:
                adj.append((r, c))
        return adj

    def adjacent_values(self, row:int, col:int) -> list:
        """Devolve os valores das celulas adjacentes à região, em todas as direções, incluindo diagonais."""
        return [self.matrix[r][c] for r, c in self.adjacent_positions(row, col)]
    
    def get_value(self, row, col):
        return self.matrix[row][col]

    
    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        from sys import stdin
        board = []
        for line in stdin:
            row = line.strip().split()
            board.append(row)
        return Board(board)  

    def print_instance(self):
        for row in self.matrix:
            print("\t".join(str(cell) for cell in row))

    # TODO: outros metodos da classe Board

class Nuruomino(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        """Guarda o estado inicial baseado no tabuleiro."""
        self.initial = NuruominoState(board)

    def actions(self, state: NuruominoState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        board = state.board
        actions = []

        for region_id, region_cells in board.regions.items():
            if is_region_filled(region_id, board):
                continue  # região já está ocupada

            for piece_letter, base_shape in PIECES.items():
                for orientation in get_all_orientations(base_shape):
                    all_coords = get_all_valid_coords(orientation, region_cells)
                    for coords in all_coords:
                        try:
                            temp_state = self.result(state, (region_id, piece_letter, orientation, coords))
                            print("\n verificação de ação:")
                            temp_state.board.print_instance()
                            print("\n---")
                            if not has_filled_2x2_block(temp_state.board):
                                actions.append((region_id, piece_letter, orientation, coords))
                                print(f"Adicionada ação: {region_id}, {piece_letter}, {orientation}, {coords}")
                        except:
                            continue

        return actions

    def result(self, state: NuruominoState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        print(f"Aplicar ação: {action}")

        from copy import deepcopy
        region_id, piece_letter, shape, coords = action

        new_matrix = deepcopy(state.board.matrix)
        new_region_map = deepcopy(state.board.region_map)

        for r, c in coords:
            new_matrix[r][c] = piece_letter

        new_board = Board(new_matrix, new_region_map)
        new_board.region_filled = state.board.region_filled.copy()
        new_board.region_filled[str(region_id)] = True

        return NuruominoState(new_board)

        

    def goal_test(self, state: NuruominoState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        board = state.board

        result = (
            is_filled_correctly(state.board) and
            not has_duplicate_adjacent_pieces(state.board) and
            is_connected(state.board) and
            not has_filled_2x2_block(state.board)
        )
        print("🎯 Goal test:", result)
        return result

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

def apply_forced_moves(problem, state):
    changed = True
    while changed:
        changed = False
        board = state.board

        for region_id, region_cells in board.regions.items():
            if is_region_filled(region_id, board):
                continue

            valid_moves = []
            for piece_letter, shape in PIECES.items():
                for orientation in get_all_orientations(shape):
                    for coords in get_all_valid_coords(orientation, region_cells):
                        valid_moves.append((region_id, piece_letter, orientation, coords))
                        print(f"Adicionada ação: {region_id}, {piece_letter}, {orientation}, {coords}")

            if len(valid_moves) == 1:
                region_id, letter, shape, coords = valid_moves[0]
                print(f"✅ Movimento forçado: Região {region_id} recebe {letter}")
                state = problem.result(state, (region_id, letter, shape, coords))
                changed = True
                break  # recomeça do zero porque o tabuleiro mudou

    return state



if __name__ == "__main__":
    board = Board.parse_instance()
    print(board.adjacent_regions(1))
    print(board.adjacent_regions(3))
    print(board.adjacent_values(0,0))

    problem = Nuruomino(board)

    s0 = NuruominoState(board)

    print("📄 Estado inicial:")
    s0.board.print_instance()
    print("\n---")

    s_forced = apply_forced_moves(problem, s0)

    print("📌 Após aplicar movimentos forçados:")
    s_forced.board.print_instance()
    print("\n---")

    problem.initial = s_forced

    #"""
    goal_node = depth_first_tree_search(problem)

    print("Solution:")
    goal_node.state.board.print_instance()

    #"""






