# callbacks/particle_simulation.py
from dash import callback, Input, Output, State, ctx, dcc
import dash
import numpy as np
import time
from importlib import import_module
import inspect
import plotly.graph_objects as go
from main import generar_figura

# === FUNCIÓN GENERAL DE COLISIÓN CORREGIDA Y ROBUSTA ===
def check_collision(pos, geometry, params):
    x, y, z = pos

    try:
        r = float(params.get("radius") or 1.0)
    except (ValueError, TypeError):
        r = 1.0
    try:
        d = float(params.get("distance") or 1.0)
    except (ValueError, TypeError):
        d = 1.0

    pos = np.array([x, y, z])

    if geometry == "charged_sphere":
        return np.linalg.norm(pos) <= r

    elif geometry == "charged_ring":
        return abs(z) < 0.05 and abs(np.sqrt(x**2 + y**2) - r) < 0.05

    elif geometry == "charged_cylinder":
        height = 2.0
        return np.sqrt(x**2 + y**2) <= r and abs(z) <= height / 2

    elif geometry == "charged_plate":
        return abs(z) < 0.05 and abs(x) <= 0.5 and abs(y) <= 0.5

    elif geometry == "parallel_plates":
        lower = -d / 2
        upper = d / 2
        return abs(x) <= 1 and abs(y) <= 1 and (z <= lower or z >= upper)

    elif geometry == "two_spheres":
        center1 = np.array([+d / 2, 0, 0])
        center2 = np.array([-d / 2, 0, 0])
        return (np.linalg.norm(pos - center1) <= r) or (np.linalg.norm(pos - center2) <= r)

    return False


# === CALLBACK 1: ACTUALIZAR ESTADO DE LA PARTÍCULA ===
@callback(
    Output("particle-state", "data"),
    Output("animation-interval", "disabled"),
    Output("graph-container", "children", allow_duplicate=True),
    Input("start-button", "n_clicks"),
    Input("stop-button", "n_clicks"),
    Input("animation-interval", "n_intervals"),
    State("input-mass",   "value"),
    State("input-charge", "value"),
    State("input-x0",     "value"),
    State("input-y0",     "value"),
    State("input-z0",     "value"),
    State("input-vx0",    "value"),
    State("input-vy0",    "value"),
    State("input-vz0",    "value"),
    State("particle-state", "data"),
    State("geometry-dropdown", "value"),
    State("input-sigma",    "value"),
    State("input-radius",   "value"),
    State("input-distance", "value"),
    State("input-invert",   "value"),
    State("input-equipotentials", "value"),
    prevent_initial_call=True
)
def manejar_particula(n_start, n_stop, n_interval,
                      m, q, x0, y0, z0, vx0, vy0, vz0,
                      estado, geometry_key,
                      sigma, radius, distance, invert, equipotentials):

    triggered = ctx.triggered_id
    if triggered == "stop-button":
        nuevo_estado = dict(estado) if estado else {}
        nuevo_estado["activo"] = False
        return nuevo_estado, True, dash.no_update

    if triggered == "start-button":
        if not estado or not estado.get("simulated"):
            print(">> Ignorado: primero simular campo.")
            return dash.no_update, dash.no_update, dash.no_update

        # Iniciar la animación con el estado actual de inputs
        return {
            "simulated": True,
            "activo": True,
            "pos": [x0, y0, z0],
            "vel": [vx0, vy0, vz0],
            "m": m,
            "q": q,
            "geometry": geometry_key,
            "sigma": sigma,
            "radius": radius,
            "distance": distance,
            "invert": invert
        }, False, dash.no_update

    if triggered == "animation-interval":
        if not estado or not estado.get("activo") or not estado.get("pos"):
            return dash.no_update, True, dash.no_update

        estado = estado.copy()
        pos = np.array(estado["pos"], dtype=float)
        vel = np.array(estado["vel"], dtype=float)
        m, q = estado["m"], estado["q"]
        dt = 0.05

        try:
            geometry_module = import_module(f"geometries.{estado['geometry']}")
            E_func = geometry_module.E_point
            sig = inspect.signature(E_func)
            kwargs = {}
            if "sigma" in sig.parameters:
                kwargs["sigma"] = estado.get("sigma")
            if "radius" in sig.parameters:
                kwargs["radius"] = estado.get("radius")
            if "distance" in sig.parameters:
                kwargs["distance"] = estado.get("distance")
            if "invert_signo" in sig.parameters:
                kwargs["invert_signo"] = "invert" in estado.get("invert", [])

            E = E_func(pos, **kwargs)
            acc = (q / m) * E
            vel += acc * dt
            pos += vel * dt

            colision = check_collision(pos, estado["geometry"], estado)
            if colision:
                print(f">> Colisión detectada con {estado['geometry']}. Partícula detenida.")
                estado["activo"] = False

            estado["pos"] = pos.tolist()
            estado["vel"] = vel.tolist()

            return estado, dash.no_update, dash.no_update

        except Exception as e:
            print(f"Error en actualización de partícula: {e}")
            return dash.no_update, dash.no_update, dash.no_update

    return dash.no_update, dash.no_update, dash.no_update


# === CALLBACK 2: REDIBUJAR FIGURA CON PARTÍCULA ===
@callback(
    Output("graph-container", "children", allow_duplicate=True),
    Input("particle-state", "data"),
    State("input-equipotentials", "value"),
    State("input-N", "value"),
    State("input-epsilon0", "value"),
    State("input-camx", "value"),
    State("input-camy", "value"),
    State("input-camz", "value"),
    prevent_initial_call=True
)
def actualizar_grafico_particula(estado, equipotentials,
                                 N, epsilon0, camx, camy, camz):
    """
    Redibuja la figura (usando main.generar_figura) añadiendo la partícula.
    Ahora pasar N, epsilon_0 y camera eye desde los inputs del menú.
    """
    if not estado or not estado.get("simulated") or "geometry" not in estado:
        return dash.no_update

    try:
        N_val = int(N) if N is not None else 20
    except (ValueError, TypeError):
        N_val = 20

    try:
        eps_val = float(epsilon0) if epsilon0 is not None else 8.854e-12
    except (ValueError, TypeError):
        eps_val = 8.854e-12

    def _safe_float(v, default):
        try:
            return float(v) if v is not None else default
        except (ValueError, TypeError):
            return default

    camx_val = _safe_float(camx, 1.8)
    camy_val = _safe_float(camy, 1.6)
    camz_val = _safe_float(camz, 1.3)

    # generar_figura(geometry, sigma, distance, radius, equipotentials, invert_signo, N, epsilon_0, cam_x, cam_y, cam_z)
    try:
        fig = generar_figura(
            estado["geometry"],
            estado.get("sigma"),
            estado.get("distance"),
            estado.get("radius"),
            equipotentials,
            estado.get("invert"),
            N_val,
            eps_val,
            camx_val,
            camy_val,
            camz_val
        )
    except Exception as e:
        print(f"Error al generar figura en actualizar_grafico_particula: {e}")
        return dash.no_update

    if estado.get("pos") is not None:
        try:
            fig.add_trace(go.Scatter3d(
                x=[estado["pos"][0]],
                y=[estado["pos"][1]],
                z=[estado["pos"][2]],
                mode="markers",
                marker=dict(color="red", size=6),
                name="Partícula"
            ))
        except Exception as e:
            print(f"Error al añadir traza de partícula: {e}")

    graph = dcc.Graph(
        figure=fig,
        style={"height": "100vh", "width": "100%"},
        config={"scrollZoom": True, "doubleClick": "reset", "displayModeBar": True},
        className="simulacion-grafico"
    )

    return [graph]
