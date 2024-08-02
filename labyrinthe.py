import random

import colorama


class Labyrinth:

    def __init__(self, grid):
        self._grid = grid
        self._path = []
        self._get_path()
        self._show_grid()

    def _get_path(self):
        # on ajoute la position de départ à la liste
        current_pos = self._get_start_pos()

        while True:
            if current_pos not in self._path:
                self._path.append(current_pos)
            # si la case contient un 3, le programme est terminé
            if self._grid[current_pos[0]][current_pos[1]] == 3:
                return
            # quand on est sur une case, on crée une liste des coordonnées des cases autour qui contiennent un 0 ou un 3
            # et dont la case d'où l'on vient ne fait pas partie
            next_pos = self._get_next_pos(current_pos)
            # s'il n'y a aucune case possible (on est dans un cul-de-sac), on met un 1 sur la case où on est,
            # on la supprime de la liste et on revient en arrière d'une case
            if not next_pos:
                self._grid[current_pos[0]][current_pos[1]] = 1
                self._path.pop()
                current_pos = self._path[-1][0], self._path[-1][1]
            else:
                current_pos = next_pos

    def _get_start_pos(self) -> tuple:
        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                if self._grid[i][j] == 2:
                    return i, j

    def _get_next_pos(self, pos) -> bool | tuple:
        possible_next_pos = ((pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0] + 1, pos[1]), (pos[0], pos[1] - 1))
        final_possible_next_pos = []
        authorized_values = (0, 3)

        for pos in possible_next_pos:
            if (pos not in self._path and
                    pos[0] in range(len(self._grid)) and
                    pos[1] in range(len(self._grid[pos[0]])) and
                    self._grid[pos[0]][pos[1]] in authorized_values):
                final_possible_next_pos.append(pos)

        if len(final_possible_next_pos) == 0:
            return False

        return random.choice(final_possible_next_pos)

    def _show_grid(self):
        draw = ""
        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                value = f"{self._grid[i][j]:^3}"
                if (i, j) in self._path:
                    value = (colorama.Back.LIGHTRED_EX + value + colorama.Style.RESET_ALL)
                draw += value
            draw += "\n"

        print(draw)


if __name__ == '__main__':
    grid = [
        [1, 1, 1, 1, 0, 1, 0, 1, 3, 1],
        [1, 2, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
        [0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 1, 0, 0, 1, 1, 1, 1],
        [1, 1, 0, 1, 1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    ]

    # grid = [
    #     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 2, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 3],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0],
    #     [0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
    # ]

    Labyrinth(grid)