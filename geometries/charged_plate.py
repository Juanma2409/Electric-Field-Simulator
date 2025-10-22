import numpy as np
import plotly.graph_objects as go
from numba import njit
from utils.math_utils import create_grid, flatten_grid


# =====================================================
# Campo eléctrico y potencial de una placa cargada
# =====================================================

@njit
def compute_field_plate(center, width, height, sigma, obs_points, epsilon_0, N):
    E = np.zeros_like(obs_points)
    dx = width / N
    dy = height / N
    dA = dx * dy
    for i in range(N):
        for j in range(N):
            x = center[0] - width / 2 + (i + 0.5) * dx
            y = center[1] - height / 2 + (j + 0.5) * dy
            z = center[2]
            r_source = np.array([x, y, z])
            dq = sigma * dA
            for k in range(obs_points.shape[0]):
                r_vec = obs_points[k] - r_source
                r_mag = np.sqrt(np.sum(r_vec**2))
                if r_mag == 0:
                    continue
                E[k] += dq * r_vec / (4 * np.pi * epsilon_0 * r_mag**3)
    return E


@njit
def compute_potential_plate(center, width, height, sigma, obs_points, epsilon_0, N):
    V = np.zeros(obs_points.shape[0])
    dx = width / N
    dy = height / N
    dA = dx * dy
    for i in range(N):
        for j in range(N):
            x = center[0] - width / 2 + (i + 0.5) * dx
            y = center[1] - height / 2 + (j + 0.5) * dy
            z = center[2]
            r_source = np.array([x, y, z])
            dq = sigma * dA
            for k in range(obs_points.shape[0]):
                r_vec = obs_points[k] - r_source
                r_mag = np.sqrt(np.sum(r_vec**2))
                if r_mag == 0:
                    continue
                V[k] += dq / (4 * np.pi * epsilon_0 * r_mag)
    return V


# =====================================================
# Simulación principal
# =====================================================
def simulate(sigma=1e-6, distance=None, show_equipotentials=True,
             N=20, epsilon_0=8.854e-12, camera_eye=None, **kwargs):

    width = 1.0
    height = 1.0
    center = np.array([0.0, 0.0, 0.0])
    extent = 2.0
    grid_step = max(0.8 * 20 / N, 0.2)

    X, Y, Z = create_grid((-extent, extent), (-extent, extent), (-extent, extent), grid_step)
    points = flatten_grid(X, Y, Z)

    # === Campo eléctrico ===
    E = compute_field_plate(center, width, height, sigma, points, epsilon_0, N)
    Ex, Ey, Ez = E[:, 0], E[:, 1], E[:, 2]

    scale = 5e5
    Ex_vis, Ey_vis, Ez_vis = Ex / scale, Ey / scale, Ez / scale

    fig = go.Figure()

    # === Dibujar vectores de campo ===
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

    # === Dibujar la placa ===
    xp = np.array([-width / 2, width / 2])
    yp = np.array([-height / 2, height / 2])
    Xp, Yp = np.meshgrid(xp, yp)
    Zp = np.zeros_like(Xp)
    fig.add_trace(go.Surface(
        x=Xp, y=Yp, z=Zp,
        showscale=False,
        opacity=0.5,
        colorscale='solar',
        name='Placa cargada'
    ))

    # === Superficies equipotenciales ===
    if show_equipotentials:
        x = np.linspace(-extent, extent, 25)
        y = np.linspace(-extent, extent, 25)
        z = np.linspace(-extent, extent, 25)
        Xv, Yv, Zv = np.meshgrid(x, y, z, indexing='ij')
        all_points = flatten_grid(Xv, Yv, Zv)
        V = compute_potential_plate(center, width, height, sigma, all_points, epsilon_0, N)
        V = V.reshape(Xv.shape)

        fig.add_trace(go.Isosurface(
            x=Xv.flatten(),
            y=Yv.flatten(),
            z=Zv.flatten(),
            value=V.flatten(),
            isomin=np.min(V),
            isomax=np.max(V),
            surface_count=5,
            colorscale='RdBu',
            opacity=0.3,
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Voltios (V)",
                    font=dict(size=13, family="Arial, sans-serif")
                ),
                tickfont=dict(size=11)
            ),
            caps=dict(x_show=False, y_show=False, z_show=False),
            name="Equipotenciales"
        ))

    # === Cámara y estilo ===
    cam_eye = camera_eye if camera_eye else dict(x=1.4, y=1.4, z=1.2)
    fig.update_layout(
        title=dict(
            text="<b>Placa cargada</b>",
            font=dict(size=22, family="Arial, sans-serif", color="#1B2631"),
            x=0.5, xanchor="center"
        ),
        scene=dict(
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            zaxis_title="z (m)",
            aspectmode="data"
        ),
        scene_camera=dict(eye=cam_eye),
        uirevision="charged_plate",
        dragmode="orbit",
        scene_dragmode="orbit",
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig


# =====================================================
# Campo puntual (para animación de partícula)
# =====================================================
def E_point(r_point, sigma=1e-6, width=1.0, height=1.0,
            epsilon_0=8.854e-12, N=20, **kwargs):
    obs = np.array([r_point], dtype=np.float64)
    center = np.array([0.0, 0.0, 0.0])
    E = compute_field_plate(center, width, height, sigma, obs, epsilon_0, N)
    return E[0]
