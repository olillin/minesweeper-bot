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
    header_size: int
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

        self.header_size = cell_size
        self.cell_size = cell_size
        self.screen_width = cell_size * game.get_width()
        self.screen_height = cell_size * game.get_height() + self.header_size

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.colors = colors
        self.font = Font("Sono-Bold.ttf", cell_size)

    def pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        return x // self.cell_size, (y - self.header_size) // self.cell_size

    def cell_to_pixel(self, x: int, y: int) -> tuple[int, int]:
        return x * self.cell_size, y * self.cell_size + self.header_size

    def get_click(self) -> tuple[int, int, bool] | None:
        """Get the clicked cell and if it was a right click, or `None` if no cell was clicked since the last call"""

        mouse_down_events = pygame.event.get(pygame.MOUSEBUTTONDOWN)
        if len(mouse_down_events) > 0:
            pixel_x, pixel_y = pygame.mouse.get_pos()
            cell_x, cell_y = self.pixel_to_cell(pixel_x, pixel_y)
            if cell_y < 0:
                return None
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

            if cell == Cell.FLAG:
                self.draw_cell(x, y, flag_color)
                self.draw_flag(x, y, background_color)
            elif cell == Cell.EXPOSED_MINE:
                if self.game.state == State.LOST:
                    self.draw_cell(x, y, mine_color)
                elif self.game.state == State.WON:
                    self.draw_cell(x, y, flower_color)
                else:
                    raise ValueError("Illegal state")
            elif cell == Cell.ZERO:
                self.draw_cell(x, y, dug_color)
            elif cell >= Cell.ONE and cell <= Cell.EIGHT:
                self.draw_cell(x, y, dug_color, str(cell))

        # Draw header

        # Flush to screen
        pygame.display.flip()

    def draw_cell(self, x: int, y: int, background: Color, text: str | None = None):
        pixel_x, pixel_y = self.cell_to_pixel(x, y)
        pygame.draw.rect(
            self.screen,
            background,
            rect=(
                pixel_x + 1,
                pixel_y + 1,
                self.cell_size - 2,
                self.cell_size - 2,
            ),
            border_radius=2,
        )
        if text is not None:
            label = self.font.render(text, True, self.colors["text"])
            rect = label.get_rect()
            rect.center = (
                pixel_x + self.cell_size // 2,
                pixel_y + self.cell_size // 2,
            )
            self.screen.blit(label, rect)

    def draw_flag(self, x: int, y: int, color: Color):
        pixel_x, pixel_y = self.cell_to_pixel(x, y)
        center_x, center_y = (
            pixel_x + self.cell_size // 2,
            pixel_y + self.cell_size // 2,
        )

        def to_absolute(x: float, y: float) -> tuple[int, int]:
            return (
                int(x * self.cell_size // 2 + center_x),
                int(y * self.cell_size // 2 + center_y),
            )

        pygame.draw.line(
            self.screen,
            color,
            to_absolute(-0.25, -0.6),
            to_absolute(-0.25, 0.6),
            width=self.cell_size // 10,
        )
        pygame.draw.polygon(
            self.screen,
            color,
            [
                to_absolute(-0.05, -0.6),
                to_absolute(-0.05, 0.1),
                to_absolute(0.5, -0.25),
            ],
        )
