# utils/math_utils.py

import numpy as np
from numba import njit
from config import K

@njit
def distance_3d_numba(p1, p2):
    """Distancia euclidiana entre dos puntos 3D (versión Numba)"""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

@njit
def electric_field_point_charge(q, r_source, r_field):
    """Campo eléctrico de una carga puntual usando Numba"""
    dx = r_field[0] - r_source[0]
    dy = r_field[1] - r_source[1]
    dz = r_field[2] - r_source[2]
    r_squared = dx**2 + dy**2 + dz**2
    r = np.sqrt(r_squared)
    if r == 0:
        return np.array([0.0, 0.0, 0.0])
    factor = K * q / r**3
    return np.array([factor * dx, factor * dy, factor * dz])

def create_grid(x_range, y_range, z_range, step):
    """Genera una malla 3D para evaluación de campo/potencial"""
    x = np.arange(*x_range, step)
    y = np.arange(*y_range, step)
    z = np.arange(*z_range, step)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    return X, Y, Z

def flatten_grid(X, Y, Z):
    """Convierte mallas 3D en listas planas de coordenadas"""
    return np.vstack((X.flatten(), Y.flatten(), Z.flatten())).T
