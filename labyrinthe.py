import random
import sys
import threading
import time
from pathlib import Path

from PySide6 import QtWidgets as QtW, QtCore
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QAction, QIcon
#from PySide6.QtWidgets import QLabel, QWidget, QGridLayout, QMainWindow

from cell import Cell


class Labyrinth(QtW.QMainWindow):
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
    __WITHOUT_PATH_DISPLAY = "Aucun"
    __SHORT_PATH_DISPLAY = "Court"
    __TOTAL_PATH_DISPLAY = "Long"
    __LBL_PLAY = "Play"
    __LBL_PAUSE = "Pause"

    def __init__(self, grid: list[list[int]]):
        super().__init__()
        self.__is_running = False
        self.__path_display = self.__TOTAL_PATH_DISPLAY
        self.__display_window()
        self.__display_grid(grid)

    def __init_grid(self, grid: list[list[int]]):
        self.__grid = []
        self.__total_path = []
        self.__short_path = []
        self.__start_cell: None | Cell = None
        self.__finish_cell: None | Cell = None
        self.__current_cell: None | Cell = None
        if not self.__set_grid(grid):
            exit()
        self.__nb_rows_grid = len(self.__grid)
        self.__nb_cols_grid = len(self.__grid[0])
        self.__init_cells_around_cells()

    def __set_grid(self, grid: list[list[int]]) -> bool:
        if type(grid) is not list:
            return False
        for row_id, row in enumerate(grid):
            if type(row) is not list:
                return False
            self.__grid.append([])
            for col_id, value in enumerate(row):
                if type(value) is not int or value not in self.__AUTHORISED_VALUES:
                    return False

                # les cases avec "authorisation" à False sont celles où on ne peut pas aller car il y a un mur ou un
                # caillou dessus. Ces derniers sont éventuellement ajoutés pendant le parcours sur les cases situées
                # dans les culs-de-sacs, en bordure de grille ou dans un "coin ouvert" (deux murs à 90° avec la case
                # opposée dans la diagonale qui est vide afin de ne pas créer un cul-de-sac)
                cell = Cell(row_id=row_id,
                            col_id=col_id,
                            value=value,
                            authorisation=False if value == self.__WALL_VALUE else True,
                            label=self.__get_label_by_value(value))

                self.__grid[row_id].append(cell)

                if value == self.__START_VALUE:
                    self.__start_cell = cell
                elif value == self.__FINISH_VALUE:
                    self.__finish_cell = cell

        return True

    def __get_label_by_value(self, value: int) -> QtW.QLabel:
        label = QtW.QLabel()
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
        next_cell = self.__start_cell
        while next_cell:
            self.__add_cell(next_cell)
            print(self.__current_cell.row_id, self.__current_cell.col_id)
            next_cell = self.__get_next_cell()
        self.__is_running = False

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

    def __add_cell(self, cell: Cell):
        time.sleep(self.__TIMER_DELAY)
        cell.prec_cell = self.__current_cell
        if self.__path_display != self.__WITHOUT_PATH_DISPLAY:
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
        if self.__path_display != self.__TOTAL_PATH_DISPLAY:
            cell.label.setStyleSheet(f"background-color:{self.__BG_COLOR_OF_CELL_NOT_IN_PATH};")

    def __display_window(self):
        self.setWindowTitle(self.__WINDOW_TITLE)
        # pour empêcher que la fenêtre prenne tout l'écran si fait un double-clic dessus
        self.setMaximumSize(50, 50)
        toolbar = self.addToolBar("")

        comboBox = QtW.QComboBox()
        comboBox.addItems([self.__WITHOUT_PATH_DISPLAY, self.__SHORT_PATH_DISPLAY, self.__TOTAL_PATH_DISPLAY])
        comboBox.setCurrentText(self.__path_display)
        comboBox.currentTextChanged.connect(self.comboBox_pathDisplaySlot)
        toolbar.addWidget(comboBox)

        buttonPlay = QtW.QPushButton(self.__LBL_PLAY)
        buttonPlay.clicked.connect(self.button_playSlot)
        toolbar.addWidget(buttonPlay)

    def __display_grid(self, grid: list[list[int]]):
        self.__init_grid(grid)
        gridLayout = QtW.QGridLayout()
        gridLayout.setSpacing(0)
        label_size = 30

        for i in range(self.__nb_rows_grid):
            for j in range(self.__nb_cols_grid):
                if i == 0:
                    label = QtW.QLabel(str(j))
                    label.setFixedSize(label_size, label_size)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    gridLayout.addWidget(label, i, j + 1)
                if j == 0:
                    label = QtW.QLabel(str(i))
                    label.setFixedSize(label_size, label_size)
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    gridLayout.addWidget(label, i + 1, j)
                label = self.__grid[i][j].label
                label.setFixedSize(label_size, label_size)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                gridLayout.addWidget(label, i + 1, j + 1)

        centralWidget = QtW.QWidget()
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)

    def __update_styleSheet_path(self):
        for cell in self.__total_path:
            if self.__path_display == self.__WITHOUT_PATH_DISPLAY or \
                    self.__path_display == self.__SHORT_PATH_DISPLAY and cell not in self.__short_path:
                cell.label.setStyleSheet(f"background-color:{self.__BG_COLOR_OF_CELL_NOT_IN_PATH};")
            else:
                cell.label.setStyleSheet(f"background-color:{self.__BG_COLOR_OF_CELL_IN_PATH};")

    @Slot()
    def button_playSlot(self):
        if not self.__is_running:
            self.__display_grid(grid)
            threading.Thread(target=self.__find_the_exit).start()
            self.__is_running = True

    @Slot()
    def comboBox_pathDisplaySlot(self):
        self.__path_display = self.sender().currentText()
        self.__update_styleSheet_path()


if __name__ == '__main__':
    grid = [
        [1, 1, 0, 1, 0, 1, 0, 1, 3, 1],
        [1, 2, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 1, 1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
    ]

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

    # grid = [
    #     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 3],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
    #     [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
    #     [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0]
    # ]

    # Création de l'application
    app = QtW.QApplication(sys.argv)
    qss = "labyrinth"
    #qss = "darkorange"

    with open(f"styles/{qss}.qss", "r") as f:
        #print(f.read())
        app.setStyleSheet(f.read())

    labyrinth = Labyrinth(grid)
    #labyrinth.setStyleSheet(f.read())
    labyrinth.show()
    sys.exit(app.exec())
