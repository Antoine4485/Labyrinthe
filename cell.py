from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap


class Cell:
    START_LETTER = "D"
    FINISH_LETTER = "A"
    PATH_VALUE = 0
    WALL_VALUE = 1
    START_VALUE = 2
    FINISH_VALUE = 3
    AUTHORISED_VALUES = (PATH_VALUE, WALL_VALUE, START_VALUE, FINISH_VALUE)
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"
    NORTH_EAST = NORTH + EAST
    SOUTH_EAST = SOUTH + EAST
    SOUTH_WEST = SOUTH + WEST
    NORTH_WEST = NORTH + WEST
    STRAIGHT_WAYS = {NORTH, EAST, SOUTH, WEST}
    DIAGONAL_WAYS = {NORTH_EAST, SOUTH_EAST, SOUTH_WEST, NORTH_WEST}
    WALL_IMG = "mur.webp"
    STONE_IMG = "caillou.png"

    def __init__(self, row_id: int, col_id: int, value: int):
        self.row_id = row_id
        self.col_id = col_id
        self.value = value
        # les cases avec "authorisation" à False sont celles où on ne peut pas aller, c'est-à-dire celles où il y a un
        # mur ou un caillou. Les cailloux sont éventuellement ajoutés pendant le parcours sur les cases situées dans
        # les culs-de-sacs, en bordure de grille ou dans "coin ouvert" (deux murs à 90° avec la case
        # opposée dans la diagonale qui est vide. Elle doit être vide afin de ne pas créer un cul-de-sac)
        self.authorisation = False if value == Cell.WALL_VALUE else True
        self.label = self._get_label_by_value(value)
        self.way = ""
        self.left_way = ""
        self.right_way = ""

    def _get_label_by_value(self, value: int) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel()

        match value:
            case self.START_VALUE:
                label.setText(self.START_LETTER)
            case self.FINISH_VALUE:
                label.setText(self.FINISH_LETTER)
            case self.WALL_VALUE:
                label.setPixmap(QPixmap(self.WALL_IMG))

        return label

    def get_straight_positions_by_ways(self):
        return {
            self.NORTH: (self.row_id - 1, self.col_id),
            self.EAST: (self.row_id, self.col_id + 1),
            self.SOUTH: (self.row_id + 1, self.col_id),
            self.WEST: (self.row_id, self.col_id - 1)
        }

    def get_diagonal_positions_by_ways(self):
        return {
            self.NORTH_EAST: (self.row_id - 1, self.col_id + 1),
            self.SOUTH_EAST: (self.row_id + 1, self.col_id + 1),
            self.SOUTH_WEST: (self.row_id + 1, self.col_id - 1),
            self.NORTH_WEST: (self.row_id - 1, self.col_id - 1)
        }



    # def _get_left_and_right_ways(self) -> tuple:
    #     match self.way:
    #         case "N":
    #             return "O", "E"
    #         case "E":
    #             return "N", "S"
    #         case "S":
    #             return "E", "O"
    #         case "O":
    #             return "S", "N"
    #         case _:
    #             return ()