import math
import numpy as np
from collections.abc import ValuesView
from scipy.spatial import ConvexHull
from gen_poly_pts import generate_vertices

Nedres = {4: "Tétraèdre", 8: "Octaèdre", 20: "Icosaèdre"}

def cartesian_to_spherical(x, y, z) -> tuple[float, float, float]:
    # Limiter z à la plage [-1, 1] pour éviter l'erreur math domain error
    z = max(-1.0, min(1.0, z))
    
    theta = math.acos(z)
    phi = math.atan2(y, x)
    if phi < 0:
        phi += 2 * math.pi
    return phi, theta, 1.0

def subdivide_triangle(A, B, C, freq: int) -> ValuesView[np.ndarray]:
    pts = {}
    for i in range(freq+1):
        for j in range(freq+1-i):
            k = freq - i - j
            wA, wB, wC = i / freq if freq else 1, j / freq if freq else 0, k / freq if freq else 0
            P = (A[0]*wA + B[0]*wB + C[0]*wC,
                 A[1]*wA + B[1]*wB + C[1]*wC,
                 A[2]*wA + B[2]*wB + C[2]*wC)
            norm = math.sqrt(P[0]**2 + P[1]**2 + P[2]**2)
            pts[(i,j)] = [P[0]/norm, P[1]/norm, P[2]/norm]
    return pts.values()

def nuage_pts(poly: int, freq: int, classe: int) -> np.ndarray:
    verts = generate_vertices(poly)
    
    print(f"Polyèdre: {Nedres[poly]}, Fréquence: {freq}, Classe: {classe}")
    for i, (x,y,z) in enumerate(verts, 1):
        phi, theta, r = cartesian_to_spherical(x, y, z)
        print(f"  Sommet {i:2d}: Φ={phi:.8f}, θ={theta:.8f}, r={r:.1f}")

    hull = ConvexHull(verts)
    faces = hull.simplices.tolist()
    for tri in faces:
        A, B, C = [verts[i] for i in tri]
        for P in subdivide_triangle(A, B, C, freq):
            # Vérifier si P est déjà dans les points en tenant compte des tolérances de comparaison
            if not any(np.allclose(P, tuple(existing_point)) for existing_point in verts):
                verts = np.append(verts, [P], axis=0)

    return verts

def edges(nuage: np.ndarray) -> set[tuple[int, int]]:
    hull = ConvexHull(nuage)
    edges = set()
    for simplex in hull.simplices:
        i, j, k = simplex
        edges.update({tuple(sorted((i,j))), tuple(sorted((j,k))), tuple(sorted((k,i)))})
    return edges