# geometries/parallel_plates.py

import numpy as np
import plotly.graph_objects as go
from config import EPSILON_0
from utils.math_utils import create_grid, flatten_grid
from numba import njit


@njit
def compute_field_parallel_plates(pos1, pos2, q1, q2, area, obs_points, epsilon_0=EPSILON_0):
    E = np.zeros_like(obs_points)

    N = 20
    w, h = 2.0, 2.0
    dx = w / N
    dy = h / N
    dA = dx * dy

    for i in range(N):
        for j in range(N):
            x = -w / 2 + (i + 0.5) * dx
            y = -h / 2 + (j + 0.5) * dy

            # Placa 1
            r1 = np.array([x, y, pos1[2]])
            dq1 = q1 / area * dA
            for k in range(obs_points.shape[0]):
                r_vec1 = obs_points[k] - r1
                r_mag1 = np.sqrt(np.sum(r_vec1**2))
                if r_mag1 > 1e-6:
                    E[k] += dq1 * r_vec1 / (4 * np.pi * epsilon_0 * r_mag1**3)

            # Placa 2
            r2 = np.array([x, y, pos2[2]])
            dq2 = q2 / area * dA
            for k in range(obs_points.shape[0]):
                r_vec2 = obs_points[k] - r2
                r_mag2 = np.sqrt(np.sum(r_vec2**2))
                if r_mag2 > 1e-6:
                    E[k] += dq2 * r_vec2 / (4 * np.pi * epsilon_0 * r_mag2**3)

    return E


@njit
def compute_potential_parallel_plates(pos1, pos2, q1, q2, area, obs_points, epsilon_0=EPSILON_0):
    V = np.zeros(obs_points.shape[0])

    N = 20
    w, h = 2.0, 2.0
    dx = w / N
    dy = h / N
    dA = dx * dy

    for i in range(N):
        for j in range(N):
            x = -w / 2 + (i + 0.5) * dx
            y = -h / 2 + (j + 0.5) * dy

            r1 = np.array([x, y, pos1[2]])
            dq1 = q1 / area * dA

            r2 = np.array([x, y, pos2[2]])
            dq2 = q2 / area * dA

            for k in range(obs_points.shape[0]):
                r_vec1 = obs_points[k] - r1
                r_mag1 = np.sqrt(np.sum(r_vec1**2))
                if r_mag1 > 1e-6:
                    V[k] += dq1 / (4 * np.pi * epsilon_0 * r_mag1)

                r_vec2 = obs_points[k] - r2
                r_mag2 = np.sqrt(np.sum(r_vec2**2))
                if r_mag2 > 1e-6:
                    V[k] += dq2 / (4 * np.pi * epsilon_0 * r_mag2)

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

    width, height = 2.0, 2.0
    area = width * height
    extent = 3.0
    step = max(0.8 * 20 / N, 0.2)

    q = sigma * area
    q1 = q
    q2 = -q if invert_signo else q

    pos1 = np.array([0.0, 0.0, -distance / 2])
    pos2 = np.array([0.0, 0.0, +distance / 2])

    # Malla de puntos
    X, Y, Z = create_grid((-extent, extent), (-extent, extent), (-extent, extent), step)
    points = flatten_grid(X, Y, Z)

    # Campo
    E = compute_field_parallel_plates(pos1, pos2, q1, q2, area, points, epsilon_0=epsilon_0)
    Ex, Ey, Ez = E[:, 0], E[:, 1], E[:, 2]
    scale = 5e5
    Ex_vis, Ey_vis, Ez_vis = Ex / scale, Ey / scale, Ez / scale

    fig = go.Figure()

    # Vectores del campo
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

    # Dibujar las placas
    def draw_plate(z, color):
        x = np.array([-width / 2, width / 2])
        y = np.array([-height / 2, height / 2])
        Xp, Yp = np.meshgrid(x, y)
        Zp = np.full_like(Xp, z)
        return go.Surface(
            x=Xp, y=Yp, z=Zp,
            colorscale=[[0, color], [1, color]],
            showscale=False,
            opacity=0.5
        )

    fig.add_trace(draw_plate(pos1[2], 'red'))
    fig.add_trace(draw_plate(pos2[2], 'blue'))

    # Equipotenciales
    if show_equipotentials:
        x = np.linspace(-extent, extent, min(40, max(10, N)))
        y = np.linspace(-extent, extent, min(40, max(10, N)))
        z = np.linspace(-extent, extent, min(40, max(10, N)))
        Xv, Yv, Zv = np.meshgrid(x, y, z, indexing='ij')
        V = compute_potential_parallel_plates(pos1, pos2, q1, q2, area, flatten_grid(Xv, Yv, Zv), epsilon_0=epsilon_0).reshape(Xv.shape)

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

    # Cámara
    cam_eye = camera_eye if camera_eye else dict(x=1.4, y=1.2, z=0.8)

    # Estética general
    fig.update_layout(
        title=dict(
            text="<b>Placas paralelas</b>",
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
        uirevision='parallel_plates',
        dragmode="orbit",
        scene_dragmode="orbit"
    )

    return fig


def E_point(r_point, sigma=1e-6, distance=1.0, invert_signo=True,
            N=20, epsilon_0=EPSILON_0, **kwargs):
    width, height = 2.0, 2.0
    area = width * height
    q = sigma * area
    q1 = q
    q2 = -q if invert_signo else q
    pos1 = np.array([0.0, 0.0, -distance / 2])
    pos2 = np.array([0.0, 0.0, +distance / 2])
    obs = np.array([r_point], dtype=np.float64)
    E = compute_field_parallel_plates(pos1, pos2, q1, q2, area, obs, epsilon_0=epsilon_0)
    return E[0]
