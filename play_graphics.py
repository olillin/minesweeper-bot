import pygame

from game import Difficulty, State, new_game
from screen import MinesweeperScreen

DIFFICULTY = Difficulty.EASY


def main():
    # Start game
    game = new_game(DIFFICULTY)

    # Start pygame and screen
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Minesweeper: Play")
    screen = MinesweeperScreen(game, cell_size=60)

    # Main loop
    screen.draw()
    while True:
        if screen.get_quit():
            break

        click = screen.get_click()
        if click is not None:
            click_x, click_y, right_click = click

            if game.state == State.LOST or game.state == State.WON:
                game = new_game(DIFFICULTY)
                screen.game = game
                changed = True
            elif right_click:
                changed = game.flag(click_x, click_y)
            else:
                changed = game.dig(click_x, click_y)

            if changed:
                screen.draw()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
