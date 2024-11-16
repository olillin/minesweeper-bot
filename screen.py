from typing import TypedDict, cast
import pygame
from pygame import Surface
from pygame.font import Font

from game import Cell, MinesweeperGame, State

Color = str


class Colors(TypedDict, total=True):
    background: Color
    dug: Color
    text: Color
    mine: Color
    flower: Color
    flag: Color


DEFAULT_COLORS: Colors = {
    "background": "pink",
    "dug": "#222222",
    "text": "#eeeeee",
    "mine": "red",
    "flower": "#ff00ff",
    "flag": "#45bb9d",
}


class MinesweeperScreen:
    game: MinesweeperGame
    screen: Surface

    cell_size: int
    screen_width: int
    screen_height: int

    colors: Colors
    font: Font

    def __init__(
        self,
        game: MinesweeperGame,
        cell_size: int = 48,
        colors: Colors = DEFAULT_COLORS,
    ):
        self.game = game

        self.cell_size = cell_size
        self.screen_width = cell_size * game.get_width()
        self.screen_height = cell_size * game.get_height()

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.colors = colors
        self.font = Font("Sono-Bold.ttf", cell_size)

    def get_click(self) -> tuple[int, int, bool] | None:
        """Get the clicked cell and if it was a right click, or `None` if no cell was clicked since the last call"""

        mouse_down_events = pygame.event.get(pygame.MOUSEBUTTONDOWN)
        if len(mouse_down_events) > 0:
            pixel_x, pixel_y = pygame.mouse.get_pos()
            cell_x, cell_y = pixel_x // self.cell_size, pixel_y // self.cell_size
            right_click = pygame.mouse.get_pressed()[2]
            return cell_x, cell_y, right_click

    def get_quit(self) -> bool:
        """Get if an exit has occurred"""
        return len(pygame.event.get(pygame.QUIT)) > 0

    def draw(self):
        """Draw the game to the screen"""

        # Colors
        (
            background_color,
            dug_color,
            text_color,
            mine_color,
            flower_color,
            flag_color,
        ) = (cast(Color, self.colors[k]) for k in self.colors.keys())

        # Draw background
        self.screen.fill(background_color)

        # Draw cells
        for x, y in self.game.get_all_coordinates():
            cell = self.game.get_cell(x, y)

            def draw_cell(color: Color, text: str | None = None):
                pixel_x = x * self.cell_size
                pixel_y = y * self.cell_size
                pygame.draw.rect(
                    self.screen,
                    color,
                    rect=(
                        pixel_x + 1,
                        pixel_y + 1,
                        self.cell_size - 2,
                        self.cell_size - 2,
                    ),
                    border_radius=2,
                )
                if text is not None:
                    label = self.font.render(text, True, text_color)
                    rect = label.get_rect()
                    rect.center = (
                        pixel_x + self.cell_size // 2,
                        pixel_y + self.cell_size // 2,
                    )
                    self.screen.blit(label, rect)

            if cell == Cell.FLAG:
                draw_cell(flag_color)
            elif cell == Cell.EXPOSED_MINE:
                if self.game.state == State.LOST:
                    draw_cell(mine_color)
                elif self.game.state == State.WON:
                    draw_cell(flower_color)
                else:
                    raise ValueError("Illegal state")
            elif cell == Cell.ZERO:
                draw_cell(dug_color)
            elif cell >= Cell.ONE and cell <= Cell.EIGHT:
                draw_cell(dug_color, str(cell))

        # Flush to screen
        pygame.display.flip()
