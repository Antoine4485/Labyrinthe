import copy
import random
import threading
import time

from PySide6 import QtWidgets as QtW, QtCore


class Labyrinth(QtW.QWidget):

    def __init__(self, grid):
        super().__init__()
        # grille pour l'affichage
        self._initial_grid = grid
        # grille pour les traitements (les valeurs de cette grille sont modifiées dans les "culs-de-sacs" pour ne pas
        # y retourner si on y est allé une fois)
        self._grid = copy.deepcopy(grid)
        self._path = []
        self._show_grid()

    def _get_and_show_path(self):
        # on ajoute la position de départ à la liste
        self._init_start_pos()

        while True:
            # quand on est sur une case, on crée une liste des coordonnées des cases autour qui contiennent un 0 ou un 3
            # et dont la case d'où l'on vient ne fait pas partie
            next_pos = self._get_next_pos()
            # s'il n'y a aucune case possible (on est dans un cul-de-sac), on met un 1 sur la case où on est pour ne pas
            # y retourner, on la supprime de la liste et on revient en arrière d'une case
            if not next_pos:
                time.sleep(0.2)
                current_pos = self._path[-1]
                self._grid[current_pos[0]][current_pos[1]] = 1
                self._remove_last_pos()
                continue
            self._add_pos(next_pos)
            # si la case contient le 3, le programme est terminé
            if self._grid[next_pos[0]][next_pos[1]] == 3:
                return
            # on supprime une éventuelle boucle (si on a "tourné en rond")
            self._remove_possible_loop()

    def _init_start_pos(self):
        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                if self._grid[i][j] == 2:
                    self._add_pos((i, j))
                    return

    def _remove_possible_loop(self):
        if len(self._path) > 1:
            for pos in self._get_closest_positions():
                if pos in self._path and pos != self._path[-2]:
                    time.sleep(0.2)
                    len_path = len(self._path)
                    index_pos = self._path.index(pos)
                    for _ in range(len_path - 1 - index_pos):
                        self._remove_last_pos()
                    return

    def _add_pos(self, pos):
        time.sleep(0.2)
        self._path.append(pos)
        self.labels[pos[0]][pos[1]].setStyleSheet(f"background-color: red;")

    def _remove_last_pos(self):
        pos = self._path.pop()
        self.labels[pos[0]][pos[1]].setStyleSheet(f"background-color: none;")

    def _get_next_pos(self) -> None | tuple:
        final_possible_next_pos = []
        authorized_values = (0, 3)

        for pos in self._get_closest_positions():
            if (pos not in self._path and
                    pos[0] in range(len(self._grid)) and
                    pos[1] in range(len(self._grid[pos[0]])) and
                    self._grid[pos[0]][pos[1]] in authorized_values):
                final_possible_next_pos.append(pos)

        if len(final_possible_next_pos) == 0:
            return None

        return random.choice(final_possible_next_pos)

    def _show_grid(self):
        #self.setGeometry(0, 0, 400, 300)
        self.setWindowTitle("Labyrinthe")
        grid_layout = QtW.QGridLayout()
        # Création d'un groupe de widgets
        group = QtW.QGroupBox()

        self.labels = [[QtW.QLabel() for _ in range(len(self._initial_grid[i]))] for i in range(len(self._initial_grid))]

        for i in range(len(self._initial_grid)):
            for j in range(len(self._initial_grid[i])):
                label = QtW.QLabel(str(self._initial_grid[i][j]))
                label.setFixedSize(30, 30)
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.labels[i][j] = label
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

    # Création de l'application
    app = QtW.QApplication([])
    labyrinth = Labyrinth(grid)
    labyrinth.show()
    app.exec()