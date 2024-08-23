import sys
import threading
import time
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtGui import QMouseEvent, Qt, QPixmap
from PySide6.QtWidgets import QMainWindow, QSlider, QToolTip, QWidget, QGridLayout, QPushButton, QLabel, QComboBox, \
    QApplication

from data import Grids
from labyrinthe import Labyrinth


class Window(QMainWindow, Labyrinth):
    __WINDOW_TITLE = "Labyrinthe"
    __CMB_BOX_GRID_SIZE_TOOLTIP_LBL = "Taille de la grille"
    __CMB_BOX_GRID_SIZE_FIRST_ITEM_LBL = "Grille"
    __SMALL_GRID_SIZE_LBL = "Petite"
    __MEDIUM_GRID_SIZE_LBL = "Moyenne"
    __LARGE_GRID_SIZE_LBL = "Grande"
    __CMB_BOX_PATH_DISPLAY_TOOLTIP_LBL = "Affichage du chemin"
    __CMB_BOX_PATH_DISPLAY_FIRST_ITEM_LBL = "Chemin"
    __WITHOUT_PATH_DISPLAY_LBL = "Aucun"
    __SHORT_PATH_DISPLAY_LBL = "Optimisé"
    __TOTAL_PATH_DISPLAY_LBL = "Complet"
    __SLIDER_LBL_TEXT = "Délai entre deux déplacements en 1/100èmes de sec"
    __PLAY_LBL = "Play"
    __PAUSE_LBL = "Pause"
    __STOP_LBL = "Stop"
    # _IMG_DIR = "img"
    # _WALL_IMG = "mur.webp"
    # _STONE_IMG = "caillou.png"

    def __init__(self):
        super().__init__()
        Labyrinth().__init__()
        self.__grids_wordings_by_codes = {Grids.SMALL_GRID_SIZE_CODE: self.__SMALL_GRID_SIZE_LBL,
                                          Grids.MEDIUM_GRID_SIZE_CODE: self.__MEDIUM_GRID_SIZE_LBL,
                                          Grids.LARGE_GRID_SIZE_CODE: self.__LARGE_GRID_SIZE_LBL}
        self.__paths_wordings_by_codes = {self._WITHOUT_PATH_DISPLAY_CODE: self.__WITHOUT_PATH_DISPLAY_LBL,
                                          self._TOTAL_PATH_DISPLAY_CODE: self.__TOTAL_PATH_DISPLAY_LBL,
                                          self._SHORT_PATH_DISPLAY_CODE: self.__SHORT_PATH_DISPLAY_LBL}
        self.__display()
        self.__display_grid()
        self.show()

    def __get_label_by_value(self, value: int) -> QLabel:
        label = QLabel()
        match value:
            case self._START_VALUE:
                label.setText(self._START_LETTER)
            case self._FINISH_VALUE:
                label.setText(self._FINISH_LETTER)
            case self._WALL_VALUE:
                label.setPixmap(QPixmap(Path(self._IMG_DIR) / self._WALL_IMG))
        return label

    def __display(self):
        self.setWindowTitle(self.__WINDOW_TITLE)
        # la ligne suivante empêche que la fenêtre prenne tout l'écran si on double-clique dessus
        self.setMaximumSize(1000, 1000)
        toolbar = self.addToolBar("")

        # choix de la grille
        cmbBox_gridSize = QComboBox()
        cmbBox_gridSize.setToolTip(self.__CMB_BOX_GRID_SIZE_TOOLTIP_LBL)
        cmbBox_gridSize.addItem(f"-- {self.__CMB_BOX_GRID_SIZE_FIRST_ITEM_LBL} --")
        cmbBox_gridSize.addItems(list(self.__grids_wordings_by_codes.values()))
        cmbBox_gridSize.setCurrentText(self.__grids_wordings_by_codes[self._grid_size_code])
        cmbBox_gridSize.currentTextChanged.connect(self.__comboBox_gridSizeSlot)
        toolbar.addWidget(cmbBox_gridSize)

        # choix du type d'affichage du parcours
        cmbBox_pathDisplay = QComboBox()
        cmbBox_pathDisplay.setToolTip(self.__CMB_BOX_PATH_DISPLAY_TOOLTIP_LBL)
        cmbBox_pathDisplay.addItem(f"-- {self.__CMB_BOX_PATH_DISPLAY_FIRST_ITEM_LBL} --")
        cmbBox_pathDisplay.addItems(list(self.__paths_wordings_by_codes.values()))
        cmbBox_pathDisplay.setCurrentText(self.__paths_wordings_by_codes[self._path_display_code])
        cmbBox_pathDisplay.currentTextChanged.connect(self.__comboBox_pathDisplaySlot)
        toolbar.addWidget(cmbBox_pathDisplay)

        # affichage de l'intervalle de temps choisi entre deux déplacements
        initial_value = int(self._timer_delay * 100)
        self.__sliderLabel = QLabel(str(initial_value))
        self.__sliderLabel.setFixedSize(20, 10)
        toolbar.addWidget(self.__sliderLabel)

        # choix de l'intervalle de temps entre deux déplacements
        slider = Slider(self.__SLIDER_LBL_TEXT)
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setFixedWidth(100)
        slider.setValue(initial_value)
        slider.valueChanged.connect(self.__slider_slot)
        toolbar.addWidget(slider)

        # bouton "Play"
        self.__buttonPlayPause = QPushButton(self.__PLAY_LBL)
        self.__buttonPlayPause.clicked.connect(self.__button_playPauseSlot)
        toolbar.addWidget(self.__buttonPlayPause)

        buttonStop = QPushButton(self.__STOP_LBL)
        buttonStop.clicked.connect(self.__button_stopSlot)
        toolbar.addWidget(buttonStop)

    def __display_grid(self):
        self._init_grid()
        gridLayout = QGridLayout()
        gridLayout.setSpacing(0)
        gridLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label_size = 30

        for i in range(self._nb_rows_grid):
            for j in range(self._nb_cols_grid):
                # if i == 0:
                #     label = QLabel(str(j))
                #     label.setFixedSize(label_size, label_size)
                #     label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                #     gridLayout.addWidget(label, i, j + 1)
                # if j == 0:
                #     label = QLabel(str(i))
                #     label.setFixedSize(label_size, label_size)
                #     label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                #     gridLayout.addWidget(label, i + 1, j)
                cell = self._grid[i][j]
                cell.label = self.__get_label_by_value(cell.value)
                #label = self._grid[i][j].label
                cell.label.setFixedSize(label_size, label_size)
                cell.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # gridLayout.addWidget(label, i + 1, j + 1)
                gridLayout.addWidget(cell.label, i, j)

        centralWidget = QWidget()
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)

    @Slot()
    def __slider_slot(self):
        delay = self.sender().value()
        self.__sliderLabel.setText(str(delay))
        self._timer_delay = delay / 100

    @Slot()
    def __button_stopSlot(self):
        if self._stop_event:
            self._stop_event.set()
            self.__buttonPlayPause.setText(self.__PLAY_LBL)

    @Slot()
    def __button_playPauseSlot(self):
        # laisser ces deux lignes ici pour le cas où l'on fait "stop" après "pause"
        self._pause_event = threading.Event()
        self._play_event = threading.Event()

        # premier clic sur play
        if not self._thread:
            self.__button_stopSlot()
            self.__display_grid()
            self.__buttonPlayPause.setText(self.__PAUSE_LBL)
            # il faut redéfinir à chaque clic sur play un nouveau thread, car on ne peut pas faire plusieurs start and
            # stop sur un même thread
            self._stop_event = threading.Event()
            self._thread = threading.Thread(target=self.__find_the_exit)
            self._thread.start()
            # self._thread.join()
            # self.__buttonPlayPause.setText(self.__PLAY_LBL)

        # clic sur pause
        elif self.__buttonPlayPause.text() == self.__PAUSE_LBL:
            self.__buttonPlayPause.setText(self.__PLAY_LBL)
            self._pause_event.set()

        # clic sur play après pause
        else:
            self.__buttonPlayPause.setText(self.__PAUSE_LBL)
            self._play_event.set()

    # todo : remettre cette fonction dans la classe Labyrinth
    def __find_the_exit(self):
        next_cell = self._start_cell
        while next_cell:
            if not self._add_cell(next_cell):
                break
            # il faut commenter la ligne suivante en production pour que l'affichage du chemin soit correct dans le cas
            # où le délai du timer est à 0
            # print(self.__current_cell.row_id, self.__current_cell.col_id)
            next_cell = self._get_next_cell()
        self._thread = None
        self.__buttonPlayPause.setText(self.__PLAY_LBL)

    @Slot()
    def __comboBox_pathDisplaySlot(self):
        if (path_display_wording := self.sender().currentText()) not in self.__paths_wordings_by_codes.values():
            return
        self.__path_display_code = self.__get_key_by_value(self.__paths_wordings_by_codes, path_display_wording)
        self._update_styleSheet_path()

    @Slot()
    def __comboBox_gridSizeSlot(self):
        if (grid_size_wording := self.sender().currentText()) not in self.__grids_wordings_by_codes.values():
            return
        # laisser la ligne suivante ici pour que le programme ne s'arrête pas quand on clique sur "Grille"
        self.__button_stopSlot()
        self.__grid_size_code = self.__get_key_by_value(self.__grids_wordings_by_codes, grid_size_wording)
        self.__display_grid()
        # self.adjustSize() permet de redimensionner correctement la fenêtre lorsque l'on choisit une taille de grille
        # inférieure
        self.adjustSize()

    @staticmethod
    def __get_key_by_value(dictionnary: dict, value):
        for k, val in dictionnary.items():
            if value == val:
                return k


class Slider(QSlider):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.__text = text
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent):
        QToolTip.showText(event.globalPosition().toPoint(), self.__text)
        super().mouseMoveEvent(event)


if __name__ == '__main__':
    # Création de l'application
    app = QApplication(sys.argv)
    qss = "labyrinth"
    #qss = "darkorange"

    with open(f"styles/{qss}.qss", "r") as f:
        app.setStyleSheet(f.read())

    window = Window()
    # labyrinth = Labyrinth()
    # labyrinth.show()
    sys.exit(app.exec())
