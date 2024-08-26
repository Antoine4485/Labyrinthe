from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel


class Label(QLabel):
    __START_LETTER = "D"
    __FINISH_LETTER = "A"
    __IMG_DIR = Path(__file__).parent / "img"
    __WALL_IMG = "wall.webp"
    __STONE_IMG = "stone.png"
    __PERSON_IMG = "person.png"
    __BG_COLOR_OF_CELL_IN_PATH = "rgb(200, 200, 200)"
    __DEFAULT_BG_COLOR = "none"

    def __init__(self):
        super().__init__()

    def set_start_letter(self):
        self.setText(self.__START_LETTER)

    def set_finish_letter(self):
        self.setText(self.__FINISH_LETTER)

    def set_wall_img(self):
        self.setPixmap(QPixmap(Path(self.__IMG_DIR) / self.__WALL_IMG))

    def set_stone_img(self):
        self.setPixmap(QPixmap(Path(self.__IMG_DIR) / self.__STONE_IMG))

    def set_person_img(self):
        self.setPixmap(QPixmap(Path(self.__IMG_DIR) / self.__PERSON_IMG))

    def remove_img(self):
        self.setPixmap(QPixmap())

    def set_bg_color_of_cell_in_path(self):
        self.setStyleSheet(f"background-color:{self.__BG_COLOR_OF_CELL_IN_PATH};")

    def set_default_bg_color(self):
        self.setStyleSheet(f"background-color:{self.__DEFAULT_BG_COLOR};")