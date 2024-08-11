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
    WAYS = {"N", "E", "S", "O"}

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
        self._start_pos = None
        self._finish_pos = None
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
        self._add_pos(self._start_pos)

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

            next_way_and_pas = self._get_next_way_and_pos()
            if not next_way_and_pas:
                return
            way, next_pos = next_way_and_pas
            if next_pos in self._path and len(self._path) > 1 and next_pos == self._path[-2]:
                self._remove_current_pos()
                continue

            self._way = way
            self._add_pos(next_pos)

    # def _get_next_pos_cardinal_point(self, next_pos: tuple) -> str:
    #     for cardinal_point, pos in self._get_authorised_next_positions().items():
    #         if pos == next_pos:
    #             return cardinal_point
    #     return ""

    def _get_next_way_and_pos(self) -> tuple:
        authorised_next_ways_and_positions = self._get_authorised_next_ways_and_positions()
        if not authorised_next_ways_and_positions:
            return ()

        authorised_next_positions = list(authorised_next_ways_and_positions.values())

        # if self._finish_pos in authorised_next_positions_values:
        #     return self._finish_pos
        #
        # # cas où on est sur la case de départ
        # if not self._prec_pos:
        #     return random.choice(authorised_next_positions_values)
        #
        # if self._way in authorised_next_positions:
        #     return authorised_next_positions[self._way]
        #
        # # s'il y a au moins une case possible en plus de la précédente, on ne revient pas sur cette dernière
        # if len(authorised_next_positions_values) > 1 and self._prec_pos in authorised_next_positions_values:
        #     authorised_next_positions_values.remove(self._prec_pos)
        #
        # return random.choice(authorised_next_positions)

        # cas où la case finale est à côté de la case actuelle
        if self._finish_pos in authorised_next_positions:
            next_pos = self._finish_pos
        else:
            # cas où on est sur la case de départ
            if not self._prec_pos:
                next_pos = random.choice(authorised_next_positions)
            else:
                # si on peut on va tout droit
                if self._way in authorised_next_ways_and_positions:
                    next_pos = authorised_next_ways_and_positions[self._way]
                else:
                    # s'il y a au moins une case possible en plus de la précédente, on ne revient pas sur cette dernière
                    if len(authorised_next_positions) > 1 and self._prec_pos in authorised_next_positions:
                        authorised_next_positions.remove(self._prec_pos)

                    next_pos = random.choice(authorised_next_positions)

        return self._get_dict_key(authorised_next_ways_and_positions, next_pos), next_pos

    def _get_left_and_right_ways(self) -> tuple:
        match self._way:
            case "N":
                return "O", "E"
            case "E":
                return "N", "S"
            case "S":
                return "E", "O"
            case "O":
                return "S", "N"
            case _:
                return ()

    def _is_diagonal_pos_in_front_of_corner(self, diagonal_way: str) -> bool:
        closest_ways_and_positions = self._get_closest_ways_and_positions()
        opposite_ways = list(self.WAYS - {diagonal_way[0], diagonal_way[1]})

        for opposite_way in opposite_ways:
            if opposite_way not in closest_ways_and_positions:
                continue
            opposite_pos = closest_ways_and_positions[opposite_way]
            if self._grid[opposite_pos[0]][opposite_pos[1]].authorisation:
                return False

        return True

    def _is_current_pos_in_open_corner(self) -> bool:
        # un coin "ouvert" est un coin qui n'est pas dans un couloir, donc si on met un caillou sur cette position
        # courante, on ne risque pas de créer un cul-de-sac.
        diagonal_ways_and_positions = self._get_diagonal_ways_and_positions()

        for way, pos in diagonal_ways_and_positions.items():
            if self._grid[pos[0]][pos[1]].authorisation and self._is_diagonal_pos_in_front_of_corner(way):
                return True

        return False

    def _is_current_pos_in_cul_de_sac(self) -> bool:
        return len(self._get_authorised_next_ways_and_positions()) == 1

    def _get_authorised_next_ways_and_positions(self) -> dict:
        return {way: pos for way, pos in self._get_closest_ways_and_positions().items()
                if self._grid[pos[0]][pos[1]].authorisation}

    def _is_pos_in_grid(self, pos: tuple) -> bool:
        return pos[0] in range(self._nb_rows_grid) and pos[1] in range(self._nb_cols_grid)

    def _get_diagonal_ways_and_positions(self) -> dict:
        ways_and_positions = {
            "NE": (self._current_pos[0] - 1, self._current_pos[1] + 1),
            "SE": (self._current_pos[0] + 1, self._current_pos[1] + 1),
            "SO": (self._current_pos[0] + 1, self._current_pos[1] - 1),
            "NO": (self._current_pos[0] - 1, self._current_pos[1] - 1)
        }

        return {way: pos for way, pos in ways_and_positions.items() if self._is_pos_in_grid(pos)}

    def _get_closest_ways_and_positions(self) -> dict:
        ways_and_positions = {
            "N": (self._current_pos[0] - 1, self._current_pos[1]),
            "E": (self._current_pos[0], self._current_pos[1] + 1),
            "S": (self._current_pos[0] + 1, self._current_pos[1]),
            "O": (self._current_pos[0], self._current_pos[1] - 1)
        }

        return {way: pos for way, pos in ways_and_positions.items() if self._is_pos_in_grid(pos)}

    def _remove_possible_loop(self) -> bool:
        index_current_pos = min_index_possible_pos = len(self._path) - 1

        for pos in self._get_closest_ways_and_positions().values():
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
                        self._start_pos = (i, j)
                    case self.FINISH_VALUE:
                        self._finish_pos = (i, j)
                if self._start_pos and self._finish_pos:
                    return

    def _add_pos(self, pos: tuple):
        time.sleep(self.TIMER_DELAY)
        self._path.append(pos)
        self._prec_pos = self._current_pos
        self._current_pos = pos
        self._grid[pos[0]][pos[1]].label.setStyleSheet("background-color:rgba(150, 150, 150, 0.5);")
        if not self._prec_pos:
            return
        cell = self._grid[self._prec_pos[0]][self._prec_pos[1]]
        label = cell.label
        if cell.value == self.START_VALUE:
            label.setText(self.START_LETTER)
        elif not cell.authorisation:
            label.setPixmap(QPixmap(self.STONE_IMG))
        else:
            label.setText("")

    def _remove_current_pos(self, with_timer_delay=True):
        if with_timer_delay:
            time.sleep(self.TIMER_DELAY)
        # s'il n'y a qu'un élément c'est forcément le point de départ, donc on ne l'enlève pas
        if len(self._path) == 1:
            return
        pos = self._path.pop()
        cell = self._grid[pos[0]][pos[1]]
        label = cell.label
        label.clear()
        if cell.value == self.START_VALUE:
            label.setText(self.START_LETTER)
        label.setStyleSheet("background-color:none;")
        if not cell.authorisation:
            label.setPixmap(QPixmap(self.STONE_IMG))
        self._current_pos = self._path[-1]
        self._prec_pos = pos
        self._way = None

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

    @staticmethod
    def _get_dict_key(dictionnary: dict, value):
        return next((key for key, val in dictionnary.items() if val == value))


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
        [0, 2, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
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
