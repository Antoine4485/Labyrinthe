import random
from threading import Thread, Event
import time

from cell import Cell
from data import Grids
from label import Label


class Labyrinth:
    __PATH_VALUE = 0
    __WALL_VALUE = 1
    __START_VALUE = 2
    __FINISH_VALUE = 3
    __AUTHORISED_VALUES = {__PATH_VALUE, __WALL_VALUE, __START_VALUE, __FINISH_VALUE}
    _WITHOUT_PATH_DISPLAY_CODE = "without"
    _SHORT_PATH_DISPLAY_CODE = "short"
    _TOTAL_PATH_DISPLAY_CODE = "total"

    def __init__(self):
        super().__init__()
        self._timer_delay = 0.2
        self._grid_size_code = Grids.SMALL_GRID_SIZE_CODE
        self._path_display_code = self._SHORT_PATH_DISPLAY_CODE
        self._thread: None | Thread = None
        self._play_event: None | Event = None
        self._pause_event: None | Event = None
        self._stop_event: None | Event = None

    def _init_grid(self):
        self._grid = []
        self.__total_path = []
        self.__short_path = []
        self._start_cell: None | Cell = None
        self.__finish_cell: None | Cell = None
        self.__current_cell: None | Cell = None
        if not self.__set_grid():
            exit()
        self._nb_rows_grid = len(self._grid)
        self._nb_cols_grid = len(self._grid[0])
        self.__init_cells_around_cells()

    def __set_grid(self) -> bool:
        grid = Grids().grids[self._grid_size_code]
        if type(grid) is not list:
            return False
        for row_id, row in enumerate(grid):
            if type(row) is not list:
                return False
            self._grid.append([])
            for col_id, value in enumerate(row):
                if type(value) is not int or value not in self.__AUTHORISED_VALUES:
                    return False

                # les cases avec "authorisation" à False sont celles où on ne peut pas aller car il y a un mur ou un
                # caillou dessus. Ces derniers sont éventuellement ajoutés pendant le parcours sur les cases situées
                # dans les culs-de-sacs, en bordure de grille ou dans un "coin ouvert" (deux murs à 90° avec la case
                # opposée dans la diagonale qui est vide afin de ne pas créer un cul-de-sac)
                cell = Cell(row_id=row_id,
                            col_id=col_id,
                            value=value,
                            authorisation=False if value == self.__WALL_VALUE else True,
                            label=self.__get_label_by_value(value))

                self._grid[row_id].append(cell)

                if value == self.__START_VALUE:
                    self._start_cell = cell
                elif value == self.__FINISH_VALUE:
                    self.__finish_cell = cell

        return True

    def __get_label_by_value(self, value: int) -> Label:
        label = Label()
        match value:
            case self.__START_VALUE:
                label.set_start_letter()
            case self.__FINISH_VALUE:
                label.set_finish_letter()
            case self.__WALL_VALUE:
                label.set_wall_img()
        return label

    def __init_cells_around_cells(self):
        # Initialisation, autour de chaque case, des cases selon leur direction, afin de pouvoir par la suite accéder
        # facilement par exemple à la case à gauche de celle à gauche de la case courante, ou à la case à droite de
        # celle à droite de la case courante (en faisant cell.left_cell.left_cell ou cell.right_cell.right_cell)
        for row in self._grid:
            for cell in row:
                self.__current_cell = cell
                self.__current_cell.closest_cells_by_directions = self.__get_closest_cells_by_directions()

    def __get_closest_cells_by_directions(self):
        closest_cells_by_directions = {}

        for direction, pos in self.__current_cell.get_positions_by_directions().items():
            if self.__is_pos_in_grid(pos):
                cell = self._grid[pos[0]][pos[1]]
                closest_cells_by_directions[direction] = cell

        return closest_cells_by_directions

    def __is_pos_in_grid(self, pos: tuple) -> bool:
        return pos[0] in range(self._nb_rows_grid) and pos[1] in range(self._nb_cols_grid)

    def _find_the_exit(self):
        next_cell = self._start_cell
        while next_cell:
            if not self.__add_cell(next_cell):
                break
            # il faut commenter la ligne suivante en production pour que l'affichage du chemin soit correct dans le cas
            # où le délai du timer est à 0
            # print(self.__current_cell.row_id, self.__current_cell.col_id)
            next_cell = self.__get_next_cell()
        self._thread = None

    def __get_next_cell(self) -> None | Cell:
        if not self.__current_cell.authorised_next_cells_by_directions or self.__current_cell == self.__finish_cell:
            return None

        authorised_next_cells = list(self.__current_cell.authorised_next_cells_by_directions.values())

        # si la case finale figure parmi celles possibles, on la choisit
        if self.__finish_cell in authorised_next_cells:
            return self.__finish_cell

        # cas où on est sur la case de départ : on choisit une direction au hasard
        if not self.__current_cell.prec_cell:
            return random.choice(authorised_next_cells)

        # On ne va pas à gauche, sauf si on est dans un couloir et qu'un passage apparaît à gauche. De même pour la
        # droite, on ne va pas à droite sauf si une issue apparaît à droite. Cela permet d'aller tout droit la
        # plupart du temps pour arriver plus vite à la fin.
        if self.__current_cell.is_left_cell_to_remove_from_authorised_next_cells():
            authorised_next_cells.remove(self.__current_cell.left_cell)

        if self.__current_cell.is_right_cell_to_remove_from_authorised_next_cells():
            authorised_next_cells.remove(self.__current_cell.right_cell)

        # s'il y a au moins une case possible en plus de la précédente, on ne revient pas sur cette dernière
        if len(authorised_next_cells) > 1 and self.__current_cell.prec_cell in authorised_next_cells:
            authorised_next_cells.remove(self.__current_cell.prec_cell)

        return random.choice(authorised_next_cells)

    def __update_short_path(self, cell: Cell):
        if cell not in self.__short_path:
            self.__short_path.append(cell)
        elif cell == self.__short_path[-2]:
            self.__remove_cell_from_short_path(with_timer_delay=False)
        # quand on est sur une case, si on a fait une boucle, on l'enlève
        self.__remove_possible_loop_from_short_path()

    def __remove_possible_loop_from_short_path(self):
        index_current_cell = min_index_possible_cell = len(self.__short_path) - 1
        cells = self.__current_cell.h_and_v_closest_cells_by_directions.values()

        for cell in cells:
            if cell in self.__short_path:
                index_cell = self.__short_path.index(cell)
                if index_cell < min_index_possible_cell:
                    min_index_possible_cell = index_cell

        if index_current_cell - min_index_possible_cell < 3:
            return

        # on crée une liste de cellules à supprimer car on ne peut pas les supprimer via leur index en bouclant
        # directement sur self.__short_path
        cells_to_remove = []
        for i in range(min_index_possible_cell + 1, index_current_cell):
            cells_to_remove.append(self.__short_path[i])

        for cell in reversed(cells_to_remove):
            self.__remove_cell_from_short_path(cell=cell, with_timer_delay=False)

    def __add_cell(self, cell: Cell) -> bool:
        if not self.__timer():
            return False

        cell.prec_cell = self.__current_cell
        if self._path_display_code != self._WITHOUT_PATH_DISPLAY_CODE:
            cell.label.set_bg_color_of_cell_in_path()
        cell.label.set_person_img()
        self.__total_path.append(cell)
        self.__current_cell = cell

        # cas où on met un caillou sur la case pour ne pas y revenir
        if self.__current_cell.is_in_cul_de_sac() or self.__current_cell.is_in_open_corner():
            self.__current_cell.authorisation = False

        self.__update_short_path(cell)
        if not cell.prec_cell:
            return False

        label = cell.prec_cell.label
        if cell.prec_cell == self._start_cell:
            label.set_start_letter()
        elif not cell.prec_cell.authorisation:
            label.set_stone_img()
        else:
            label.remove_img()
        return True

    def __remove_cell_from_short_path(self, cell: None | Cell = None, with_timer_delay=True):
        if with_timer_delay:
            self.__timer()
        # s'il n'y a qu'un élément c'est forcément le point de départ, donc on ne l'enlève pas
        if len(self.__short_path) == 1:
            return
        if not cell:
            cell = self.__short_path[-1]
        self.__short_path.remove(cell)
        if self._path_display_code != self._TOTAL_PATH_DISPLAY_CODE:
            cell.label.set_default_bg_color()

    def _update_styleSheet_path(self):
        for cell in self.__total_path:
            if self._path_display_code == self._WITHOUT_PATH_DISPLAY_CODE or \
                    self._path_display_code == self._SHORT_PATH_DISPLAY_CODE and cell not in self.__short_path:
                cell.label.set_default_bg_color()
            else:
                cell.label.set_bg_color_of_cell_in_path()

    def __timer(self) -> bool:
        if self._timer_delay > 0:
            time.sleep(self._timer_delay)

        # on gère ici les events plutôt que dans la fonction __find_the_exit() afin que le curseur s'arrête dès le clic
        # sur les boutons "Pause" ou "Stop" et qu'il n'y ait pas une case en plus d'ajoutée au chemin
        if self._stop_event.is_set():
            return False

        while self._pause_event and self._pause_event.is_set() and not self._play_event.is_set():
            time.sleep(0.1)
            if self._stop_event.is_set():
                return False

        return True