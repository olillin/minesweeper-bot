import pygame

from game import Cell, Difficulty, MinesweeperGame, State, new_game
from screen import MinesweeperScreen

DIFFICULTY = Difficulty.HARD


def all_coordinates_spiral(
    game: MinesweeperGame, previous_x: int, previous_y: int
) -> list[tuple[int, int]]:
    step = 1
    coords: list[tuple[int, int]] = []
    in_bounds = True
    pointer_x: int = 0
    pointer_y: int = 0

    def add_coord(x: int, y: int):
        nonlocal in_bounds, pointer_x, pointer_y
        if game.in_bounds(x, y):
            coords.append((x, y))
            in_bounds = True
        pointer_x, pointer_y = x, y

    while in_bounds:
        in_bounds = False
        for _ in range(step):
            add_coord(pointer_x, pointer_y + 1)
        for _ in range(step):
            add_coord(pointer_x + 1, pointer_y)
        step += 1
        for _ in range(step):
            add_coord(pointer_x, pointer_y - 1)
        for _ in range(step):
            add_coord(pointer_x - 1, pointer_y)
        step += 1

    return coords


def can_easy_dig(game: MinesweeperGame, x: int, y: int) -> bool:
    cell = game.get_cell(x, y)
    neighbours = game.get_neighbours(x, y)
    undiscovered_neighbours = neighbours.count(Cell.UNDISCOVERED)
    flag_neighbours = neighbours.count(Cell.FLAG)

    mine_count = int(cell)

    return (
        cell >= Cell.ONE
        and cell <= Cell.EIGHT
        and flag_neighbours == mine_count
        and undiscovered_neighbours > 0
    )


def can_easy_flag(game: MinesweeperGame, x: int, y: int) -> bool:
    cell = game.get_cell(x, y)
    neighbours = game.get_neighbours(x, y)
    undiscovered_neighbours = neighbours.count(Cell.UNDISCOVERED)
    flag_neighbours = neighbours.count(Cell.FLAG)

    mine_count = int(cell)

    return (
        cell >= Cell.ONE
        and cell <= Cell.EIGHT
        and flag_neighbours + undiscovered_neighbours == mine_count
        and undiscovered_neighbours > 0
    )


def get_chained_flag(game: MinesweeperGame, x: int, y: int) -> tuple[int, int] | None:
    cell = game.get_cell(x, y)
    if cell < Cell.ONE or cell > Cell.EIGHT:
        return

    neighbour_coords = game.get_neighbour_coordinates(x, y)
    unflagged = game.get_unflagged_mine_neighbour_count(x, y)
    for nx, ny in neighbour_coords:
        cell1 = game.get_cell(nx, ny)
        if cell1 < Cell.ONE or cell1 > Cell.EIGHT:
            continue

        delta1 = [
            coord
            for coord in set(game.get_neighbour_coordinates(nx, ny)).difference(
                game.get_neighbour_coordinates(x, y)
            )
            if game.get_cell(*coord) == Cell.UNDISCOVERED
        ]
        delta2 = [
            coord
            for coord in set(game.get_neighbour_coordinates(x, y)).difference(
                game.get_neighbour_coordinates(nx, ny)
            )
            if game.get_cell(*coord) == Cell.UNDISCOVERED
        ]

        if len(delta2) == 0 and len(delta1) == 1 and unflagged == 1:
            print(
                f"Chained debug: ({x}, {y}), n({nx}, {ny}), unflagged {unflagged}, delta1{delta1}"
            )
            return delta1[0]


def make_next_move(
    game: MinesweeperGame, previous_x: int, previous_y: int
) -> tuple[int, int]:
    coords = all_coordinates_spiral(game, previous_x, previous_y)
    for x, y in coords:
        if can_easy_dig(game, x, y):
            game.dig(x, y)
            return x, y
        if can_easy_flag(game, x, y):
            game.flag(x, y)
            return x, y
        chained = get_chained_flag(game, x, y)
        if chained is not None:
            game.flag(*chained)
            return chained

    return previous_x, previous_y


def main():
    # Start game
    game = new_game(DIFFICULTY)

    # Start pygame and screen
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Minesweeper: Bot")
    screen = MinesweeperScreen(game, cell_size=30)

    # Main loop
    x, y = 0, 0
    screen.draw()
    while True:
        if screen.get_quit():
            break

        if game.state == State.PLAYING:
            x, y = make_next_move(game, x, y)

        click = screen.get_click()
        if click:
            click_x, click_y, _ = click
            if game.state == State.UNGENERATED:
                screen.start_timer()
                x = click_x
                y = click_y
                game.dig(x, y)
            elif game.state == State.LOST or game.state == State.WON:
                game = new_game(DIFFICULTY)
                screen.game = game
                screen.reset_timer()

        # End game
        if game.state == State.LOST or game.state == State.WON:
            screen.end_game()

        screen.draw()

        clock.tick(10)


if __name__ == "__main__":
    main()
