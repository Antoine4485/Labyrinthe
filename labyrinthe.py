import copy
import random
import threading
import time

from PySide6 import QtWidgets as QtW, QtCore
from PySide6.QtGui import QPixmap


class Labyrinth(QtW.QWidget):

    def __init__(self, grid):
        super().__init__()
        self._path_value = 0
        self._wall_value = 1
        self._start_value = 2
        self._finish_value = 3
        self._timer_delay = 0.2
        # grille pour l'affichage
        self._grid = [[{"value": value,
                        "authorisation": False if value == self._wall_value else True,
                        "label": self._get_label_by_value(value)} for value in row] for row in grid]

        #self._initial_grid = grid
        # grille pour les traitements (les valeurs de cette grille sont modifiées dans les "culs-de-sacs" pour ne pas
        # y retourner si on y est allé une fois)
        #self._grid = copy.deepcopy(grid)
        self._path = []
        #self.labels = []
        self._show_grid()

    def _get_label_by_value(self, value):
        label = QtW.QLabel()

        match value:
            case self._start_value:
                label.setText("D")
            case self._finish_value:
                label.setText("A")
            case self._wall_value:
                label.setPixmap(QPixmap('mur.webp'))

        return label

    # def _get_cell_text_by_value(self, value):
    #     match value:
    #         case self._start_value:
    #             return "D"
    #         case self._finish_value:
    #             return "A"
    #     return ""

    def _get_and_show_path(self):
        # on ajoute la position de départ à la liste
        self._init_start_pos()

        while True:
            # quand on est sur une case, on crée une liste des coordonnées des cases autour qui contiennent un 0 ou un 3
            # et dont la case d'où l'on vient ne fait pas partie
            #next_pos = self._get_next_pos()
            # s'il n'y a aucune case possible (on est dans un cul-de-sac), on met un 1 sur la case où on est pour ne pas
            # y retourner, on la supprime de la liste et on revient en arrière d'une case
            self._timer()
            possible_next_positions = self._get_possible_next_positions()
            prec_pos = self._path[-2] if len(self._path) > 1 else None
            #if (pos != prec_pos):
            match len(possible_next_positions):
                case 0:
                    return
                case 1:
                    next_pos = possible_next_positions[0]
                    current_pos = self._path[-1]
                    self._grid[current_pos[0]][current_pos[1]]["authorisation"] = False
                    # cas où on est dans un cul-de-sac
                    if next_pos == prec_pos:
                        self._remove_last_pos()
                        continue
                #case 2:
                    # s'il y a deux possibilités (avancer ou reculer), on avance
                    # index_prec_pos = possible_next_positions.index(prec_pos)
                    # index_next_pos = int(not index_prec_pos)
                    # next_pos = possible_next_positions[index_next_pos]
                case _:
                    if prec_pos in possible_next_positions:
                        possible_next_positions.remove(prec_pos)
                    #possible_next_positions.remove(prec_pos)
                    #index_prec_pos = possible_next_positions.index(prec_pos)
                    next_pos = random.choice(possible_next_positions)

            # if len(possible_next_positions) == 0:
            #     return
            #
            # elif len(possible_next_positions) == 1:
            #     next_pos = possible_next_positions[0]
            #     self._timer()
            #     current_pos = self._path[-1]
            #     self._grid[current_pos[0]][current_pos[1]]["authorisation"] = False
            #     # cas où on est dans un cul-de-sac
            #     if next_pos == prec_pos:
            #         self._remove_last_pos()
            #         continue
            #     # current_pos = self._path[-1]
            #     # self.labels[current_pos[0]][current_pos[1]].setPixmap(QPixmap('bb.png'))
            #
            # elif len(possible_next_positions) == 2:
            #     index_prec_pos = possible_next_positions.index(prec_pos)
            #     index_next_pos = int(not index_prec_pos)
            #     next_pos = possible_next_positions[index_next_pos]
            #     #current_pos = self._path[-1]
            #     #self._grid[current_pos[0]][current_pos[1]]["authorisation"] = False
            # else:
            #     next_pos = random.choice(possible_next_positions)

            # if not next_pos:
            #     self._timer()
            #     current_pos = self._path[-1]
            #     self._grid[current_pos[0]][current_pos[1]]["authorisation"] = False
            #     self._remove_last_pos()
            #     # current_pos = self._path[-1]
            #     # self.labels[current_pos[0]][current_pos[1]].setPixmap(QPixmap('bb.png'))
            #     continue
            self._add_pos(next_pos)
            # si la case contient le 3, le programme est terminé
            if self._grid[next_pos[0]][next_pos[1]]["value"] == self._finish_value:
                return

    def _init_start_pos(self):
        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                if self._grid[i][j]["value"] == self._start_value:
                    self._add_pos((i, j))
                    return

    # def _remove_possible_loop(self):
    #     if len(self._path) > 1:
    #         for pos in self._get_closest_positions():
    #             if pos in self._path and pos != self._path[-2]:
    #                 self._timer()
    #                 for _ in range(len(self._path) - 1 - self._path.index(pos)):
    #                     self._remove_last_pos()
    #                 return

    def _add_pos(self, pos):
        self._timer()
        if len(self._path) > 0:
            current_pos = self._path[-1]
            current_label = self._grid[current_pos[0]][current_pos[1]]["label"]
            #label_text = current_label.text()
            current_label.clear()
            if self._grid[current_pos[0]][current_pos[1]]["value"] == self._start_value:
                current_label.setText("D")
            #self.labels[current_pos[0]][current_pos[1]].setStyleSheet(f"background-color: rgb(200, 200, 200);")
        self._path.append(pos)
        self._grid[pos[0]][pos[1]]["label"].setPixmap(QPixmap('bb.png'))
        #self.labels[pos[0]][pos[1]].setPixmap(QPixmap())
        #self.labels[pos[0]][pos[1]].setStyleSheet(f"background-color: rgb(200, 200, 200);")

    def _remove_last_pos(self):
        self._timer()
        # s'il n'y a qu'un élément c'est forcément le point de départ, donc on ne l'enlève pas
        if len(self._path) == 1:
            return
        pos = self._path.pop()
        label = self._grid[pos[0]][pos[1]]["label"]
        label.clear()
        if self._grid[pos[0]][pos[1]]["value"] == self._start_value:
            label.setText("D")
        if len(self._path) > 0:
            last_pos = self._path[-1]
            self._grid[last_pos[0]][last_pos[1]]["label"].setPixmap(QPixmap('bb.png'))
        #self.labels[pos[0]][pos[1]].setStyleSheet(f"background-color: none;")

    def _get_possible_next_positions(self):
        final_possible_next_pos = []
        #prec_pos = self._path[-2] if len(self._path) > 1 else None

        for pos in self._get_closest_positions():
            #if (pos != prec_pos and
            if (pos[0] in range(len(self._grid)) and
                    pos[1] in range(len(self._grid[pos[0]])) and
                    self._grid[pos[0]][pos[1]]["authorisation"] is True):
                final_possible_next_pos.append(pos)

        return final_possible_next_pos

    def _get_next_pos(self) -> None | tuple:
        final_possible_next_pos = []
        prec_pos = self._path[-2] if len(self._path) > 1 else None

        for pos in self._get_closest_positions():
            if (pos != prec_pos and
                    pos[0] in range(len(self._grid)) and
                    pos[1] in range(len(self._grid[pos[0]])) and
                    self._grid[pos[0]][pos[1]]["authorisation"] is True):
                final_possible_next_pos.append(pos)

        if len(final_possible_next_pos) == 0:
            return None

        return random.choice(final_possible_next_pos)

    def _show_grid(self):
        #self.setGeometry(0, 0, 400, 300)
        self.setWindowTitle("Labyrinthe")
        grid_layout = QtW.QGridLayout()
        grid_layout.setSpacing(0)
        # Création d'un groupe de widgets
        group = QtW.QGroupBox()

        #self.labels = [[QtW.QLabel() for _ in range(len(self._initial_grid[i]))] for i in range(len(self._initial_grid))]

        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                label = self._grid[i][j]["label"]
                label.setFixedSize(30, 30)
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                grid_layout.addWidget(label, i, j)

        # On définit la grille comme disposition du groupe
        group.setLayout(grid_layout)
        #group.setFixedSize(250, 250)
        #group.setStyleSheet("padding: 20px;")
        # Création d'une disposition verticale QVBox
        layout = QtW.QVBoxLayout()

        #layout.setSpacing(100)
        # On ajoute les widgets créé à la disposition
        # Le champ edit sera donc au-dessus du bouton
        layout.addWidget(group)
        self.setLayout(layout)
        #self.setStyleSheet("padding: 20px;")
        threading.Thread(target=self._get_and_show_path).start()

    def _get_closest_positions(self):
        current_pos = self._path[-1]
        return ((current_pos[0] - 1, current_pos[1]),
                (current_pos[0], current_pos[1] + 1),
                (current_pos[0] + 1, current_pos[1]),
                (current_pos[0], current_pos[1] - 1))

    def _timer(self):
        time.sleep(self._timer_delay)


if __name__ == '__main__':
    # grid = [
    #     [1, 1, 1, 1, 0, 1, 0, 1, 3, 1],
    #     [1, 2, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    #     [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
    #     [0, 1, 0, 1, 0, 0, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 1, 0, 1, 0, 0, 0],
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

    grid = [
        [1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
        [0, 1, 2, 1, 0, 0, 0, 0, 0, 3],
        [0, 1, 0, 1, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 1, 1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    ]

    grid = [
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 2, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 3],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
    ]

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
    #     [1, 2, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
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
