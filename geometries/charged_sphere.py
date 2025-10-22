import numpy as np
import plotly.graph_objects as go
from numba import njit

# =====================================================
# Campo eléctrico y potencial de una esfera cargada
# =====================================================

@njit
def compute_field_sphere(center, radius, sigma, obs_points, epsilon_0):
    E = np.zeros_like(obs_points)
    q_total = 4 * np.pi * radius**2 * sigma

    for i in range(obs_points.shape[0]):
        r_vec = obs_points[i] - center
        r_mag = np.sqrt(np.sum(r_vec**2))
        if r_mag <= radius:
            E[i] = np.array([0.0, 0.0, 0.0])  # Campo dentro de la esfera
        else:
            E[i] = (q_total * r_vec) / (4 * np.pi * epsilon_0 * r_mag**3)
    return E


@njit
def compute_potential_sphere(center, radius, sigma, obs_points, epsilon_0):
    V = np.zeros(obs_points.shape[0])
    q_total = 4 * np.pi * radius**2 * sigma

    for i in range(obs_points.shape[0]):
        r_vec = obs_points[i] - center
        r_mag = np.sqrt(np.sum(r_vec**2))
        if r_mag <= radius:
            V[i] = q_total / (4 * np.pi * epsilon_0 * radius)
        else:
            V[i] = q_total / (4 * np.pi * epsilon_0 * r_mag)
    return V


# =====================================================
# Simulación principal
# =====================================================
def simulate(sigma=1e-6, radius=1.0, show_equipotentials=True,
             N=20, epsilon_0=8.854e-12, camera_eye=None, **kwargs):

    center = np.array([0.0, 0.0, 0.0])
    extent = 3.0

    # === Densidad de puntos controlada por N ===
    grid_step = max(0.8 * 20 / N, 0.2)
    x = np.arange(-extent, extent + grid_step, grid_step)
    y = np.arange(-extent, extent + grid_step, grid_step)
    z = np.arange(-extent, extent + grid_step, grid_step)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    points = np.column_stack((X.flatten(), Y.flatten(), Z.flatten()))

    # === Campo eléctrico ===
    E = compute_field_sphere(center, radius, sigma, points, epsilon_0)
    Ex, Ey, Ez = E[:, 0], E[:, 1], E[:, 2]

    # === Escalado visual de vectores ===
    scale = 5e5
    Ex_vis, Ey_vis, Ez_vis = Ex / scale, Ey / scale, Ez / scale

    fig = go.Figure()

    # === Dibujar líneas de campo ===
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

    # === Esfera ===
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x_s = radius * np.outer(np.cos(u), np.sin(v))
    y_s = radius * np.outer(np.sin(u), np.sin(v))
    z_s = radius * np.outer(np.ones(np.size(u)), np.cos(v))

    fig.add_trace(go.Surface(
        x=x_s, y=y_s, z=z_s,
        colorscale='solar',
        opacity=0.5,
        showscale=False,
        name="Esfera cargada"
    ))

    # === Equipotenciales ===
    if show_equipotentials:
        Xv, Yv, Zv = np.meshgrid(x, y, z, indexing='ij')
        grid = np.column_stack((Xv.flatten(), Yv.flatten(), Zv.flatten()))
        V = compute_potential_sphere(center, radius, sigma, grid, epsilon_0).reshape(Xv.shape)

        fig.add_trace(go.Isosurface(
            x=Xv.flatten(),
            y=Yv.flatten(),
            z=Zv.flatten(),
            value=V.flatten(),
            isomin=np.min(V),
            isomax=np.max(V),
            surface_count=5,
            colorscale='RdBu',
            colorbar=dict(
                title=dict(
                    text="Voltios (V)",
                    font=dict(size=13, family="Arial, sans-serif")
                ),
                tickfont=dict(size=11)
            ),
            opacity=0.3,
            showscale=True,
            caps=dict(x_show=False, y_show=False, z_show=False),
            name="Equipotenciales"
        ))

    # === Cámara y diseño ===
    cam_eye = camera_eye if camera_eye else dict(x=1.7, y=1.7, z=1.3)
    fig.update_layout(
        title=dict(
            text="<b>Esfera cargada</b>",
            font=dict(size=20, family="Arial, sans-serif", color="#1B2631"),
            x=0.5,
            xanchor="center"
        ),
        scene=dict(
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            zaxis_title="z (m)",
            aspectmode="data"
        ),
        scene_camera=dict(eye=cam_eye),
        dragmode="orbit",
        scene_dragmode="orbit",
        uirevision=True,
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig


# =====================================================
# Campo puntual para la partícula
# =====================================================
def E_point(r_point, sigma=1e-6, radius=1.0, epsilon_0=8.854e-12, **kwargs):
    obs = np.array([r_point], dtype=np.float64)
    center = np.array([0.0, 0.0, 0.0])
    E = compute_field_sphere(center, radius, sigma, obs, epsilon_0)
    return E[0]
