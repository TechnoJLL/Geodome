import dome
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QSpinBox, QGroupBox, QPushButton, QButtonGroup, QMessageBox, QProgressBar
)
import sys

class WorkerThread(QThread):
    progress_started = pyqtSignal()
    progress_finished = pyqtSignal(int, int, int, np.ndarray)

    def __init__(self, poly:int, freq:int, classe:int):
        super().__init__()
        self.poly = poly
        self.freq = freq
        self.classe = classe

    def run(self) -> None:
        self.progress_started.emit()
        pts_arr = dome.nuage_pts(self.poly, self.freq, self.classe)
        self.progress_finished.emit(self.poly, self.freq, self.classe, pts_arr)

class MatplotlibWidget(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8,8))
        self.ax = self.fig.add_subplot(111, projection='3d')  # Graphique 3D
        self.ax.set_box_aspect((1,1,1))
        super().__init__(self.fig)
        self.setParent(parent)

    def plot(self, poly:int, freq:int, classe:int, pts_arr: np.ndarray) -> None:
        self.ax.clear()  # Efface le graphique précédent

        u = np.linspace(0, 2*np.pi, 40)
        v = np.linspace(0, np.pi, 20)
        x_s = np.outer(np.cos(u), np.sin(v))
        y_s = np.outer(np.sin(u), np.sin(v))
        z_s = np.outer(np.ones_like(u), np.cos(v))
        self.ax.plot_wireframe(x_s, y_s, z_s, color='lightgray', alpha=0.5)

        self.ax.scatter(pts_arr[:,0], pts_arr[:,1], pts_arr[:,2], color='red', s=10)

        for i, j in dome.edges(pts_arr):
            xs, ys, zs = zip(pts_arr[i], pts_arr[j])
            self.ax.plot(xs, ys, zs, color='blue')

        self.ax.set_title(f"{dome.Nedres[poly]} subdivisé, classe {classe}, freq {freq}")
        self.draw()

class PolyhedronConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration du Polyèdre / Division")

        # Conteneur principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Disposition horizontale
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Menu des paramètres (à gauche)
        menu_layout = QVBoxLayout()
        menu_container = QWidget()
        menu_container.setLayout(menu_layout)
        menu_container.setFixedWidth(200)  # Largeur fixe minimale
        main_layout.addWidget(menu_container)

        # Choix du polyèdre
        poly_label = QLabel("Choix du polyèdre:")
        menu_layout.addWidget(poly_label)

        self.poly_group = QButtonGroup(self)
        poly_layout = QVBoxLayout()
        for nedre,label in dome.Nedres.items():
            radio = QRadioButton(label)
            self.poly_group.addButton(radio, nedre)
            if nedre == list(dome.Nedres)[0]:
                radio.setChecked(True)
            poly_layout.addWidget(radio)
        menu_layout.addLayout(poly_layout)

        # Paramètre de division
        div_group = QGroupBox("Division")
        div_layout = QVBoxLayout(div_group)
        menu_layout.addWidget(div_group)

        freq_layout = QHBoxLayout()
        freq_label = QLabel("Fréquence:")
        freq_layout.addWidget(freq_label)

        self.freq_input = QSpinBox()
        self.freq_input.setValue(1)
        self.freq_input.setMinimum(1)
        self.freq_input.setFixedWidth(50)
        freq_layout.addWidget(self.freq_input)
        div_layout.addLayout(freq_layout)

        # Choix de la classe
        class_layout = QVBoxLayout()
        self.class_group = QButtonGroup(self)

        class1_radio = QRadioButton("Classe 1")
        class1_radio.setChecked(True)
        self.class_group.addButton(class1_radio, 1)
        class_layout.addWidget(class1_radio)

        class2_radio = QRadioButton("Classe 2")
        self.class_group.addButton(class2_radio, 2)
        class_layout.addWidget(class2_radio)

        div_layout.addLayout(class_layout)

        # Bouton de mise à jour
        update_button = QPushButton("Générer")
        update_button.clicked.connect(self.show_selection_and_run)
        menu_layout.addWidget(update_button)

        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0,1)
        menu_layout.addWidget(self.progressBar)

        # Widget de visualisation
        self.visualization_widget = MatplotlibWidget()
        main_layout.addWidget(self.visualization_widget)
    
        self.worker_thread = None
        self.show_selection_and_run()

    def show_selection_and_run(self):
        poly = self.poly_group.checkedId()
        classe = self.class_group.checkedId()
        freq = self.freq_input.value()

        if classe == 2 and freq % 2 != 0:
            QMessageBox.warning(self, "Erreur", "Classe 2 requiert une fréquence paire.")
            return
        
        self.worker_thread = WorkerThread(poly, freq, classe)
        self.worker_thread.progress_started.connect(self.on_progress_started)
        self.worker_thread.progress_finished.connect(self.on_progress_finished)
        self.worker_thread.start()

    def on_progress_started(self):
        self.progressBar.setRange(0, 0)

    def on_progress_finished(self, poly, freq, classe, pts_arr):
        self.progressBar.setRange(0, 1)
        self.visualization_widget.plot(poly, freq, classe, pts_arr)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PolyhedronConfigWindow()
    window.show()
    sys.exit(app.exec_())
