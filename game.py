from enum import IntEnum
import random
from typing import cast


class Cell(IntEnum):
    FLAG = -2
    UNDISCOVERED = -1
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    EXPOSED_MINE = 9


class State(IntEnum):
    UNGENERATED = 0
    PLAYING = 1
    LOST = 2
    WON = 3


class MinesweeperGame:
    # Configuration
    width: int
    height: int
    mine_count: int
    # State
    state: State
    cells: list[Cell]
    mines: list[bool]

    def __init__(self, width: int, height: int, mine_count: int):
        self.state = State.UNGENERATED
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.clear()

    def clear(self):
        cells_length = self.width * self.width
        self.cells = [Cell.UNDISCOVERED] * cells_length
        self.mines = [False] * cells_length
        self.generated = False

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_size(self) -> tuple[int, int]:
        return self.get_width(), self.get_height()

    def get_cell_count(self) -> int:
        return self.width * self.height

    def get_state(self) -> State:
        return self.state

    def get_mine_count(self) -> int:
        return self.mine_count

    def get_cells(self) -> list[Cell]:
        return self.cells

    def get_mines(self) -> list[bool]:
        return self.mines

    def in_bounds(self, x: int, y: int) -> bool:
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def assert_in_bounds(self, x: int, y: int):
        if not self.in_bounds(x, y):
            raise ValueError("Illegal cell coordinate")

    def get_cell(self, x: int, y: int) -> Cell:
        self.assert_in_bounds(x, y)
        return self.cells[y * self.width + x]

    def _set_cell(self, x: int, y: int, cell: Cell):
        self.assert_in_bounds(x, y)
        self.cells[y * self.width + x] = cell

    def is_mine(self, x: int, y: int) -> int:
        self.assert_in_bounds(x, y)
        return self.mines[y * self.width + x]

    def _set_mine(self, x: int, y: int, mine: bool):
        self.assert_in_bounds(x, y)
        self.mines[y * self.width + x] = mine

    def get_neighbour_coordinates(self, x: int, y: int) -> list[tuple[int, int]]:
        self.assert_in_bounds(x, y)
        offsets = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
        ]
        coords: list[tuple[int, int]] = []
        for dx, dy in offsets:
            coord = x + dx, y + dy
            if self.in_bounds(*coord):
                coords.append(coord)

        return coords

    def get_neighbours(self, x: int, y: int) -> list[Cell]:
        return [self.get_cell(*coord) for coord in self.get_neighbour_coordinates(x, y)]

    def get_mine_neighbour_count(self, x: int, y: int) -> int:
        return [
            self.is_mine(*coord) for coord in self.get_neighbour_coordinates(x, y)
        ].count(True)

    def get_all_coordinates(self) -> list[tuple[int, int]]:
        return [(x, y) for y in range(self.height) for x in range(self.width)]

    def count_mines(self) -> int:
        return self.mines.count(True)

    def count_flags(self) -> int:
        return self.cells.count(Cell.FLAG)

    def get_remaining_mines(self) -> int:
        return self.mine_count - self.count_flags()

    def generate(self, start_x: int, start_y: int):
        while self.count_mines() < self.mine_count:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            if self.is_mine(x, y):
                continue
            if abs(x - start_x) <= 1 and abs(y - start_y) <= 1:
                continue

            self._set_mine(x, y, True)

        self.state = State.PLAYING

    def dig(self, x: int, y: int) -> bool:
        """Dig a cell and returns whether anything changed"""
        if self.state == State.UNGENERATED:
            self.generate(x, y)

        cell = self.get_cell(x, y)
        if cell != Cell.UNDISCOVERED:
            # Easy digging
            if cell >= Cell.ONE and cell <= Cell.EIGHT:
                neighbours = self.get_neighbours(x, y)
                undiscovered_neighbours = neighbours.count(Cell.UNDISCOVERED)
                flag_neighbours = neighbours.count(Cell.FLAG)

                mine_count = int(cell)
                if flag_neighbours == mine_count and undiscovered_neighbours > 0:
                    for nx, ny in self.get_neighbour_coordinates(x, y):
                        if self.get_cell(nx, ny) == Cell.UNDISCOVERED:
                            self.dig(nx, ny)
                    return True
            return False

        if self.is_mine(x, y):
            self.lose()
        else:
            self._show(x, y)

        if self.has_won():
            self.win()

        self._expand_zeros()

        return True

    def _expand_zeros(self):
        done = False
        while not done:
            done = True
            for x in range(self.width):
                for y in range(self.height):
                    if self.get_cell(x, y) == Cell.UNDISCOVERED:
                        neighbours = self.get_neighbour_coordinates(x, y)
                        for nx, ny in neighbours:
                            if self.get_cell(nx, ny) == Cell.ZERO:
                                self._show(x, y)
                                done = False
                                break

    def _show(self, x: int, y: int) -> Cell:
        """Shows a cell and returns its state"""
        self.assert_in_bounds(x, y)

        if self.is_mine(x, y):
            cell = Cell.EXPOSED_MINE
        else:
            mine_count = self.get_mine_neighbour_count(x, y)
            cell = cast(Cell, mine_count)
        self._set_cell(x, y, cell)
        return cell

    def flag(self, x: int, y: int) -> bool:
        """Attempt to place or remove a flag and return if anything changed"""

        cell = self.get_cell(x, y)

        if self.state == State.UNGENERATED:
            return False

        if cell == Cell.UNDISCOVERED:
            self._set_cell(x, y, Cell.FLAG)
        elif cell == Cell.FLAG:
            self._set_cell(x, y, Cell.UNDISCOVERED)
        else:
            # Easy flagging
            if cell >= 1 and cell <= 8:
                neighbours = self.get_neighbours(x, y)
                undiscovered_neighbours = neighbours.count(Cell.UNDISCOVERED)
                flag_neighbours = neighbours.count(Cell.FLAG)

                mine_count = int(cell)
                if (
                    flag_neighbours + undiscovered_neighbours == mine_count
                    and undiscovered_neighbours > 0
                ):
                    for nx, ny in self.get_neighbour_coordinates(x, y):
                        if self.get_cell(nx, ny) == Cell.UNDISCOVERED:
                            self.flag(nx, ny)
                    return True
            return False
        return True

    def has_won(self) -> bool:
        exposed_cells: int = sum(
            [cell >= Cell.ZERO and cell <= Cell.EIGHT for cell in self.cells]
        )
        return self.get_cell_count() - exposed_cells == self.mine_count

    def win(self):
        self.state = State.WON
        self.end_game()

    def lose(self):
        self.state = State.LOST
        self.end_game()

    def end_game(self):
        for i in range(len(self.cells)):
            if self.mines[i]:
                self.cells[i] = Cell.EXPOSED_MINE


class Difficulty(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4


def new_game(difficulty: Difficulty) -> MinesweeperGame:
    if difficulty == Difficulty.EXPERT:
        return MinesweeperGame(40, 20, 150)
    elif difficulty == Difficulty.HARD:
        return MinesweeperGame(30, 16, 99)
    elif difficulty == Difficulty.MEDIUM:
        return MinesweeperGame(15, 12, 50)
    else:
        return MinesweeperGame(8, 8, 10)
