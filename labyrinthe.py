import random
import threading
import time

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap

from cell import Cell


class Labyrinth(QtWidgets.QWidget):
    TIMER_DELAY = 0.2

    def __init__(self, grid: list[list[int]]):
        super().__init__()
        if not self._set_grid(grid):
            exit()
        self._nb_rows_grid = len(self._grid)
        self._nb_cols_grid = len(self._grid[0])
        self._path = []
        self._start_cell = None
        self._finish_cell = None
        self._current_cell = None
        self._prec_cell = None
        self._show_grid()

    def _set_grid(self, grid: list[list[int]]) -> bool:
        if type(grid) is not list:
            return False
        for row in grid:
            if type(row) is not list:
                return False
            for cell in row:
                if type(cell) is not int or cell not in Cell.AUTHORISED_VALUES:
                    return False

        self._grid = [[Cell(row_id=row_id, col_id=col_id, value=value)
                       for col_id, value in enumerate(row)] for row_id, row in enumerate(grid)]
        return True

    def _find_the_exit(self):
        self._init_start_and_finish_cells()
        self._add_cell(self._start_cell)

        while True:
            print(self._current_cell.row_id, self._current_cell.col_id)
            # quand on est sur une case, si on a fait une boucle, on l'enlève
            if self._remove_possible_loop():
                continue
            # si la case contient la valeur finale, le programme est terminé
            if self._current_cell.value == Cell.FINISH_VALUE:
                return
            # cas où on met un caillou sur la case pour ne pas y revenir
            if self._is_current_cell_in_open_corner() or self._is_current_cell_in_cul_de_sac():
                self._current_cell.authorisation = False
            next_cell = self._get_next_cell()
            if not next_cell:
                return
            if next_cell in self._path and len(self._path) > 1 and next_cell == self._path[-2]:
                self._remove_current_cell()
                continue
            self._add_cell(next_cell)

    def _get_next_cell(self) -> None | Cell:
        authorised_next_cells_by_ways = self._get_authorised_next_cells_by_ways()
        if not authorised_next_cells_by_ways:
            return None
        authorised_next_cells = list(authorised_next_cells_by_ways.values())
        if self._finish_cell in authorised_next_cells:
            return self._finish_cell
        # cas où on est sur la case de départ
        if not self._prec_cell:
            return random.choice(authorised_next_cells)
        # si la gauche est autorisée alors qu'elle l'était déjà, on l'enlève de la liste des possibilités
        # si la droite est autorisée alors qu'elle l'était déjà, on l'enlève de la liste des possibilités
        #left_pos, right_pos = self._get_left_and_right_pos()

        # if left_pos in authorised_next_positions and

        # si on peut on va tout droit
        if self._current_cell.way in authorised_next_cells_by_ways:
            return authorised_next_cells_by_ways[self._current_cell.way]
        # s'il y a au moins une case possible en plus de la précédente, on ne revient pas sur cette dernière
        if len(authorised_next_cells) > 1 and self._prec_cell in authorised_next_cells:
            authorised_next_cells.remove(self._prec_cell)

        return random.choice(authorised_next_cells)

    # def _get_left_and_right_pos(self):
    #     closest_ways_and_positions = self._get_closest_ways_and_positions()
    #     left_way, right_way = self._get_left_and_right_ways()
    #     return closest_ways_and_positions[left_way], closest_ways_and_positions[right_way]

    def _is_diagonal_cell_in_front_of_corner(self, diagonal_cell: Cell) -> bool:
        straight_cells_by_ways = self._get_straight_cells_by_ways()
        opposite_ways = list(Cell.STRAIGHT_WAYS - {diagonal_cell.way[0], diagonal_cell.way[1]})

        for opposite_way in opposite_ways:
            if opposite_way not in straight_cells_by_ways:
                continue
            opposite_cell = straight_cells_by_ways[opposite_way]
            if opposite_cell.authorisation:
                return False

        return True

    def _is_current_cell_in_open_corner(self) -> bool:
        # un coin "ouvert" est un coin qui n'est pas dans un couloir, donc si on met un caillou sur cette position
        # courante, on ne risque pas de créer un cul-de-sac.
        diagonal_cells_by_ways = self._get_diagonal_cells_by_ways()

        for way, cell in diagonal_cells_by_ways.items():
            if cell.authorisation and self._is_diagonal_cell_in_front_of_corner(cell):
                return True

        return False

    def _is_current_cell_in_cul_de_sac(self) -> bool:
        return len(self._get_authorised_next_cells_by_ways()) == 1

    def _get_authorised_next_cells_by_ways(self) -> dict:
        return {way: cell for way, cell in self._get_straight_cells_by_ways().items() if cell.authorisation}

    def _is_pos_in_grid(self, pos: tuple) -> bool:
        return pos[0] in range(self._nb_rows_grid) and pos[1] in range(self._nb_cols_grid)

    def _get_diagonal_cells_by_ways(self) -> dict:
        positions_by_ways = self._current_cell.get_diagonal_positions_by_ways()
        return self._get_cells_by_ways(positions_by_ways)

    def _get_straight_cells_by_ways(self) -> dict:
        positions_by_ways = self._current_cell.get_straight_positions_by_ways()
        return self._get_cells_by_ways(positions_by_ways)

    def _get_cells_by_ways(self, positions_by_ways):
        cells_by_ways = {}
        for way, pos in positions_by_ways.items():
            if not self._is_pos_in_grid(pos):
                continue
            cell = self._grid[pos[0]][pos[1]]
            cell.way = way
            cells_by_ways[way] = cell

        return cells_by_ways

    def _remove_possible_loop(self) -> bool:
        index_current_cell = min_index_possible_cell = len(self._path) - 1

        for cell in self._get_straight_cells_by_ways().values():
            if cell in self._path:
                index_cell = self._path.index(cell)
                if index_cell < min_index_possible_cell:
                    min_index_possible_cell = index_cell

        diff = index_current_cell - min_index_possible_cell
        if diff < 3:
            return False
        for _ in range(diff):
            self._remove_current_cell(with_timer_delay=False)
        return True

    def _init_start_and_finish_cells(self):
        for i in range(self._nb_rows_grid):
            for j in range(self._nb_cols_grid):
                cell = self._grid[i][j]
                match cell.value:
                    case Cell.START_VALUE:
                        self._start_cell = cell
                    case Cell.FINISH_VALUE:
                        self._finish_cell = cell
                if self._start_cell and self._finish_cell:
                    return

    def _add_cell(self, cell: Cell):
        time.sleep(self.TIMER_DELAY)
        self._path.append(cell)
        self._prec_cell = self._current_cell
        self._current_cell = cell
        self._current_cell.label.setStyleSheet("background-color:rgba(150, 150, 150, 0.5);")
        if not self._prec_cell:
            return
        label = self._prec_cell.label
        if self._prec_cell.value == Cell.START_VALUE:
            label.setText(Cell.START_LETTER)
        elif not self._prec_cell.authorisation:
            label.setPixmap(QPixmap(Cell.STONE_IMG))
        else:
            label.setText("")

    def _remove_current_cell(self, with_timer_delay=True):
        if with_timer_delay:
            time.sleep(self.TIMER_DELAY)
        # s'il n'y a qu'un élément c'est forcément le point de départ, donc on ne l'enlève pas
        if len(self._path) == 1:
            return
        cell = self._path.pop()
        label = cell.label
        label.clear()
        if cell.value == Cell.START_VALUE:
            label.setText(Cell.START_LETTER)
        label.setStyleSheet("background-color:none;")
        if not cell.authorisation:
            label.setPixmap(QPixmap(Cell.STONE_IMG))
        self._current_cell = self._prec_cell
        self._prec_cell = self._path[-2] if len(self._path) > 1 else None

    def _show_grid(self):
        self.setWindowTitle("Labyrinthe")
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(0)
        group = QtWidgets.QGroupBox()

        for i in range(self._nb_rows_grid):
            for j in range(self._nb_cols_grid):
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
                label = self._grid[i][j].label
                label.setFixedSize(30, 30)
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                grid_layout.addWidget(label, i + 1, j + 1)

        group.setLayout(grid_layout)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(group)
        self.setLayout(layout)
        threading.Thread(target=self._find_the_exit).start()


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
        [1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
        [0, 2, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0]
    ]

    # Création de l'application
    app = QtWidgets.QApplication([])
    labyrinth = Labyrinth(grid)
    labyrinth.show()
    app.exec()
