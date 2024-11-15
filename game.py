from enum import IntEnum
import random


class Cell(IntEnum):
    FLAG = -2
    UNDISCOVERED = -1
    EMPTY = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    EXPOSED_MINE = 9


class MinesweeperGame:
    # Configuration
    width: int
    height: int
    mine_count: int
    # State
    generated: bool
    grid: list[Cell]
    mines: list[bool]

    def __init__(self, width: int, height: int, mine_count: int):
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.clear_grid()

    def clear_grid(self):
        grid_length = self.width * self.width
        self.grid = [Cell.UNDISCOVERED] * grid_length
        self.mines = [False] * grid_length
        self.generated = False

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_size(self) -> tuple[int, int]:
        return self.get_width(), self.get_height()

    def get_mine_count(self) -> int:
        return self.mine_count

    def get_grid(self) -> list[Cell]:
        return self.grid

    def get_mines(self) -> list[bool]:
        return self.mines

    def in_bounds(self, x: int, y: int) -> bool:
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def assert_in_bounds(self, x: int, y: int):
        if not self.in_bounds(x, y):
            raise ValueError("Illegal cell coordinate")

    def get_cell(self, x: int, y: int) -> int:
        self.assert_in_bounds(x, y)
        return self.grid[y * self.width + x]

    def get_mine(self, x: int, y: int) -> int:
        self.assert_in_bounds(x, y)
        return self.mines[y * self.width + x]

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

    def get_neighbours(self, x: int, y: int) -> list[int]:
        return [self.get_cell(*coord) for coord in self.get_neighbour_coordinates(x, y)]

    def get_mine_neighbour_count(self, x: int, y: int) -> int:
        return [
            self.get_mine(*coord) for coord in self.get_neighbour_coordinates(x, y)
        ].count(True)

    def count_mines(self) -> int:
        return self.mines.count(True)

    def generate(self, start_x: int, start_y: int):
        while self.count_mines() < self.mine_count:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.get_mine(x, y):
                continue
            if x == start_x and y == start_y:
                continue


class Difficulty(IntEnum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4


def start_game(difficulty: Difficulty) -> MinesweeperGame:
    if difficulty == Difficulty.EXPERT:
        return MinesweeperGame(40, 20, 150)
    elif difficulty == Difficulty.HARD:
        return MinesweeperGame(30, 16, 99)
    elif difficulty == Difficulty.MEDIUM:
        return MinesweeperGame(16, 16, 10)
    else:
        return MinesweeperGame(8, 8, 10)
