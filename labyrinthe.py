import random
import threading
import time

from PySide6 import QtWidgets as QtW, QtCore
from PySide6.QtGui import QPixmap


class Labyrinth(QtW.QWidget):
    START_LETTER = "D"
    FINISH_LETTER = "A"
    PATH_VALUE = 0
    WALL_VALUE = 1
    START_VALUE = 2
    FINISH_VALUE = 3
    TIMER_DELAY = 0.2
    WALL_IMG = "mur.webp"
    MAN_IMG = "bb.png"
    PATH_IMG = "aa.png"
    STONE_IMG = "caillou.png"

    def __init__(self, grid):
        super().__init__()
        self._grid = [[{"value": value,
                        "authorisation": False if value == self.WALL_VALUE else True,
                        "label": self._get_label_by_value(value)} for value in row] for row in grid]
        self._nb_rows_grid = len(self._grid)
        self._nb_cols_grid = len(self._grid[0])
        self._path = []
        self._current_pos = None
        self._prec_pos = None
        #self._next_pos = ()
        self._show_grid()

    def _get_label_by_value(self, value):
        label = QtW.QLabel()

        match value:
            case self.START_VALUE:
                label.setText(self.START_LETTER)
            case self.FINISH_VALUE:
                label.setText(self.FINISH_LETTER)
            case self.WALL_VALUE:
                label.setPixmap(QPixmap(self.WALL_IMG))
            # case _:
            #     label.setPixmap(QPixmap())

        return label

    def _find_the_exit(self):
        self._init_start_pos()

        while True:
            time.sleep(self.TIMER_DELAY)
            possible_next_positions = self._get_possible_next_positions()

            match len(possible_next_positions):
                case 0:
                    # plus d'issue possible
                    return
                case 1:
                    # on est dans un cul-de-sac (ça peut être dès le point de départ)
                    self._grid[self._current_pos[0]][self._current_pos[1]]["authorisation"] = False
                    #self._grid[self._current_pos[0]][self._current_pos[1]]["label"].setText("4")
                    next_pos = possible_next_positions[0]
                    #if next_pos == self._prec_pos:
                    if len(self._path) > 1 and next_pos == self._path[-2]:
                        # on fait demi-tour si on arrive dans ce cul-de-sac (ce qui n'est pas le cas si le cul-de-sac
                        # est au point de départ ; dans ce cas-là on avance, on ne fait pas demi-tour)
                        self._remove_current_pos()
                        continue
                case _:
                    if self._prec_pos in possible_next_positions:
                        # pour ne pas revenir en arrière
                        possible_next_positions.remove(self._prec_pos)

                    if self._remove_possible_loop(possible_next_positions):
                        continue

                    next_pos = random.choice(possible_next_positions)

                    if next_pos in self._path:
                        self._remove_current_pos()
                        continue
            self._add_pos(next_pos)
            # si la case contient le 3, le programme est terminé
            if self._grid[next_pos[0]][next_pos[1]]["value"] == self.FINISH_VALUE:
                return

    def _get_possible_next_positions(self):
        possible_next_pos = []

        for pos in self._get_closest_positions():
            if (pos[0] in range(self._nb_rows_grid) and
                    pos[1] in range(self._nb_cols_grid) and
                    self._grid[pos[0]][pos[1]]["authorisation"]):
                possible_next_pos.append(pos)

        return possible_next_pos

    # def _get_next_pos(self) -> tuple:
    #     possible_next_pos = []
    #
    #     for pos in self._get_closest_positions():
    #         if (pos[0] in range(self._nb_rows_grid) and
    #                 pos[1] in range(self._nb_cols_grid) and
    #                 self._grid[pos[0]][pos[1]]["authorisation"]):
    #                 #and (pos == self._prec_pos or pos not in self._path)):
    #             possible_next_pos.append(pos)
    #
    #     if len(possible_next_pos) > 1:
    #         possible_next_pos.remove(self._prec_pos)
    #
    #     return random.choice(possible_next_pos) if len(possible_next_pos) > 0 else ()

    def _get_closest_positions(self):
        return ((self._current_pos[0] - 1, self._current_pos[1]),
                (self._current_pos[0], self._current_pos[1] + 1),
                (self._current_pos[0] + 1, self._current_pos[1]),
                (self._current_pos[0], self._current_pos[1] - 1))

    def _remove_possible_loop(self, possible_positions) -> bool:
        for possible_position in possible_positions:
            if possible_position in self._path:
                index_possible_position = self._path.index(possible_position)
                index_current_position = len(self._path) - 1
                diff = index_current_position - index_possible_position
                if diff < 3:
                    continue
                for _ in range(diff):
                    self._remove_current_pos(with_timer_delay=False)
                return True
        return False

    # def _remove_possible_loop(self, possible_positions):
    #     if len(self._path) > 1:
    #         for pos in possible_positions:
    #             if pos in self._path and pos != self._prec_pos:
    #                 #time.sleep(self.TIMER_DELAY)
    #                 for _ in range(len(self._path) - 1 - self._path.index(pos)):
    #                     self._remove_current_pos()
    #                 return

    def _init_start_pos(self):
        for i in range(self._nb_rows_grid):
            for j in range(self._nb_cols_grid):
                if self._grid[i][j]["value"] == self.START_VALUE:
                    self._add_pos((i, j))
                    return

    def _add_pos(self, pos):
        time.sleep(self.TIMER_DELAY)
        # if len(self._path) > 0:
        #     current_label = self._grid[self._current_pos[0]][self._current_pos[1]]["label"]
        #     if self._grid[self._current_pos[0]][self._current_pos[1]]["value"] == self.START_VALUE:
        #         current_label.setText(self.START_LETTER)
        #else:
        #current_label.setPixmap(QPixmap(self.PATH_IMG))
        #current_label.setPixmap(QPixmap())
        #current_label.setStyleSheet("background-color:rgba(150, 150, 150, 0.5);")
        self._path.append(pos)
        self._prec_pos = self._current_pos
        self._current_pos = pos
        self._grid[pos[0]][pos[1]]["label"].setStyleSheet("background-color:rgba(150, 150, 150, 0.5);")

        if not self._prec_pos:
            return

        if self._grid[self._prec_pos[0]][self._prec_pos[1]]["value"] == self.START_VALUE:
            self._grid[self._prec_pos[0]][self._prec_pos[1]]["label"].setText(self.START_LETTER)
        elif not self._grid[self._prec_pos[0]][self._prec_pos[1]]["authorisation"]:
            self._grid[self._prec_pos[0]][self._prec_pos[1]]["label"].setPixmap(QPixmap(self.STONE_IMG))

        #self._grid[pos[0]][pos[1]]["label"].setText("X")
        #self._grid[pos[0]][pos[1]]["label"].setPixmap(QPixmap(self.MAN_IMG))

    def _remove_current_pos(self, with_timer_delay=True):
        if with_timer_delay:
            time.sleep(self.TIMER_DELAY)
        # s'il n'y a qu'un élément c'est forcément le point de départ, donc on ne l'enlève pas
        if len(self._path) == 1:
            return
        pos = self._path.pop()
        label = self._grid[pos[0]][pos[1]]["label"]
        label.clear()
        if self._grid[pos[0]][pos[1]]["value"] == self.START_VALUE:
            label.setText(self.START_LETTER)
        # self._grid[pos[0]][pos[1]]["label"].setText("")
        self._grid[pos[0]][pos[1]]["label"].setStyleSheet("background-color:none;")
        if not self._grid[pos[0]][pos[1]]["authorisation"]:
            self._grid[pos[0]][pos[1]]["label"].setPixmap(QPixmap(self.STONE_IMG))
        #if len(self._path) > 1:
        self._current_pos = self._path[-1]
        self._prec_pos = pos
        #self._grid[self._current_pos[0]][self._current_pos[1]]["label"].setPixmap(QPixmap(self.MAN_IMG))

    def _show_grid(self):
        self.setWindowTitle("Labyrinthe")
        grid_layout = QtW.QGridLayout()
        grid_layout.setSpacing(0)
        group = QtW.QGroupBox()

        for i in range(self._nb_rows_grid):
            for j in range(self._nb_cols_grid):
                if i == 0:
                    label = QtW.QLabel(str(j))
                    label.setFixedSize(30, 30)
                    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    grid_layout.addWidget(label, i, j + 1)
                if j == 0:
                    label = QtW.QLabel(str(i))
                    label.setFixedSize(30, 30)
                    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    grid_layout.addWidget(label, i + 1, j)
                label = self._grid[i][j]["label"]
                label.setFixedSize(30, 30)
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                grid_layout.addWidget(label, i + 1, j + 1)

        group.setLayout(grid_layout)
        layout = QtW.QVBoxLayout()
        layout.addWidget(group)
        self.setLayout(layout)
        threading.Thread(target=self._find_the_exit).start()


if __name__ == '__main__':
    # grid = [
    #     [1, 1, 1, 1, 0, 1, 0, 1, 3, 1],
    #     [1, 2, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    #     [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [0, 1, 0, 1, 0, 0, 1, 1, 1, 1],
    #     [1, 1, 0, 1, 1, 0, 1, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    #     [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
    #     [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
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

    grid = [
        [1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 2, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    ]

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

    # grid = [
    #     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 3],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0, 0, 2, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0]
    # ]

    # Création de l'application
    app = QtW.QApplication([])
    labyrinth = Labyrinth(grid)
    labyrinth.show()
    app.exec()
