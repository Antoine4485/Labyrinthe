import random
import threading
import time

from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap


class Cell:
    def __init__(self, value, authorisation, label):
        self.value = value
        self.authorisation = authorisation
        self.label = label


class Labyrinth(QtWidgets.QWidget):
    START_LETTER = "D"
    FINISH_LETTER = "A"
    PATH_VALUE = 0
    WALL_VALUE = 1
    START_VALUE = 2
    FINISH_VALUE = 3
    TIMER_DELAY = 0.2
    WALL_IMG = "mur.webp"
    STONE_IMG = "caillou.png"
    CARDINAL_POINTS = {"N", "E", "S", "O"}

    def __init__(self, grid):
        super().__init__()
        # les cases avec "authorisation" à False sont celles où on ne peut pas aller, c'est-à-dire celles où il y a un
        # mur ou un caillou. Les cailloux sont éventuellement ajoutés pendant le parcours sur les cases situées dans
        # les culs-de-sacs, en bordure de grille, ou dans "coin ouvert" c'est-à-dire deux murs à 90° et avec la case
        # opposée dans la diagonale qui est vide afin de ne pas créer un cul-de-sac.
        self._grid = [[Cell(value=value,
                            authorisation=False if value == self.WALL_VALUE else True,
                            label=self._get_label_by_value(value)) for value in row] for row in grid]
        self._nb_rows_grid = len(self._grid)
        self._nb_cols_grid = len(self._grid[0])
        self._path = []
        self._current_pos = None
        self._prec_pos = None
        self._start_value_pos = None
        self._finish_value_pos = None
        self._way = ""
        self._show_grid()

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

    def _find_the_exit(self):
        self._init_start_and_finish_pos()
        self._add_pos(self._start_value_pos)

        while True:
            # quand on est sur une case, si on a fait une boucle, on l'enlève
            if self._remove_possible_loop():
                continue
            # si la case contient la valeur finale, le programme est terminé
            if self._grid[self._current_pos[0]][self._current_pos[1]].value == self.FINISH_VALUE:
                return
            # cas où on met un caillou sur la case pour ne pas y revenir
            if self._is_current_pos_in_open_corner() or \
                    self._is_current_pos_in_cul_de_sac():
                self._grid[self._current_pos[0]][self._current_pos[1]].authorisation = False

            next_pos = self._get_next_pos()
            if not next_pos:
                return
            if next_pos in self._path and len(self._path) > 1 and next_pos == self._path[-2]:
                self._remove_current_pos()
                continue

            self._add_pos(next_pos)

    def _get_next_pos(self) -> tuple:
        possible_next_positions = self._get_possible_next_positions()
        if not possible_next_positions:
            return ()

        if self._finish_value_pos in possible_next_positions:
            next_pos = self._finish_value_pos
        else:
            # s'il y a au moins une case possible en plus de la précédente, on ne revient pas sur cette dernière
            if len(possible_next_positions) > 1 and self._prec_pos in possible_next_positions:
                possible_next_positions.remove(self._prec_pos)

            next_pos = random.choice(possible_next_positions)

        return next_pos

    def _is_diagonal_pos_in_front_of_corner(self, diag_cardinal_point: str) -> bool:
        closest_positions = self._get_closest_positions()
        opposite_cardinal_points = list(self.CARDINAL_POINTS - {diag_cardinal_point[0], diag_cardinal_point[1]})

        for opposite_cardinal_point in opposite_cardinal_points:
            if opposite_cardinal_point not in closest_positions:
                continue
            opposite_cardinal_point_pos = closest_positions[opposite_cardinal_point]
            if self._grid[opposite_cardinal_point_pos[0]][opposite_cardinal_point_pos[1]].authorisation:
                return False

        return True

    def _is_current_pos_in_open_corner(self) -> bool:
        # un coin "ouvert" est un coin qui n'est pas dans un couloir, donc si on met un caillou sur cette position
        # courante, on ne risque pas de créer un cul-de-sac.
        diagonal_positions = self._get_diagonal_positions()

        for cardinal_point, pos in diagonal_positions.items():
            if self._grid[pos[0]][pos[1]].authorisation and self._is_diagonal_pos_in_front_of_corner(cardinal_point):
                return True

        return False

    def _is_current_pos_in_cul_de_sac(self) -> bool:
        return len(self._get_possible_next_positions()) == 1

    def _get_possible_next_positions(self) -> list[tuple]:
        possible_next_pos = []

        for pos in self._get_closest_positions().values():
            if pos[0] in range(self._nb_rows_grid) and \
                    pos[1] in range(self._nb_cols_grid) and \
                    self._grid[pos[0]][pos[1]].authorisation:
                possible_next_pos.append(pos)

        return possible_next_pos

    def _is_pos_in_grid(self, pos: tuple) -> bool:
        return pos[0] in range(self._nb_rows_grid) and pos[1] in range(self._nb_cols_grid)

    def _get_diagonal_positions(self) -> dict:
        positions = {
            "NE": (self._current_pos[0] - 1, self._current_pos[1] + 1),
            "SE": (self._current_pos[0] + 1, self._current_pos[1] + 1),
            "SO": (self._current_pos[0] + 1, self._current_pos[1] - 1),
            "NO": (self._current_pos[0] - 1, self._current_pos[1] - 1)
        }

        return {cardinal_point: pos for cardinal_point, pos in positions.items() if self._is_pos_in_grid(pos)}

    def _get_closest_positions(self) -> dict:
        positions = {
            "N": (self._current_pos[0] - 1, self._current_pos[1]),
            "E": (self._current_pos[0], self._current_pos[1] + 1),
            "S": (self._current_pos[0] + 1, self._current_pos[1]),
            "O": (self._current_pos[0], self._current_pos[1] - 1)
        }

        return {cardinal_point: pos for cardinal_point, pos in positions.items() if self._is_pos_in_grid(pos)}

    def _remove_possible_loop(self) -> bool:
        index_current_pos = min_index_possible_pos = len(self._path) - 1

        for pos in self._get_closest_positions().values():
            if pos in self._path:
                index_pos = self._path.index(pos)
                if index_pos < min_index_possible_pos:
                    min_index_possible_pos = index_pos

        diff = index_current_pos - min_index_possible_pos
        if diff < 3:
            return False

        for _ in range(diff):
            self._remove_current_pos(with_timer_delay=False)

        return True

    def _init_start_and_finish_pos(self):
        for i in range(self._nb_rows_grid):
            for j in range(self._nb_cols_grid):
                match self._grid[i][j].value:
                    case self.START_VALUE:
                        self._start_value_pos = (i, j)
                    case self.FINISH_VALUE:
                        self._finish_value_pos = (i, j)
                if self._start_value_pos and self._finish_value_pos:
                    return

    def _add_pos(self, pos: tuple):
        time.sleep(self.TIMER_DELAY)
        self._path.append(pos)
        self._prec_pos = self._current_pos
        self._current_pos = pos
        self._grid[pos[0]][pos[1]].label.setStyleSheet("background-color:rgba(150, 150, 150, 0.5);")

        if not self._prec_pos:
            return

        if self._grid[self._prec_pos[0]][self._prec_pos[1]].value == self.START_VALUE:
            self._grid[self._prec_pos[0]][self._prec_pos[1]].label.setText(self.START_LETTER)
        elif not self._grid[self._prec_pos[0]][self._prec_pos[1]].authorisation:
            self._grid[self._prec_pos[0]][self._prec_pos[1]].label.setPixmap(QPixmap(self.STONE_IMG))
        else:
            self._grid[self._prec_pos[0]][self._prec_pos[1]].label.setText("")

    def _remove_current_pos(self, with_timer_delay=True):
        if with_timer_delay:
            time.sleep(self.TIMER_DELAY)
        # s'il n'y a qu'un élément c'est forcément le point de départ, donc on ne l'enlève pas
        if len(self._path) == 1:
            return
        pos = self._path.pop()
        label = self._grid[pos[0]][pos[1]].label
        label.clear()
        if self._grid[pos[0]][pos[1]].value == self.START_VALUE:
            label.setText(self.START_LETTER)
        self._grid[pos[0]][pos[1]].label.setStyleSheet("background-color:none;")
        if not self._grid[pos[0]][pos[1]].authorisation:
            self._grid[pos[0]][pos[1]].label.setPixmap(QPixmap(self.STONE_IMG))
        self._current_pos = self._path[-1]
        self._prec_pos = pos

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
        [0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 2, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0]
    ]

    # Création de l'application
    app = QtWidgets.QApplication([])
    labyrinth = Labyrinth(grid)
    labyrinth.show()
    app.exec()
