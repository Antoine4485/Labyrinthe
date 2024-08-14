from PySide6 import QtWidgets


class Cell:
    __NORTH_CODE = "N"
    __EAST_CODE = "E"
    __SOUTH_CODE = "S"
    __WEST_CODE = "W"
    __STRAIGHT_DIRECTIONS = {__NORTH_CODE, __EAST_CODE, __SOUTH_CODE, __WEST_CODE}
    __NORTH_EAST_CODE = __NORTH_CODE + __EAST_CODE
    __SOUTH_EAST_CODE = __SOUTH_CODE + __EAST_CODE
    __SOUTH_WEST_CODE = __SOUTH_CODE + __WEST_CODE
    __NORTH_WEST_CODE = __NORTH_CODE + __WEST_CODE
    __DIAGONAL_DIRECTIONS = {__NORTH_EAST_CODE, __SOUTH_EAST_CODE, __SOUTH_WEST_CODE, __NORTH_WEST_CODE}

    def __init__(self, row_id: int, col_id: int, value: int, authorisation: bool, label: QtWidgets.QLabel):
        self.__row_id = row_id
        self.__col_id = col_id
        self.__value = value
        self.__authorisation = authorisation
        self.__label = label
        self.__direction = ""
        self.__prec_cell: None | Cell = None
        self.__left_cell: None | Cell = None
        self.__right_cell: None | Cell = None
        self.__straight_cells = {}
        self.__diagonal_cells = {}

    def get_straight_positions_by_directions(self) -> dict:
        return {
            self.__NORTH_CODE: (self.__row_id - 1, self.col_id),
            self.__EAST_CODE: (self.__row_id, self.col_id + 1),
            self.__SOUTH_CODE: (self.__row_id + 1, self.col_id),
            self.__WEST_CODE: (self.__row_id, self.col_id - 1)
        }

    def get_diagonal_positions_by_directions(self) -> dict:
        return {
            self.__NORTH_EAST_CODE: (self.__row_id - 1, self.col_id + 1),
            self.__SOUTH_EAST_CODE: (self.__row_id + 1, self.col_id + 1),
            self.__SOUTH_WEST_CODE: (self.__row_id + 1, self.col_id - 1),
            self.__NORTH_WEST_CODE: (self.__row_id - 1, self.col_id - 1)
        }

    def get_left_direction(self) -> str:
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

    def get_right_direction(self) -> str:
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

    @staticmethod
    def get_opposite_directions(direction: str) -> None | set:
        if direction not in Cell.__DIAGONAL_DIRECTIONS:
            return None
        return set(Cell.__STRAIGHT_DIRECTIONS - {direction[0], direction[1]})

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
        return self.__left_cell

    @left_cell.setter
    def left_cell(self, left_cell):
        self.__left_cell = left_cell

    @property
    def right_cell(self):
        return self.__right_cell

    @right_cell.setter
    def right_cell(self, right_cell):
        self.__right_cell = right_cell

    @property
    def straight_cells(self):
        return self.__straight_cells

    @straight_cells.setter
    def straight_cells(self, straight_cells):
        self.__straight_cells = straight_cells

    @property
    def diagonal_cells(self):
        return self.__diagonal_cells

    @diagonal_cells.setter
    def diagonal_cells(self, diagonal_cells):
        self.__diagonal_cells = diagonal_cells