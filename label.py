from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel


class Label(QLabel):
    __START_LETTER = "D"
    __FINISH_LETTER = "A"
    __PERSON_LETTER = "X"
    __IMG_DIR = "img"
    __WALL_IMG = "mur.webp"
    __STONE_IMG = "caillou.png"
    __BG_COLOR_OF_CELL_IN_PATH = "rgba(150, 150, 150, 0.5)"
    __BG_COLOR_OF_CELL_NOT_IN_PATH = "none"

    def __init__(self):
        super().__init__()

    def set_start_letter(self):
        self.setText(self.__START_LETTER)

    def set_finish_letter(self):
        self.setText(self.__FINISH_LETTER)

    def set_person_letter(self):
        self.setText(self.__PERSON_LETTER)

    def set_bg_color_of_cell_in_path(self):
        self.setStyleSheet(f"background-color:{self.__BG_COLOR_OF_CELL_IN_PATH};")

    def set_bg_color_of_cell_not_in_path(self):
        self.setStyleSheet(f"background-color:{self.__BG_COLOR_OF_CELL_NOT_IN_PATH};")

    def set_wall_img(self):
        self.setPixmap(QPixmap(Path(self.__IMG_DIR) / self.__WALL_IMG))

    def set_stone_img(self):
        self.setPixmap(QPixmap(Path(self.__IMG_DIR) / self.__STONE_IMG))