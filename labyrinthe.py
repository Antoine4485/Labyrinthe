import random
import sys
import threading
import time
from pathlib import Path

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap

from cell import Cell


class Labyrinth(QtWidgets.QWidget):
    __PATH_VALUE = 0
    __WALL_VALUE = 1
    __START_VALUE = 2
    __FINISH_VALUE = 3
    __AUTHORISED_VALUES = {__PATH_VALUE, __WALL_VALUE, __START_VALUE, __FINISH_VALUE}
    __TIMER_DELAY = 0.2
    __START_LETTER = "D"
    __FINISH_LETTER = "A"
    __PERSON_LETTER = "X"
    __WINDOW_TITLE = "Labyrinthe"
    __IMG_DIR = "img"
    __WALL_IMG = "mur.webp"
    __STONE_IMG = "caillou.png"
    __BG_COLOR_OF_CELL_IN_PATH = "rgba(150, 150, 150, 0.5)"
    __BG_COLOR_OF_CELL_NOT_IN_PATH = "none"

    def __init__(self, grid: list[list[int]]):
        super().__init__()
        if not self.__set_grid(grid):
            exit()
        self.__nb_rows_grid = len(self.__grid)
        self.__nb_cols_grid = len(self.__grid[0])
        self.__total_path = []
        self.__short_path = []
        self.__start_cell: None | Cell = None
        self.__finish_cell: None | Cell = None
        self.__current_cell: None | Cell = None
        self.__init_cells_around_cells()
        self.__show_grid()

    def __set_grid(self, grid: list[list[int]]) -> bool:
        if type(grid) is not list:
            return False
        for row in grid:
            if type(row) is not list:
                return False
            for cell in row:
                if type(cell) is not int or cell not in self.__AUTHORISED_VALUES:
                    return False

        # les cases avec "authorisation" à False sont celles où on ne peut pas aller car il y a un mur ou un caillou
        # dessus. Ces derniers sont éventuellement ajoutés pendant le parcours sur les cases situées dans les
        # culs-de-sacs, en bordure de grille ou dans un "coin ouvert" (deux murs à 90° avec la case opposée dans la
        # diagonale qui est vide afin de ne pas créer un cul-de-sac)
        self.__grid = [[Cell(row_id=row_id,
                             col_id=col_id,
                             value=value,
                             authorisation=False if value == self.__WALL_VALUE else True,
                             label=self.__get_label_by_value(value))
                        for col_id, value in enumerate(row)] for row_id, row in enumerate(grid)]
        return True

    def __get_label_by_value(self, value: int) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel()
        match value:
            case self.__START_VALUE:
                label.setText(self.__START_LETTER)
            case self.__FINISH_VALUE:
                label.setText(self.__FINISH_LETTER)
            case self.__WALL_VALUE:
                label.setPixmap(QPixmap(Path(self.__IMG_DIR) / self.__WALL_IMG))
        return label

    def __init_cells_around_cells(self):
        # Initialisation, autour de chaque case, des cases selon leur direction, afin de pouvoir par la suite accéder
        # facilement par exemple à la case à gauche de celle à gauche de la case courante, ou à la case à droite de
        # celle à droite de la case courante (en faisant cell.left_cell.left_cell ou cell.right_cell.right_cell)
        for row in self.__grid:
            for cell in row:
                self.__current_cell = cell
                self.__current_cell.closest_cells_by_directions = self.__get_closest_cells_by_directions()

    #
    def __get_closest_cells_by_directions(self):
        closest_cells_by_directions = {}

        for direction, pos in self.__current_cell.get_positions_by_directions().items():
            if self.__is_pos_in_grid(pos):
                cell = self.__grid[pos[0]][pos[1]]
                closest_cells_by_directions[direction] = cell

        return closest_cells_by_directions

    def __is_pos_in_grid(self, pos: tuple) -> bool:
        return pos[0] in range(self.__nb_rows_grid) and pos[1] in range(self.__nb_cols_grid)

    def __find_the_exit(self):
        self.__init_start_and_finish_cells()
        next_cell = self.__start_cell
        while next_cell:
            self.__add_cell(next_cell)
            print(self.__current_cell.row_id, self.__current_cell.col_id)
            next_cell = self.__get_next_cell()

    def __get_next_cell(self) -> None | Cell:
        if not self.__current_cell.authorised_next_cells_by_directions or self.__current_cell == self.__finish_cell:
            return None

        authorised_next_cells = list(self.__current_cell.authorised_next_cells_by_directions.values())

        # si la case finale figure parmi celles possibles, on la choisit
        if self.__finish_cell in authorised_next_cells:
            return self.__finish_cell

        # cas où on est sur la case de départ : on choisit une direction au hasard
        if not self.__current_cell.prec_cell:
            return random.choice(authorised_next_cells)

        # On ne va pas à gauche, sauf si on est dans un couloir et qu'un passage apparaît à gauche. De même pour la
        # droite, on ne va pas à droite sauf si une issue apparaît à droite. Cela permet d'aller tout droit la
        # plupart du temps pour arriver plus vite à la fin.
        if self.__current_cell.is_left_cell_to_remove_from_authorised_next_cells():
            authorised_next_cells.remove(self.__current_cell.left_cell)

        if self.__current_cell.is_right_cell_to_remove_from_authorised_next_cells():
            authorised_next_cells.remove(self.__current_cell.right_cell)

        # s'il y a au moins une case possible en plus de la précédente, on ne revient pas sur cette dernière
        if len(authorised_next_cells) > 1 and self.__current_cell.prec_cell in authorised_next_cells:
            authorised_next_cells.remove(self.__current_cell.prec_cell)

        return random.choice(authorised_next_cells)

    def __update_short_path(self, cell: Cell):
        if cell not in self.__short_path:
            self.__short_path.append(cell)
        elif cell == self.__short_path[-2]:
            self.__remove_cell_from_short_path(with_timer_delay=False)
        # quand on est sur une case, si on a fait une boucle, on l'enlève
        self.__remove_possible_loop_from_short_path()

    def __remove_possible_loop_from_short_path(self):
        index_current_cell = min_index_possible_cell = len(self.__short_path) - 1
        cells = self.__current_cell.h_and_v_closest_cells_by_directions.values()

        for cell in cells:
            if cell in self.__short_path:
                index_cell = self.__short_path.index(cell)
                if index_cell < min_index_possible_cell:
                    min_index_possible_cell = index_cell

        if index_current_cell - min_index_possible_cell < 3:
            return

        # on crée une liste de cellules à supprimer car on ne peut pas les supprimer via leur index en bouclant
        # directement sur self.__short_path
        cells_to_remove = []
        for i in range(min_index_possible_cell + 1, index_current_cell):
            cells_to_remove.append(self.__short_path[i])

        for cell in reversed(cells_to_remove):
            self.__remove_cell_from_short_path(cell=cell, with_timer_delay=False)

    def __init_start_and_finish_cells(self):
        for row in self.__grid:
            for cell in row:
                if cell.value == self.__START_VALUE:
                    self.__start_cell = cell
                elif cell.value == self.__FINISH_VALUE:
                    self.__finish_cell = cell
                if self.__start_cell and self.__finish_cell:
                    return

    def __add_cell(self, cell: Cell):
        time.sleep(self.__TIMER_DELAY)
        cell.prec_cell = self.__current_cell
        cell.label.setStyleSheet(f"background-color:{self.__BG_COLOR_OF_CELL_IN_PATH};")
        cell.label.setText(self.__PERSON_LETTER)
        self.__total_path.append(cell)
        self.__current_cell = cell

        # cas où on met un caillou sur la case pour ne pas y revenir
        if self.__current_cell.is_in_cul_de_sac() or self.__current_cell.is_in_open_corner():
            self.__current_cell.authorisation = False

        self.__update_short_path(cell)

        if not cell.prec_cell:
            return
        label = cell.prec_cell.label
        if cell.prec_cell == self.__start_cell:
            label.setText(self.__START_LETTER)
        elif not cell.prec_cell.authorisation:
            label.setPixmap(QPixmap(Path(self.__IMG_DIR) / self.__STONE_IMG))
        else:
            label.setText("")

    def __remove_cell_from_short_path(self, cell: None | Cell = None, with_timer_delay=True):
        if with_timer_delay:
            time.sleep(self.__TIMER_DELAY)
        # s'il n'y a qu'un élément c'est forcément le point de départ, donc on ne l'enlève pas
        if len(self.__short_path) == 1:
            return
        if not cell:
            cell = self.__short_path[-1]
        self.__short_path.remove(cell)
        cell.label.setStyleSheet(f"background-color:{self.__BG_COLOR_OF_CELL_NOT_IN_PATH};")

    def __show_grid(self):
        self.setWindowTitle(self.__WINDOW_TITLE)
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(0)
        group = QtWidgets.QGroupBox()

        for i in range(self.__nb_rows_grid):
            for j in range(self.__nb_cols_grid):
                if i == 0:
                    label = QtWidgets.QLabel(str(j))
                    label.setFixedSize(30, 30)
                    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    grid_layout.addWidget(label, i, j + 1)
                if j == 0:
                    label = QtWidgets.QLabel(str(i))
                    label.setFixedSize(30, 30)
                    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    grid_layout.addWidget(label, i + 1, j)
                label = self.__grid[i][j].label
                label.setFixedSize(30, 30)
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                grid_layout.addWidget(label, i + 1, j + 1)

        group.setLayout(grid_layout)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(group)
        self.setLayout(layout)
        threading.Thread(target=self.__find_the_exit).start()


if __name__ == '__main__':
    # grid = [
    #     [1, 1, 0, 1, 0, 1, 0, 1, 3, 1],
    #     [1, 2, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    #     [1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 0, 1, 0, 0, 1, 1, 1, 1],
    #     [1, 1, 0, 1, 1, 0, 1, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    #     [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
    #     [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
    # ]

    # grid = [
    #     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0, 2, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 3],
    #     [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1],
    #     [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #     [1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
    # ]

    grid = [
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 3],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
        [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0]
    ]

    # Création de l'application
    app = QtWidgets.QApplication([])
    labyrinth = Labyrinth(grid)
    labyrinth.show()
    sys.exit(app.exec())
