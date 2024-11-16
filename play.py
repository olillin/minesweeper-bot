from game import Difficulty, MinesweeperGame, State, Cell, new_game
from typing import cast
import re


def get_cell_char(cell: Cell, state: State) -> str:
    match cell:
        case Cell.UNDISCOVERED:
            return "🌱"
        case Cell.ZERO:
            return "  "
        case Cell.FLAG:
            return "🚩"
        case Cell.EXPOSED_MINE:
            if state == State.LOST:
                return "💥"
            elif state == State.WON:
                return "🌺"
            else:
                raise ValueError("Illegal state")
        case _:
            return f"{cell}\ufe0f\u20e3 "


def show_game(game: MinesweeperGame):
    for x in range(game.get_width()):
        print(str(x + 1).ljust(2), end="")
    print()
    for y in range(game.get_height()):
        for x in range(game.get_width()):
            cell = game.get_cell(x, y)
            cell_char = get_cell_char(cell, game.get_state())
            print(cell_char, end="")
        print(f" {y + 1}")


def debug_show_mines(game: MinesweeperGame):
    for y in range(game.get_height()):
        for x in range(game.get_width()):
            cell_char = "X" if game.is_mine(x, y) else "."
            print(cell_char, end="")
        print()


def main():
    # Select difficulty
    difficulty = input("Select difficulty: ")
    if not difficulty.isdigit() or int(difficulty) not in Difficulty:
        print("Invalid difficulty")
        return
    difficulty = cast(Difficulty, int(difficulty))

    # Start game
    game = new_game(difficulty)
    show_game(game)

    # Game loop
    while True:
        try:
            move = input("> ")
            x, y = [int(number) - 1 for number in re.findall(r"\d+", move)]
            if move.startswith("f"):
                game.flag(x, y)
            else:
                game.dig(x, y)
            show_game(game)
            # debug_show_mines(game)
            if game.get_state() != State.PLAYING:
                break
        except ValueError:
            pass

    # Finished
    if game.get_state() == State.WON:
        print("You won! 👑")
    elif game.get_state() == State.LOST:
        print("You lost 👿")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
