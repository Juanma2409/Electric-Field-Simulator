# geometries/two_spheres.py

import numpy as np
import plotly.graph_objects as go
from config import EPSILON_0
from utils.math_utils import create_grid, flatten_grid
from numba import njit


@njit
def compute_field_two_spheres(r1, r2, q1, q2, radius, obs_points, epsilon_0=EPSILON_0):
    E = np.zeros_like(obs_points)
    for i in range(obs_points.shape[0]):
        r_vec1 = obs_points[i] - r1
        r_vec2 = obs_points[i] - r2
        d1 = np.sqrt(np.sum(r_vec1**2))
        d2 = np.sqrt(np.sum(r_vec2**2))

        if d1 > radius:
            E[i] += (q1 * r_vec1) / (4 * np.pi * epsilon_0 * d1**3)
        if d2 > radius:
            E[i] += (q2 * r_vec2) / (4 * np.pi * epsilon_0 * d2**3)
    return E


@njit
def compute_potential_two_spheres(r1, r2, q1, q2, radius, obs_points, epsilon_0=EPSILON_0):
    V = np.zeros(obs_points.shape[0])
    for i in range(obs_points.shape[0]):
        d1 = np.linalg.norm(obs_points[i] - r1)
        d2 = np.linalg.norm(obs_points[i] - r2)

        if d1 > radius:
            V[i] += q1 / (4 * np.pi * epsilon_0 * d1)
        else:
            V[i] += q1 / (4 * np.pi * epsilon_0 * radius)

        if d2 > radius:
            V[i] += q2 / (4 * np.pi * epsilon_0 * d2)
        else:
            V[i] += q2 / (4 * np.pi * epsilon_0 * radius)
    return V


def simulate(sigma=1e-6,
             distance=1.0,
             show_equipotentials=True,
             invert_signo=True,
             N=20,
             epsilon_0=EPSILON_0,
             camera_eye=None,
             **kwargs):
  
    try:
        distance = float(distance)
    except:
        distance = 1.0

    radius = 0.5
    extent = 3.0
    grid_step = max(0.8 * 20 / N, 0.25)

    q = 4 * np.pi * radius**2 * sigma
    q1 = q
    q2 = -q if invert_signo else q

    r1 = np.array([-distance / 2, 0.0, 0.0])
    r2 = np.array([+distance / 2, 0.0, 0.0])

    X, Y, Z = create_grid((-extent, extent), (-extent, extent), (-extent, extent), grid_step)
    points = flatten_grid(X, Y, Z)

    E = compute_field_two_spheres(r1, r2, q1, q2, radius, points, epsilon_0=epsilon_0)
    Ex, Ey, Ez = E[:, 0], E[:, 1], E[:, 2]
    scale = 5e5
    Ex_vis, Ey_vis, Ez_vis = Ex / scale, Ey / scale, Ez / scale

    fig = go.Figure()

    # === Vectores de campo ===
    for i in range(len(points)):
        x0, y0, z0 = points[i]
        fig.add_trace(go.Scatter3d(
            x=[x0, x0 + Ex_vis[i]],
            y=[y0, y0 + Ey_vis[i]],
            z=[z0, z0 + Ez_vis[i]],
            mode='lines',
            line=dict(color='blue', width=3),
            showlegend=False
        ))

    # === Esferas cargadas ===
    def esfera(center, color):
        phi, theta = np.mgrid[0:np.pi:20j, 0:2*np.pi:30j]
        xs = center[0] + radius * np.sin(phi) * np.cos(theta)
        ys = center[1] + radius * np.sin(phi) * np.sin(theta)
        zs = center[2] + radius * np.cos(phi)
        return go.Surface(
            x=xs, y=ys, z=zs,
            colorscale=[[0, color], [1, color]],
            showscale=False,
            opacity=0.6
        )

    fig.add_trace(esfera(r1, 'red'))
    fig.add_trace(esfera(r2, 'blue'))

    # === Equipotenciales ===
    if show_equipotentials:
        x = np.linspace(-extent, extent, min(40, max(10, N)))
        y = np.linspace(-extent, extent, min(40, max(10, N)))
        z = np.linspace(-extent, extent, min(40, max(10, N)))
        Xv, Yv, Zv = np.meshgrid(x, y, z, indexing='ij')

        V = compute_potential_two_spheres(r1, r2, q1, q2, radius,
                                          flatten_grid(Xv, Yv, Zv),
                                          epsilon_0=epsilon_0).reshape(Xv.shape)

        fig.add_trace(go.Isosurface(
            x=Xv.flatten(),
            y=Yv.flatten(),
            z=Zv.flatten(),
            value=V.flatten(),
            isomin=np.min(V),
            isomax=np.max(V),
            surface_count=5,
            opacity=0.3,
            colorscale='RdBu',
            showscale=True,
            caps=dict(x_show=False, y_show=False, z_show=False),
            colorbar=dict(
                title=dict(text="V (voltios)", font=dict(size=13, family="Arial, sans-serif")),
                tickfont=dict(size=11)
            ),
            name="Equipotenciales"
        ))

    # === Estética general ===
    cam_eye = camera_eye if camera_eye else dict(x=1.8, y=1.6, z=1.3)

    fig.update_layout(
        title=dict(
            text="<b>Dos esferas cargadas</b>",
            font=dict(size=22, family="Arial, sans-serif", color="#1B2631"),
            x=0.5, xanchor="center"
        ),
        scene=dict(
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            zaxis_title="z (m)",
            aspectmode="data",
            xaxis=dict(showbackground=True, backgroundcolor="rgba(240,240,240,0.7)"),
            yaxis=dict(showbackground=True, backgroundcolor="rgba(240,240,240,0.7)"),
            zaxis=dict(showbackground=True, backgroundcolor="rgba(240,240,240,0.7)")
        ),
        scene_camera=dict(eye=cam_eye),
        margin=dict(l=0, r=0, b=0, t=40),
        paper_bgcolor="white",
        uirevision='two_spheres',
        dragmode="orbit",
        scene_dragmode="orbit"
    )

    return fig


def E_point(r_point, sigma=1e-6, distance=1.0, invert_signo=True,
            N=20, epsilon_0=EPSILON_0, **kwargs):
    radius = 0.5
    q = 4 * np.pi * radius**2 * sigma
    q1 = q
    q2 = -q if invert_signo else q
    r1 = np.array([-distance / 2, 0.0, 0.0])
    r2 = np.array([+distance / 2, 0.0, 0.0])
    obs = np.array([r_point], dtype=np.float64)
    E = compute_field_two_spheres(r1, r2, q1, q2, radius, obs, epsilon_0=epsilon_0)
    return E[0]
