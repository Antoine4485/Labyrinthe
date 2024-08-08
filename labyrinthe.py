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
    TIMER_DELAY = 0.5
    WALL_IMG = "mur.webp"
    MAN_IMG = "bb.png"
    PATH_IMG = "aa.png"
    STONE_IMG = "caillou.png"
    CARDINAL_POINTS = {"N", "E", "S", "O"}

    def __init__(self, grid):
        super().__init__()
        # les cases avec "authorisation" à False sont celles où on ne peut pas aller, c'est-à-dire celles où il y a un
        # mur ou un caillou. Les cailloux sont éventuellement ajoutés pendant le parcours sur les cases situées dans
        # les culs-de-sacs ou en bordure de grille, ou sur celles entourées de 8 cases vides. Ceci afin de ne pas
        # repasser sur ces cases et d'arriver plus vite à la fin.
        self._grid = [[{"value": value,
                        "authorisation": False if value == self.WALL_VALUE else True,
                        "label": self._get_label_by_value(value)} for value in row] for row in grid]
        self._nb_rows_grid = len(self._grid)
        self._nb_cols_grid = len(self._grid[0])
        self._path = []
        self._current_pos = None
        self._prec_pos = None
        self._start_value_pos = None
        self._finish_value_pos = None
        self._show_grid()
        #self._find_the_exit()

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

    def _is_diagonal_pos_in_front_of_corner(self, diag_cardinal_point):
        closest_positions = self._get_closest_positions()
        opposite_cardinal_points = list(self.CARDINAL_POINTS - {diag_cardinal_point[0], diag_cardinal_point[1]})

        for opposite_cardinal_point in opposite_cardinal_points:
            if opposite_cardinal_point not in closest_positions:
                continue
            opposite_cardinal_point_pos = closest_positions[opposite_cardinal_point]
            if self._grid[opposite_cardinal_point_pos[0]][opposite_cardinal_point_pos[1]]["authorisation"]:
                return False

        return True

    def _is_current_pos_in_open_corner(self):
        # un coin "ouvert" est un coin qui n'est pas dans un couloir
        diagonal_positions = self._get_diagonal_positions()

        for cardinal_point, pos in diagonal_positions.items():
            if self._grid[pos[0]][pos[1]]["authorisation"] and self._is_diagonal_pos_in_front_of_corner(cardinal_point):
                return True

        return False



    # def _is_current_pos_in_corner(self):
    #     diag_cardinal_points = self._get_four_diagonal_positions().keys()
    #     closest_positions = self._get_four_closest_positions()
    #     corner = True
    #
    #     for diag_cardinal_point in diag_cardinal_points:
    #         corner = True
    #         opposite_cardinal_points = list(self.CARDINAL_POINTS - {diag_cardinal_point[0], diag_cardinal_point[1]})
    #         for opposite_cardinal_point in opposite_cardinal_points:
    #             opposite_cardinal_point_pos = closest_positions[opposite_cardinal_point]
    #             row, col = opposite_cardinal_point_pos[0], opposite_cardinal_point_pos[1]
    #             if self._grid[row][col]["authorisation"]:
    #                 corner = False
    #                 break
    #
    #     return corner

    def is_current_pos_in_cul_de_sac(self):
        return len(self._get_possible_next_positions()) == 1

    def _is_current_pos_on_border_grid(self):
        if self._current_pos[0] in (0, self._nb_rows_grid - 1) or \
                self._current_pos[1] in (0, self._nb_cols_grid - 1):
            return True
        return False

    def _find_the_exit(self):
        self._init_start_and_finish_pos()
        self._add_pos(self._start_value_pos)

        while True:
            time.sleep(self.TIMER_DELAY)
            # if self._remove_possible_loop():
            #     continue
            # si la case contient le 3, le programme est terminé
            if self._grid[self._current_pos[0]][self._current_pos[1]]["value"] == self.FINISH_VALUE:
                return

            # cas où on met un caillou sur la case
            # if self._is_current_pos_on_border_grid() or \
            #         self._is_current_pos_in_open_corner() or \
            #         self.is_current_pos_in_cul_de_sac():
            #     self._grid[self._current_pos[0]][self._current_pos[1]]["authorisation"] = False

            if self._is_current_pos_in_open_corner() or \
                    self.is_current_pos_in_cul_de_sac():
                self._grid[self._current_pos[0]][self._current_pos[1]]["authorisation"] = False

            possible_next_positions = self._get_possible_next_positions()
            if not possible_next_positions:
                return

            if self._finish_value_pos in possible_next_positions:
                next_pos = self._finish_value_pos
            else:
                # s'il y a au moins une case possible en plus de la précédente, on ne revient pas sur cette dernière
                # if len(possible_next_positions) > 1 and self._prec_pos in possible_next_positions:
                #     possible_next_positions.remove(self._prec_pos)
                if len(possible_next_positions) > 1 and \
                        len(self._path) > 1 and \
                        self._path[-2] in possible_next_positions:
                    possible_next_positions.remove(self._path[-2])

                if len(possible_next_positions) == 1:
                    next_pos = possible_next_positions[0]
                else:
                    next_pos = random.choice(possible_next_positions)

                #if next_pos in self._path:
                # if next_pos in self._path and len(self._path) > 1 and next_pos == self._path[-2]:
                #     self._remove_current_pos()
                #     continue

            self._add_pos(next_pos)

            # match len(possible_next_positions):
            #     case 0:
            #         # plus d'issue possible
            #         return
            #     case 1:
            #         # on est dans un cul-de-sac
            #         # si on est sur la case de départ on avance
            #         if self._grid[self._current_pos[0]][self._current_pos[1]]["value"] == self.START_VALUE:
            #             next_pos = possible_next_positions[0]
            #         # sinon on recule
            #         else:
            #             self._remove_current_pos()
            #             continue
            #     case _:



            # # si la case contient le 3, le programme est terminé
            # if self._grid[self._current_pos[0]][self._current_pos[1]]["value"] == self.FINISH_VALUE:
            #     return
            #
            # # if self._is_case_isolated():
            # #     # si la case est entourée de 8 cases vides, on met un caillou dessus
            # #     self._grid[self._current_pos[0]][self._current_pos[1]]["authorisation"] = False
            #
            # possible_next_positions = []
            # for pos in self._get_possible_next_positions():
            #     if pos[0] not in range(self._nb_rows_grid) or pos[1] not in range(self._nb_cols_grid):
            #         # si la case est au bord de la grille, on met un caillou dessus
            #         self._grid[self._current_pos[0]][self._current_pos[1]]["authorisation"] = False
            #     else:
            #         possible_next_positions.append(pos)
            #
            # match len(possible_next_positions):
            #     case 0:
            #         # plus d'issue possible
            #         return
            #     case 1:
            #         # on est dans un cul-de-sac (ça peut être dès le point de départ)
            #         self._grid[self._current_pos[0]][self._current_pos[1]]["authorisation"] = False
            #         #self._grid[self._current_pos[0]][self._current_pos[1]]["label"].setText("4")
            #         next_pos = possible_next_positions[0]
            #         #if next_pos == self._prec_pos:
            #         if len(self._path) > 1 and next_pos == self._path[-2]:
            #             # on fait demi-tour si on arrive dans ce cul-de-sac (ce qui n'est pas le cas si le cul-de-sac
            #             # est au point de départ ; dans ce cas-là on avance, on ne fait pas demi-tour)
            #             self._remove_current_pos()
            #             continue
            #     case _:
            #         if self._prec_pos in possible_next_positions:
            #             # pour ne pas revenir en arrière
            #             possible_next_positions.remove(self._prec_pos)
            #         if self._remove_possible_loop(possible_next_positions):
            #             continue
            #         next_pos = random.choice(possible_next_positions)
            #         if next_pos in self._path:
            #             self._remove_current_pos()
            #             continue
            #
            # self._add_pos(next_pos)

    # def _get_possible_next_positions(self):
    #     possible_next_pos = []
    #
    #     # on inclus les éventuelles cases extérieures à la grille si la case est en bord de grille,
    #     # afin de pouvoir y mettre un caillou par la suite
    #     for pos in self._get_four_closest_positions().values():
    #         if (pos[0] not in range(self._nb_rows_grid) or
    #                 pos[1] not in range(self._nb_cols_grid) or
    #                 self._grid[pos[0]][pos[1]]["authorisation"]):
    #             possible_next_pos.append(pos)
    #
    #     return possible_next_pos

    def _get_possible_next_positions(self):
        possible_next_pos = []

        for pos in self._get_closest_positions().values():
            if (pos[0] in range(self._nb_rows_grid) and
                    pos[1] in range(self._nb_cols_grid) and
                    self._grid[pos[0]][pos[1]]["authorisation"]):
                possible_next_pos.append(pos)

        return possible_next_pos

        # if (pos[0] in range(self._nb_rows_grid) and
        #         pos[1] in range(self._nb_cols_grid) and
        #         self._grid[pos[0]][pos[1]]["authorisation"]):
        #     possible_next_pos.append(pos)

        # for pos in self._get_closest_positions():
        #     if self._grid[pos[0]][pos[1]]["authorisation"] or

        # return [pos for pos in self._get_closest_positions() if
        #         self._grid[pos[0]][pos[1]]["authorisation"] or
        #         self._grid[pos[0]][pos[1]]["value"] != self.WALL_VALUE]

        # for pos in self._get_closest_positions():
        #     if self._grid[pos[0]][pos[1]]["authorisation"]:
        #         possible_next_pos.append(pos)
        #
        # return possible_next_pos

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

    def _is_pos_in_grid(self, pos):
        return pos[0] in range(self._nb_rows_grid) and pos[1] in range(self._nb_cols_grid)

    def _get_diagonal_positions(self):
        positions = {
            "NE": (self._current_pos[0] - 1, self._current_pos[1] + 1),
            "SE": (self._current_pos[0] + 1, self._current_pos[1] + 1),
            "SO": (self._current_pos[0] + 1, self._current_pos[1] - 1),
            "NO": (self._current_pos[0] - 1, self._current_pos[1] - 1)
        }

        return {cardinal_point: pos for cardinal_point, pos in positions.items() if self._is_pos_in_grid(pos)}

    def _get_closest_positions(self):
        positions = {
            "N": (self._current_pos[0] - 1, self._current_pos[1]),
            "E": (self._current_pos[0], self._current_pos[1] + 1),
            "S": (self._current_pos[0] + 1, self._current_pos[1]),
            "O": (self._current_pos[0], self._current_pos[1] - 1)
        }

        return {cardinal_point: pos for cardinal_point, pos in positions.items() if self._is_pos_in_grid(pos)}



    # def _is_case_isolated(self):
    #     for i in range(self._current_pos[0] - 1, self._current_pos[0] + 2):
    #         for j in range(self._current_pos[1] - 1, self._current_pos[1] + 2):
    #             if ((i != self._current_pos[0] or j != self._current_pos[1]) and
    #                     not (self._grid[i][j]["authorisation"])):
    #                 return False
    #     return True

    #def _is_case_on_corner(self):

    # def _remove_loop(self, start_loop_pos):
    #     index_current_position = len(self._path) - 1
    #     diff = index_current_position - self._path.index(start_loop_pos)
    #     # if diff < 3:
    #     #     continue
    #     for _ in range(diff):
    #         self._remove_current_pos(with_timer_delay=False)
        #return True
        #return False

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

    # def _remove_possible_loop(self, possible_positions):
    #     if len(self._path) > 1:
    #         for pos in possible_positions:
    #             if pos in self._path and pos != self._prec_pos:
    #                 #time.sleep(self.TIMER_DELAY)
    #                 for _ in range(len(self._path) - 1 - self._path.index(pos)):
    #                     self._remove_current_pos()
    #                 return

    def _init_start_and_finish_pos(self):
        for i in range(self._nb_rows_grid):
            for j in range(self._nb_cols_grid):
                match self._grid[i][j]["value"]:
                    case self.START_VALUE:
                        self._start_value_pos = (i, j)
                    case self.FINISH_VALUE:
                        self._finish_value_pos = (i, j)


    def _add_pos(self, pos):
        #time.sleep(self.TIMER_DELAY)
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
        self._grid[pos[0]][pos[1]]["label"].setText("X")

        if not self._prec_pos:
            return

        if self._grid[self._prec_pos[0]][self._prec_pos[1]]["value"] == self.START_VALUE:
            self._grid[self._prec_pos[0]][self._prec_pos[1]]["label"].setText(self.START_LETTER)
        elif not self._grid[self._prec_pos[0]][self._prec_pos[1]]["authorisation"]:
            self._grid[self._prec_pos[0]][self._prec_pos[1]]["label"].setPixmap(QPixmap(self.STONE_IMG))
        else:
            self._grid[self._prec_pos[0]][self._prec_pos[1]]["label"].setText("")

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
        self._grid[self._current_pos[0]][self._current_pos[1]]["label"].setText("X")
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
    app = QtW.QApplication([])
    labyrinth = Labyrinth(grid)
    labyrinth.show()
    app.exec()
