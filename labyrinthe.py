import random
import threading
import time

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap

from cell import Cell


class Labyrinth(QtWidgets.QWidget):
    __START_LETTER = "D"
    __FINISH_LETTER = "A"
    __PATH_VALUE = 0
    __WALL_VALUE = 1
    __START_VALUE = 2
    __FINISH_VALUE = 3
    __AUTHORISED_VALUES = {__PATH_VALUE, __WALL_VALUE, __START_VALUE, __FINISH_VALUE}
    __WALL_IMG = "mur.webp"
    __STONE_IMG = "caillou.png"
    __TIMER_DELAY = 0.2

    def __init__(self, grid: list[list[int]]):
        super().__init__()
        #self.grid = grid
        if not self.__set_grid(grid):
            exit()
        self.__nb_rows_grid = len(self.__grid)
        self.__nb_cols_grid = len(self.__grid[0])
        self.__total_path = []
        self.__showed_path = []
        #self.__loop_removed = False
        self.__start_cell: None | Cell = None
        self.__finish_cell: None | Cell = None
        self.__current_cell: None | Cell = None
        self.__init_cells_around_cells()
        self.__show_grid()

    # @property
    # def grid(self):
    #     return self.__grid
    #
    # @grid.setter
    # def grid(self, grid):
    #     self.__grid = grid

    def __set_grid(self, grid: list[list[int]]) -> bool:
        if type(grid) is not list:
            return False
        for row in grid:
            if type(row) is not list:
                return False
            for cell in row:
                if type(cell) is not int or cell not in self.__AUTHORISED_VALUES:
                    return False

        # les cases avec "authorisation" à False sont celles où on ne peut pas aller, c'est-à-dire celles où il y a un
        # mur ou un caillou. Les cailloux sont éventuellement ajoutés pendant le parcours sur les cases situées dans
        # les culs-de-sacs, en bordure de grille ou dans "coin ouvert" (deux murs à 90° avec la case
        # opposée dans la diagonale qui est vide. Elle doit être vide afin de ne pas créer un cul-de-sac)
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
                label.setPixmap(QPixmap(self.__WALL_IMG))

        return label

    def __init_cells_around_cells(self):
        for row in self.__grid:
            for cell in row:
                cell.straight_cells = self.__get_straight_cells_by_directions(cell)
                cell.diagonal_cells = self.__get_diagonal_cells_by_directions(cell)

    def __get_diagonal_cells_by_directions(self, cell: None | Cell = None) -> dict:
        cell = cell if cell else self.__current_cell
        positions_by_directions = cell.get_diagonal_positions_by_directions()
        return self.__get_cells_by_directions(positions_by_directions)

    def __get_straight_cells_by_directions(self, cell: None | Cell = None) -> dict:
        cell = cell if cell else self.__current_cell
        positions_by_directions = cell.get_straight_positions_by_directions()
        return self.__get_cells_by_directions(positions_by_directions)

    def __get_cells_by_directions(self, positions_by_directions):
        cells_by_directions = {}
        for direction, pos in positions_by_directions.items():
            if not self.__is_pos_in_grid(pos):
                continue
            cell = self.__grid[pos[0]][pos[1]]
            # cell.direction = direction
            cells_by_directions[direction] = cell

        return cells_by_directions

    def __is_pos_in_grid(self, pos: tuple) -> bool:
        return pos[0] in range(self.__nb_rows_grid) and pos[1] in range(self.__nb_cols_grid)

    def __get_authorised_next_cells_by_directions(self) -> dict:
        # straight_cells_by_directions = self.__get_straight_cells_by_directions()
        #
        # for direction, cell in straight_cells_by_directions.items():
        #     straight_cells_by_directions[direction].direction = direction
        #
        # return straight_cells_by_directions
        return {direction: cell for direction, cell in self.__get_straight_cells_by_directions().items()
                if cell.authorisation}

    # def _get_straight_cells_by_directions(self, cell: Cell) -> dict:
    #     return {direction: position for direction, position in cell.get_straight_positions_by_directions()
    #             if self._is_pos_in_grid(position)}
    #
    # def _get_diagonal_cells_by_directions(self, cell: Cell) -> dict:
    #     return {direction: position for direction, position in cell.get_diagonal_positions_by_directions()
    #             if self._is_pos_in_grid(position)}

    def __find_the_exit(self):
        self.__init_start_and_finish_cells()
        self.__add_cell_in_total_path(self.__start_cell)
        self.__add_cell_in_showed_path(self.__start_cell)

        while True:
            print(self.__current_cell.row_id, self.__current_cell.col_id)
            # quand on est sur une case, si on a fait une boucle, on l'enlève
            # if self.__remove_showed_path_loop():
            #     continue
            #self.__remove_showed_path_loop()

            # si la case contient la valeur finale, le programme est terminé
            if self.__current_cell == self.__finish_cell:
                return
            # cas où on met un caillou sur la case pour ne pas y revenir
            if self.__is_current_cell_in_open_corner() or self.__is_current_cell_in_cul_de_sac():
                self.__current_cell.authorisation = False
            next_cell = self.__get_next_cell()
            if not next_cell:
                return

            next_cell.direction = self.__get_key_by_value(self.__current_cell.straight_cells, next_cell)
            self.__add_cell_in_total_path(next_cell)

            if next_cell not in self.__showed_path:
                self.__add_cell_in_showed_path(next_cell)
            else:
                if next_cell == self.__showed_path[-2]:
                    self.__remove_current_cell_from_showed_path(with_timer_delay=False)
                # else:
                #     self.__remove_showed_path_loop()

            # elif next_cell == self.__current_cell.prec_cell:
            # elif next_cell == self.__showed_path[-2]:
            #     self.__remove_current_cell_from_showed_path()
            # else:
            #     self.__remove_possible_loop()

            # else:
            #     if next_cell == self.__showed_path[-2]:
            #         self.__remove_current_cell_from_showed_path()
                # else:
                #     self.__remove_showed_path_loop()



            # if next_cell in self.__showed_path and next_cell == self.__current_cell.prec_cell:
            #     self.__remove_current_cell_from_showed_path()
            # else:
            #     self.__showed_path.append(next_cell)


    @staticmethod
    def __get_key_by_value(dictionnaire: dict, value):
        for key, val in dictionnaire.items():
            if val == value:
                return key

    def __get_next_cell(self) -> None | Cell:
        authorised_next_cells_by_directions = self.__get_authorised_next_cells_by_directions()

        if not authorised_next_cells_by_directions:
            return None

        authorised_next_cells = list(authorised_next_cells_by_directions.values())

        if self.__finish_cell in authorised_next_cells:
            return self.__finish_cell

        # cas où on est sur la case de départ
        if not self.__current_cell.prec_cell:
            return random.choice(authorised_next_cells)

        # cas où on est sur la deuxième case
        if not self.__current_cell.prec_cell.prec_cell and \
                self.__current_cell.direction in authorised_next_cells_by_directions:
            return authorised_next_cells_by_directions[self.__current_cell.direction]

        # si on peut on va tout droit
        if self.__current_cell.direction == self.__current_cell.prec_cell.direction \
                and self.__current_cell.direction in authorised_next_cells_by_directions:
            # si la case courante et la case précédente ont la même direction et que la case à gauche de la case courante
            # est autorisée ainsi que celle à gauche de la case précédente, on enlève la case à gauche de la case courante
            # de la liste des possibilités
            if self.__current_cell.prec_cell.left_cell and \
                    self.__current_cell.prec_cell.left_cell.authorisation and \
                    self.__current_cell.left_cell.authorisation:
                authorised_next_cells.remove(self.__current_cell.left_cell)

            # si la case courante et la case précédente ont la même direction et que la case à droite de la case
            # courante est autorisée ainsi que celle à droite de la case précédente, on enlève la case à droite de la
            # case courante de la liste des possibilités
            if self.__current_cell.prec_cell.right_cell and \
                    self.__current_cell.prec_cell.right_cell.authorisation and \
                    self.__current_cell.right_cell.authorisation:
                authorised_next_cells.remove(self.__current_cell.right_cell)

        # s'il y a au moins une case possible en plus de la précédente, on ne revient pas sur la case précédente
        if len(authorised_next_cells) > 1 and self.__current_cell.prec_cell in authorised_next_cells:
            authorised_next_cells.remove(self.__current_cell.prec_cell)

        return random.choice(authorised_next_cells)

    def __is_diagonal_direction_in_front_of_corner(self, direction: str) -> bool:
        straight_cells_by_directions = self.__get_straight_cells_by_directions()

        for opposite_direction in Cell.get_opposite_directions(direction):
            if opposite_direction not in straight_cells_by_directions:
                continue
            opposite_cell = straight_cells_by_directions[opposite_direction]
            if opposite_cell.authorisation:
                return False

        return True

    # def __is_diagonal_cell_in_front_of_corner(self, direction: str) -> bool:
    #     straight_cells_by_directions = self.__get_straight_cells_by_directions()
    #     opposite_directions = Cell.get_opposite_directions(direction)
    #
    #     for opposite_direction in opposite_directions:
    #         # si "opposite_direction" est au bord du labyrinthe
    #         if opposite_direction not in straight_cells_by_directions:
    #             continue
    #         opposite_cell = straight_cells_by_directions[opposite_direction]
    #         if opposite_cell.authorisation:
    #             return False
    #
    #     return True

    def __is_current_cell_in_open_corner(self) -> bool:
        # un coin "ouvert" est un coin qui n'est pas dans un couloir, donc si on met un caillou sur cette position
        # courante, on ne risque pas de créer un cul-de-sac.
        diagonal_cells_by_directions = self.__get_diagonal_cells_by_directions()
        for direction, cell in diagonal_cells_by_directions.items():
            if cell.authorisation and self.__is_diagonal_direction_in_front_of_corner(direction):
                return True
        return False

    def __is_current_cell_in_cul_de_sac(self) -> bool:
        return len(self.__get_authorised_next_cells_by_directions()) == 1

    def __remove_showed_path_loop(self) -> bool:
        index_current_cell = min_index_possible_cell = len(self.__total_path) - 1

        for cell in self.__get_straight_cells_by_directions().values():
            if cell in self.__total_path:
                index_cell = self.__total_path.index(cell)
                if index_cell < min_index_possible_cell:
                    min_index_possible_cell = index_cell

        diff = index_current_cell - min_index_possible_cell
        if diff < 3:
            return False
        for _ in range(diff):
            self.__remove_current_cell_from_showed_path(with_timer_delay=False)
        return True

    def __init_start_and_finish_cells(self):
        for row in self.__grid:
            for cell in row:
                if cell.value == self.__START_VALUE:
                    self.__start_cell = cell
                elif cell.value == self.__FINISH_VALUE:
                    self.__finish_cell = cell
                if self.__start_cell and self.__finish_cell:
                    return

    # def _is_start_cell(self, cell):
    #     return True if cell.value == self.__START_VALUE else False
    #
    # def _is_finish_cell(self, cell):
    #     return True if cell.value == self.__FINISH_VALUE else False

    # def _get_left_and_right_cells(self):
    #     straight_cells_by_directions = self._get_straight_cells_by_directions()
    #     left_and_right_directions = self.__current_cell.get_left_and_right_directions()
    #     return straight_cells_by_directions[left_and_right_directions[0]], straight_cells_by_directions[left_and_right_directions[1]]

    def __add_cell_in_showed_path(self, cell: Cell):
        self.__showed_path.append(cell)

    def __add_cell_in_total_path(self, cell: Cell):
        """
        NE PLUS TOUCHER !!!!!!!!!!!!!!!!!!!!!!!
        """
        time.sleep(self.__TIMER_DELAY)
        cell.prec_cell = self.__current_cell
        self.__total_path.append(cell)
        self.__current_cell = cell
        cell.left_cell = cell.straight_cells.get(cell.get_left_direction())
        cell.right_cell = cell.straight_cells.get(cell.get_right_direction())
        cell.label.setStyleSheet("background-color:rgba(150, 150, 150, 0.5);")
        cell.label.setText("X")

        if not cell.prec_cell:
            return
        label = cell.prec_cell.label
        if cell.prec_cell == self.__start_cell:
            label.setText(self.__START_LETTER)
        elif not cell.prec_cell.authorisation:
            label.setPixmap(QPixmap(self.__STONE_IMG))
        else:
            label.setText("")

        # left_direction = cell.__get_left_direction()
        # right_direction = cell.__get_right_direction()
        #
        # cell.left_cell = cell.straight_cells[left_direction]
        # cell.right_cell = cell.straight_cells[right_direction]

        # if not cell.prec_cell:
        #     return
        # label = cell.prec_cell.label
        # if cell.prec_cell == self.__start_cell:
        #     label.setText(self.__START_LETTER)
        # elif not cell.prec_cell.authorisation:
        #     label.setPixmap(QPixmap(self.__STONE_IMG))
        # else:
        #     label.setText("")

    def __remove_current_cell_from_showed_path(self, with_timer_delay=True):
        if with_timer_delay:
            time.sleep(self.__TIMER_DELAY)
        # s'il n'y a qu'un élément c'est forcément le point de départ, donc on ne l'enlève pas
        if len(self.__showed_path) == 1:
            return
        cell = self.__showed_path.pop()
        cell.label.setStyleSheet("background-color:none;")

        # label = cell.label
        # label.clear()
        # if cell == self.__start_cell:
        #     label.setText(self.__START_LETTER)
        # label.setStyleSheet("background-color:none;")
        # if not cell.authorisation:
        #     label.setPixmap(QPixmap(self.__STONE_IMG))
        #self.__current_cell = cell.prec_cell
        #self.__prec_cell = cell

    def __show_grid(self):
        self.setWindowTitle("Labyrinthe")
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
    #     [1, 1, 1, 1, 0, 1, 0, 1, 3, 1],
    #     [1, 2, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
    #     [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [0, 1, 0, 1, 0, 0, 1, 1, 1, 1],
    #     [1, 1, 0, 1, 1, 0, 1, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    #     [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
    #     [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    # ]

    # grid = [
    #     [1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
    #     [1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    #     [0, 1, 2, 1, 0, 0, 0, 0, 0, 3],
    #     [0, 1, 0, 1, 0, 0, 1, 1, 1, 1],
    #     [1, 1, 0, 1, 1, 0, 1, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    #     [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
    #     [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    # ]

    # grid = [
    #     [1, 1, 1, 0, 0, 1, 0, 1, 1, 1],
    #     [1, 0, 1, 2, 0, 0, 0, 0, 0, 1],
    #     [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    #     [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    #     [1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    #     [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
    #     [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    # ]

    # grid = [
    #     [1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #     [0, 0, 2, 0, 1, 0, 0, 0, 0, 3],
    #     [1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 0, 1, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    #     [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
    #     [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
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

    # grid = [
    #     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 2, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 3],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0],
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
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0]
    ]

    # Création de l'application
    app = QtWidgets.QApplication([])
    labyrinth = Labyrinth(grid)
    labyrinth.show()
    app.exec()
