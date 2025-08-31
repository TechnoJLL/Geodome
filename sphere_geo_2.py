import math
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from gen_poly_pts import generate_vertices

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

def show_selection_and_run():
    poly = poly_var.get()
    try:
        freq = int(freq_var.get())
    except ValueError:
        messagebox.showerror("Erreur", "Fréquence doit être un entier positif.")
        return

    classe = classe_var.get()
    if classe == "Classe 2" and freq % 2 != 0:
        messagebox.showerror("Erreur", "Classe 2 requiert une fréquence paire.")
        return

    root.destroy()

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

# --- GUI ---
root = tk.Tk()
root.title("Configuration du Polyèdre / Division")

# Choix du polyèdre
ttk.Label(root, text="Choix du polyèdre:").pack(anchor="w", padx=10, pady=2)
poly_var = tk.StringVar(value="Tétraèdre")
for p in ("Tétraèdre", "Octaèdre", "Icosaèdre"):
    ttk.Radiobutton(root, text=p, variable=poly_var, value=p).pack(anchor="w", padx=20)

# Paramètre de division
div_frame = ttk.LabelFrame(root, text="Division")
div_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(div_frame, text="Fréquence:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
freq_var = tk.StringVar(value="1")
ttk.Entry(div_frame, textvariable=freq_var, width=5).grid(row=0, column=1, padx=5, pady=5)

# Choix de la classe
classe_var = tk.StringVar(value="Classe 1")
ttk.Radiobutton(div_frame, text="Classe 1", variable=classe_var, value="Classe 1").grid(row=1, column=0, padx=5, pady=2)
ttk.Radiobutton(div_frame, text="Classe 2", variable=classe_var, value="Classe 2").grid(row=1, column=1, padx=5, pady=2)

# Bouton de validation
ttk.Button(root, text="Valider", command=show_selection_and_run).pack(pady=10)

root.mainloop()
