from PySide6 import QtWidgets


class Cell:
    __NORTH_CODE = "N"
    __EAST_CODE = "E"
    __SOUTH_CODE = "S"
    __WEST_CODE = "W"
    __H_AND_V_DIRECTIONS = {__NORTH_CODE, __EAST_CODE, __SOUTH_CODE, __WEST_CODE}
    __NORTH_EAST_CODE = __NORTH_CODE + __EAST_CODE
    __SOUTH_EAST_CODE = __SOUTH_CODE + __EAST_CODE
    __SOUTH_WEST_CODE = __SOUTH_CODE + __WEST_CODE
    __NORTH_WEST_CODE = __NORTH_CODE + __WEST_CODE
    __DIAGONAL_DIRECTIONS = {__NORTH_EAST_CODE, __SOUTH_EAST_CODE, __SOUTH_WEST_CODE, __NORTH_WEST_CODE}

    def __init__(self, row_id: int, col_id: int, value: int, authorisation: bool):
        self.__row_id = row_id
        self.__col_id = col_id
        self.__value = value
        self.__authorisation = authorisation
        self.__label: None | QtWidgets.QLabel = None
        self.__direction = ""
        self.__prec_cell: None | Cell = None
        self.__left_cell: None | Cell = None
        self.__right_cell: None | Cell = None
        self.__closest_cells_by_directions = {}

    def get_positions_by_directions(self) -> dict[str: tuple]:
        return {
            self.__NORTH_CODE: (self.__row_id - 1, self.col_id),
            self.__EAST_CODE: (self.__row_id, self.col_id + 1),
            self.__SOUTH_CODE: (self.__row_id + 1, self.col_id),
            self.__WEST_CODE: (self.__row_id, self.col_id - 1),
            self.__NORTH_EAST_CODE: (self.__row_id - 1, self.col_id + 1),
            self.__SOUTH_EAST_CODE: (self.__row_id + 1, self.col_id + 1),
            self.__SOUTH_WEST_CODE: (self.__row_id + 1, self.col_id - 1),
            self.__NORTH_WEST_CODE: (self.__row_id - 1, self.col_id - 1)
        }

    def __get_left_direction(self) -> str:
        match self.direction:
            case self.__NORTH_CODE:
                return self.__WEST_CODE
            case self.__EAST_CODE:
                return self.__NORTH_CODE
            case self.__SOUTH_CODE:
                return self.__EAST_CODE
            case self.__WEST_CODE:
                return self.__SOUTH_CODE
            case _:
                return ""

    def __get_right_direction(self) -> str:
        match self.direction:
            case self.__NORTH_CODE:
                return self.__EAST_CODE
            case self.__EAST_CODE:
                return self.__SOUTH_CODE
            case self.__SOUTH_CODE:
                return self.__WEST_CODE
            case self.__WEST_CODE:
                return self.__NORTH_CODE
            case _:
                return ""

    def is_in_cul_de_sac(self) -> bool:
        return len(self.authorised_next_cells_by_directions) == 1

    def is_in_open_corner(self) -> bool:
        # un coin "ouvert" est un coin qui n'est pas dans un couloir large d'une seule case
        for direction, cell in self.diagonal_closest_cells_by_directions.items():
            if cell.authorisation and self.__is_diagonal_direction_in_front_of_corner(direction):
                return True
        return False

    def __is_diagonal_direction_in_front_of_corner(self, direction: str) -> bool:
        for opposite_direction in self.__get_opposite_directions(direction):
            if opposite_direction not in self.h_and_v_closest_cells_by_directions:
                continue
            opposite_cell = self.h_and_v_closest_cells_by_directions[opposite_direction]
            if opposite_cell.authorisation:
                return False
        return True

    def is_left_cell_to_remove_from_authorised_next_cells(self) -> bool:
        if (self.direction in self.authorised_next_cells_by_directions and
                self.left_cell and
                self.left_cell.authorisation and
                self.left_cell.left_cell and
                ((self.left_cell.left_cell != self.prec_cell.prec_cell and
                  self.left_cell.left_cell.authorisation) or
                 self.left_cell.left_cell == self.prec_cell.prec_cell)):
            return True
        return False

    def is_right_cell_to_remove_from_authorised_next_cells(self) -> bool:
        if (self.direction in self.authorised_next_cells_by_directions and
                self.right_cell and
                self.right_cell.authorisation and
                self.right_cell.right_cell and
                ((self.right_cell.right_cell != self.prec_cell.prec_cell and
                  self.right_cell.right_cell.authorisation) or
                 self.right_cell.right_cell == self.prec_cell.prec_cell)):
            return True
        return False

    def __get_closest_cell(self, direction):
        cell: None | Cell = self.closest_cells_by_directions.get(direction)
        return cell

    @staticmethod
    def __get_opposite_directions(direction: str) -> None | set:
        if direction not in Cell.__DIAGONAL_DIRECTIONS:
            return None
        return set(Cell.__H_AND_V_DIRECTIONS - {direction[0], direction[1]})

    @property
    def row_id(self):
        return self.__row_id

    @row_id.setter
    def row_id(self, row_id):
        self.__row_id = row_id

    @property
    def col_id(self):
        return self.__col_id

    @col_id.setter
    def col_id(self, col_id):
        self.__col_id = col_id

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def authorisation(self):
        return self.__authorisation

    @authorisation.setter
    def authorisation(self, authorisation):
        self.__authorisation = authorisation

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, direction):
        self.__direction = direction

    @property
    def prec_cell(self):
        return self.__prec_cell

    @prec_cell.setter
    def prec_cell(self, prec_cell):
        self.__prec_cell = prec_cell

    @property
    def left_cell(self):
        return self.__get_closest_cell(self.__get_left_direction())

    @property
    def right_cell(self):
        return self.__get_closest_cell(self.__get_right_direction())

    @property
    def closest_cells_by_directions(self):
        return self.__closest_cells_by_directions

    @closest_cells_by_directions.setter
    def closest_cells_by_directions(self, closest_cells):
        self.__closest_cells_by_directions = closest_cells

    @property
    def h_and_v_closest_cells_by_directions(self):
        h_and_v_closest_cells_by_directions = {}

        for direction, cell in self.closest_cells_by_directions.items():
            if direction in self.__H_AND_V_DIRECTIONS:
                cell.direction = direction
                h_and_v_closest_cells_by_directions[direction] = cell

        return h_and_v_closest_cells_by_directions

    @property
    def diagonal_closest_cells_by_directions(self):
        return {direction: cell for direction, cell in self.closest_cells_by_directions.items()
                if direction in self.__DIAGONAL_DIRECTIONS}

    @property
    def authorised_next_cells_by_directions(self):
        return {direction: cell for direction, cell in self.h_and_v_closest_cells_by_directions.items()
                if cell.authorisation}
