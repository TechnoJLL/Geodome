import math
import numpy as np

def cartesian_to_spherical(x, y, z):
    # Limiter z à la plage [-1, 1] pour éviter l'erreur math domain error
    z = max(-1.0, min(1.0, z))
    
    theta = math.acos(z)
    phi = math.atan2(y, x)
    if phi < 0:
        phi += 2 * math.pi
    return phi, theta, 1.0

def rotation_matrix(axis, angle):
    """Retourne une matrice de rotation autour de l'axe donné par 'axis' avec l'angle 'angle'."""
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    axis = np.array(axis) / np.linalg.norm(axis)  # Normalisation de l'axe
    ux, uy, uz = axis

    return np.array([
        [cos_angle + ux**2 * (1 - cos_angle), ux * uy * (1 - cos_angle) - uz * sin_angle, ux * uz * (1 - cos_angle) + uy * sin_angle],
        [uy * ux * (1 - cos_angle) + uz * sin_angle, cos_angle + uy**2 * (1 - cos_angle), uy * uz * (1 - cos_angle) - ux * sin_angle],
        [uz * ux * (1 - cos_angle) - uy * sin_angle, uz * uy * (1 - cos_angle) + ux * sin_angle, cos_angle + uz**2 * (1 - cos_angle)]
    ])

def generate_vertices(poly, apex_type="sommet"):
    """Génère les sommets d'un polyèdre régulier, en tenant compte de l'orientation de l'apex."""
    
    if poly == "Tétraèdre":
        verts = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    elif poly == "Octaèdre":
        verts = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    elif poly == "Icosaèdre":
        phi = (1 + math.sqrt(5)) / 2
        verts = [
            (0, 1, phi), (0, -1, phi), (0, 1, -phi), (0, -1, -phi),
            (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
            (phi, 0, 1), (-phi, 0, 1), (phi, 0, -1), (-phi, 0, -1)
        ]
    else:
        raise ValueError("Polyèdre invalide")
    
    # Normaliser les points pour les amener sur la sphère unité
    normed = [(x / math.sqrt(x**2 + y**2 + z**2), y / math.sqrt(x**2 + y**2 + z**2), z / math.sqrt(x**2 + y**2 + z**2)) for x, y, z in verts]
    
    if apex_type == "sommet":
        # Orientation 1: Le premier sommet doit être placé à l'apex (coordonnées (0, 0, 1))
        # Rotation nécessaire pour que le premier vertex (index 0) soit sur l'apex
        first_vertex = np.array(normed[0])
        z_axis = np.array([0, 0, 1])  # L'axe Z est l'apex de la sphère

        # Calcul de la rotation nécessaire pour aligner le premier vertex avec l'axe Z
        axis_of_rotation = np.cross(first_vertex, z_axis)
        axis_of_rotation = axis_of_rotation / np.linalg.norm(axis_of_rotation)  # Normalisation de l'axe
        angle = math.acos(np.dot(first_vertex, z_axis))  # Calcul de l'angle entre les deux vecteurs

        # Appliquer la rotation à tous les points
        rotation_mat = rotation_matrix(axis_of_rotation, angle)
        normed = np.dot(normed, rotation_mat.T)

    return normed
