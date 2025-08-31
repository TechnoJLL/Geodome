import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from gen_poly_pts import generate_vertices
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QLineEdit, QGroupBox, QPushButton, QButtonGroup
)
import sys

def cartesian_to_spherical(x, y, z):
    # Limiter z à la plage [-1, 1] pour éviter l'erreur math domain error
    z = max(-1.0, min(1.0, z))
    
    theta = math.acos(z)
    phi = math.atan2(y, x)
    if phi < 0:
        phi += 2 * math.pi
    return phi, theta, 1.0

def subdivide_triangle(A, B, C, freq):
    pts = {}
    for i in range(freq+1):
        for j in range(freq+1-i):
            k = freq - i - j
            wA, wB, wC = i / freq if freq else 1, j / freq if freq else 0, k / freq if freq else 0
            P = (A[0]*wA + B[0]*wB + C[0]*wC,
                 A[1]*wA + B[1]*wB + C[1]*wC,
                 A[2]*wA + B[2]*wB + C[2]*wC)
            norm = math.sqrt(P[0]**2 + P[1]**2 + P[2]**2)
            pts[(i,j)] = (P[0]/norm, P[1]/norm, P[2]/norm)
    return pts.values()

def plot_with_division(verts, faces, freq, classe, title):
    points = list(verts)
    for tri in faces:
        A, B, C = [verts[i] for i in tri]
        for P in subdivide_triangle(A, B, C, freq):
            # Convertir P en tuple pour la comparaison
            P_tuple = tuple(P)
            # Vérifier si P est déjà dans les points en tenant compte des tolérances de comparaison
            if not any(np.allclose(P_tuple, tuple(existing_point)) for existing_point in points):
                points.append(P)

    pts_arr = np.array(points, dtype=float)
    hull = ConvexHull(pts_arr)

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_box_aspect((1,1,1))

    u = np.linspace(0, 2*np.pi, 40)
    v = np.linspace(0, np.pi, 20)
    x_s = np.outer(np.cos(u), np.sin(v))
    y_s = np.outer(np.sin(u), np.sin(v))
    z_s = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x_s, y_s, z_s, color='lightgray', alpha=0.5)

    ax.scatter(pts_arr[:,0], pts_arr[:,1], pts_arr[:,2], color='red', s=10)

    edges = set()
    for simplex in hull.simplices:
        i, j, k = simplex
        edges.update({tuple(sorted((i,j))), tuple(sorted((j,k))), tuple(sorted((k,i)))})

    for i, j in edges:
        xs, ys, zs = zip(pts_arr[i], pts_arr[j])
        ax.plot(xs, ys, zs, color='blue')

    ax.set_title(title)
    plt.show()

class PolyhedronConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration du Polyèdre / Division")

        # Conteneur principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Choix du polyèdre
        poly_label = QLabel("Choix du polyèdre:")
        main_layout.addWidget(poly_label)

        self.poly_group = QButtonGroup(self)
        poly_layout = QVBoxLayout()
        for p in ("Tétraèdre", "Octaèdre", "Icosaèdre"):
            radio = QRadioButton(p)
            self.poly_group.addButton(radio)
            poly_layout.addWidget(radio)
        main_layout.addLayout(poly_layout)

        # Paramètre de division
        div_group = QGroupBox("Division")
        div_layout = QVBoxLayout(div_group)
        main_layout.addWidget(div_group)

        freq_layout = QHBoxLayout()
        freq_label = QLabel("Fréquence:")
        freq_layout.addWidget(freq_label)

        self.freq_input = QLineEdit()
        self.freq_input.setText("1")
        self.freq_input.setFixedWidth(50)
        freq_layout.addWidget(self.freq_input)
        div_layout.addLayout(freq_layout)

        # Choix de la classe
        class_layout = QHBoxLayout()
        self.class_group = QButtonGroup(self)

        class1_radio = QRadioButton("Classe 1")
        class1_radio.setChecked(True)
        self.class_group.addButton(class1_radio)
        class_layout.addWidget(class1_radio)

        class2_radio = QRadioButton("Classe 2")
        self.class_group.addButton(class2_radio)
        class_layout.addWidget(class2_radio)

        div_layout.addLayout(class_layout)

        # Bouton de validation
        validate_button = QPushButton("Valider")
        validate_button.clicked.connect(self.show_selection_and_run)
        main_layout.addWidget(validate_button)

    def show_selection_and_run(self):
        poly = None
        for button in self.poly_group.buttons():
            if button.isChecked():
                poly = button.text()
                break

        try:
            freq = int(self.freq_input.text())
        except ValueError:
            print("Erreur: Fréquence doit être un entier positif.")
            return

        classe = None
        for button in self.class_group.buttons():
            if button.isChecked():
                classe = button.text()
                break

        if classe == "Classe 2" and freq % 2 != 0:
            print("Erreur: Classe 2 requiert une fréquence paire.")
            return

        # Appel de la fonction avec l'argument apex_type fixé à "sommet"
        verts = generate_vertices(poly, apex_type="sommet")
        pts = np.array(verts, dtype=float)
        hull = ConvexHull(pts)
        faces = hull.simplices.tolist()

        print(f"Polyèdre: {poly}, Fréquence: {freq}, Classe: {classe}")
        for i, (x,y,z) in enumerate(verts, 1):
            phi, theta, r = cartesian_to_spherical(x, y, z)
            print(f"  Sommet {i:2d}: Φ={phi:.8f}, θ={theta:.8f}, r={r:.1f}")

        plot_with_division(verts, faces, freq, classe, title=f"{poly} subdivisé, classe {classe}, freq {freq}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PolyhedronConfigWindow()
    window.show()
    sys.exit(app.exec_())
