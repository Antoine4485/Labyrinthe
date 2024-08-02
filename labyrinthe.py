import random

labyrinthe = [
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

# labyrinthe = [
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


def affiche_labyrinthe(labyrinthe):
    draw = ""
    for row in labyrinthe:
        draw += " ".join(map(str, row)) + "\n"
    print(draw)


def get_pos_depart() -> tuple:
    for i in range(len(labyrinthe)):
        for j in range(len(labyrinthe[i])):
            if labyrinthe[i][j] == 2:
                return i, j


def get_next_pos(pos, path) -> bool | tuple:
    four_possible_next_pos = ((pos[0] - 1, pos[1]), (pos[0], pos[1] + 1), (pos[0] + 1, pos[1]), (pos[0], pos[1] - 1))
    possible_next_pos = []
    authorized_values = (0, 3)

    for pos in four_possible_next_pos:
        if (pos not in path and
                pos[0] in range(len(labyrinthe)) and
                pos[1] in range(len(labyrinthe[pos[0]])) and
                labyrinthe[pos[0]][pos[1]] in authorized_values):
            possible_next_pos.append(pos)

    if len(possible_next_pos) == 0:
        return False
    return random.choice(possible_next_pos)


def sortir_labyrinthe(labyrinthe) -> bool | list:
    affiche_labyrinthe(labyrinthe)
    path = []
    # on ajoute la position de départ à la liste
    current_pos = get_pos_depart()

    while True:
        if current_pos not in path:
            path.append(current_pos)
        # si la case contient un 3, le programme est terminé
        if labyrinthe[current_pos[0]][current_pos[1]] == 3:
            return path
        # quand on est sur une case, on crée une liste des coordonnées des cases autour qui contiennent un 0 ou un 3
        # et dont la case d'où l'on vient ne fait pas partie
        next_pos = get_next_pos(current_pos, path)
        # s'il n'y a aucune case possible (on est dans un cul-de-sac), on met un 1 sur la case où on est,
        # on la supprime de la liste et on revient en arrière d'une case
        if not next_pos:
            labyrinthe[current_pos[0]][current_pos[1]] = 1
            path.pop()
            current_pos = path[-1][0], path[-1][1]
        else:
            current_pos = next_pos


if __name__ == '__main__':
    print(sortir_labyrinthe(labyrinthe))