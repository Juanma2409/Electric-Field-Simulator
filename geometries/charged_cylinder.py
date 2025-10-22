# geometries/charged_cylinder.py

import numpy as np
import plotly.graph_objects as go
from config import EPSILON_0
from utils.math_utils import create_grid, flatten_grid
from numba import njit


@njit
def compute_field_cylinder(center, radius, height, sigma, obs_points,
                           N_theta=40, N_z=40, epsilon_0=EPSILON_0):
    E = np.zeros_like(obs_points)
    dtheta = 2 * np.pi / N_theta
    dz = height / N_z
    dA = radius * dtheta * dz
    dq = sigma * dA

    for i in range(N_theta):
        theta = i * dtheta
        x = center[0] + radius * np.cos(theta)
        y = center[1] + radius * np.sin(theta)

        for j in range(N_z):
            z = center[2] - height / 2 + j * dz
            r_source = np.array([x, y, z])

            for k in range(obs_points.shape[0]):
                r_vec = obs_points[k] - r_source
                r_mag = np.sqrt(np.sum(r_vec**2))
                if r_mag > 1e-6:
                    E[k] += dq * r_vec / (4 * np.pi * epsilon_0 * r_mag**3)
    return E


@njit
def compute_potential_cylinder(center, radius, height, sigma, obs_points,
                               N_theta=40, N_z=40, epsilon_0=EPSILON_0):
    V = np.zeros(obs_points.shape[0])
    dtheta = 2 * np.pi / N_theta
    dz = height / N_z
    dA = radius * dtheta * dz
    dq = sigma * dA

    for i in range(N_theta):
        theta = i * dtheta
        x = center[0] + radius * np.cos(theta)
        y = center[1] + radius * np.sin(theta)

        for j in range(N_z):
            z = center[2] - height / 2 + j * dz
            r_source = np.array([x, y, z])

            for k in range(obs_points.shape[0]):
                r_vec = obs_points[k] - r_source
                r_mag = np.sqrt(np.sum(r_vec**2))
                if r_mag > 1e-6:
                    V[k] += dq / (4 * np.pi * epsilon_0 * r_mag)
    return V


def simulate(sigma=1e-6,
             radius=1.0,
             height=2.0,
             show_equipotentials=True,
             N=20,
             epsilon_0=EPSILON_0,
             camera_eye=None,
             **kwargs):
    
    center = np.array([0.0, 0.0, 0.0])
    extent = 3.5

    # grid_step adaptativo según N 
    grid_step = max(0.8 * 20 / N, 0.2)

    X, Y, Z = create_grid((-extent, extent), (-extent, extent), (-extent, extent), grid_step)
    points = flatten_grid(X, Y, Z)

    N_theta = max(20, int(40 + N))
    N_z = max(20, int(40 + N))

    # Campo eléctrico
    E = compute_field_cylinder(center, radius, height, sigma, points,
                               N_theta=N_theta, N_z=N_z, epsilon_0=epsilon_0)
    Ex, Ey, Ez = E[:, 0], E[:, 1], E[:, 2]

    # Escalado visual 
    scale = 6e5
    Ex_vis, Ey_vis, Ez_vis = Ex / scale, Ey / scale, Ez / scale

    fig = go.Figure()

    # Vectores de campo 
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

    # Superficie del cilindro
    theta = np.linspace(0, 2 * np.pi, 64)
    z_c = np.linspace(-height / 2, height / 2, 40)
    Theta, Zmesh = np.meshgrid(theta, z_c)
    Xc = radius * np.cos(Theta)
    Yc = radius * np.sin(Theta)
    Zc = Zmesh

    fig.add_trace(go.Surface(
        x=Xc, y=Yc, z=Zc,
        colorscale='solar',
        opacity=0.55,
        showscale=False,
        name="Cilindro"
    ))

    # Equipotenciales 
    if show_equipotentials:
        xv = np.linspace(-extent, extent, min(40, max(10, N)))
        yv = np.linspace(-extent, extent, min(40, max(10, N)))
        zv = np.linspace(-extent, extent, min(40, max(10, N)))
        Xv, Yv, Zv = np.meshgrid(xv, yv, zv, indexing='ij')
        all_points = flatten_grid(Xv, Yv, Zv)

        V = compute_potential_cylinder(center, radius, height, sigma, all_points,
                                       N_theta=N_theta, N_z=N_z, epsilon_0=epsilon_0)
        V = V.reshape(Xv.shape)

        fig.add_trace(go.Isosurface(
            x=Xv.flatten(),
            y=Yv.flatten(),
            z=Zv.flatten(),
            value=V.flatten(),
            isomin=np.min(V),
            isomax=np.max(V),
            surface_count=6,
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

    # Cámara y estética
    cam_eye = camera_eye if camera_eye else dict(x=1.8, y=1.6, z=1.4)

    fig.update_layout(
        title=dict(
            text="<b>Cilindro cargado</b>",
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
        uirevision='charged_cylinder',
        dragmode="orbit",
        scene_dragmode="orbit"
    )

    return fig


def E_point(r_point, sigma=1e-6, radius=1.0, height=2.0,
            N=20, epsilon_0=EPSILON_0, **kwargs):
    obs = np.array([r_point], dtype=np.float64)
    center = np.array([0.0, 0.0, 0.0])
    N_theta = max(20, int(40 + N))
    N_z = max(20, int(40 + N))
    E = compute_field_cylinder(center, radius, height, sigma, obs,
                               N_theta=N_theta, N_z=N_z, epsilon_0=epsilon_0)
    return E[0]
