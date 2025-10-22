import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go

from geometries.charged_plate import simulate as simulate_charged_plate
from geometries.charged_sphere import simulate as simulate_charged_sphere
from geometries.charged_cylinder import simulate as simulate_charged_cylinder
from geometries.parallel_plates import simulate as simulate_parallel_plates
from geometries.two_spheres import simulate as simulate_two_spheres
from geometries.charged_ring import simulate as simulate_charged_ring

from components.particle_controls import particle_controls
from callbacks import particle_simulation

# === Mapeo de geometrías ===
geometry_map = {
    "charged_plate": simulate_charged_plate,
    "charged_sphere": simulate_charged_sphere,
    "charged_cylinder": simulate_charged_cylinder,
    "parallel_plates": simulate_parallel_plates,
    "two_spheres": simulate_two_spheres,
    "charged_ring": simulate_charged_ring
}

geometries = {
    "Placa cargada": "charged_plate",
    "Placas paralelas": "parallel_plates",
    "Esfera cargada": "charged_sphere",
    "Dos esferas cargadas": "two_spheres",
    "Anillo cargado": "charged_ring",
    "Cilindro cargado": "charged_cylinder"
}


# ===== GENERAR FIGURA =====
def generar_figura(geometry, sigma, distance, radius, equipotentials, invert_signo,
                   N, epsilon_0, cam_x, cam_y, cam_z):

    sigma_val = sigma if sigma is not None else 1e-6
    distance_val = distance if distance is not None else 1.0
    radius_val = radius if radius is not None else 1.0
    N_val = int(N) if N is not None else 20
    eps_val = epsilon_0 if epsilon_0 is not None else 8.854e-12
    show_equip = "equipotentials" in equipotentials if equipotentials else False
    invert = "invert" in invert_signo if invert_signo else False

    simulate_fn = geometry_map.get(geometry)
    simulate_args = simulate_fn.__code__.co_varnames
    kwargs = {
        "sigma": sigma_val,
        "show_equipotentials": show_equip,
        "N": N_val,
        "epsilon_0": eps_val,
        "camera_eye": dict(x=cam_x, y=cam_y, z=cam_z)
    }
    if "distance" in simulate_args:
        kwargs["distance"] = distance_val
    if "radius" in simulate_args and geometry != "charged_sphere":
        kwargs["radius"] = radius_val
    if "invert_signo" in simulate_args:
        kwargs["invert_signo"] = invert

    fig = simulate_fn(**kwargs)

    fig.update_layout(
        dragmode="orbit",
        scene_dragmode="orbit"
    )
    return fig


# ===== APP DASH =====
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Simulador de Campo Eléctrico"

# ===== ESTILOS =====
CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "padding": "20px",
    "borderRadius": "12px",
    "boxShadow": "0 4px 8px rgba(0,0,0,0.1)",
    "marginBottom": "20px"
}

BUTTON_STYLE = {
    "marginTop": "15px",
    "backgroundColor": "#2E86C1",
    "color": "white",
    "border": "none",
    "padding": "12px 22px",
    "borderRadius": "8px",
    "cursor": "pointer",
    "fontWeight": "bold",
    "fontSize": "15px"
}

TITLE_STYLE = {
    "textAlign": "center",
    "marginBottom": "30px",
    "fontFamily": "Arial, sans-serif",
    "color": "#1B2631"
}


# ===== LAYOUT =====
app.layout = html.Div([
    html.H1("Simulación de Campo Eléctrico", style=TITLE_STYLE),

    html.Div([

        # === CONTROLES ===
        html.Div([
            # ==== Selección de geometría ====
            html.Div([
                html.Label("Selecciona una configuración:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id='geometry-dropdown',
                    options=[{"label": k, "value": v} for k, v in geometries.items()],
                    value="charged_plate",
                    style={"marginBottom": "15px"}
                ),
                html.Div(id='geometry-controls', style={"marginTop": "10px"}),

                html.Button("Simular", id="simulate-btn", n_clicks=0, style=BUTTON_STYLE)
            ], style=CARD_STYLE),

            # ==== CONTROLES DE LA PARTÍCULA ====
            html.Div([
                html.H3("Controles de la partícula",
                        style={"textAlign": "center", "marginBottom": "15px"}),
                html.Div(particle_controls(),
                         style={"display": "flex", "justifyContent": "center",
                                "alignItems": "center", "flexDirection": "column"})
            ], style=CARD_STYLE),

            # ==== OPCIONES AVANZADAS ====
            html.Div([
                html.H3("Opciones avanzadas", style={"textAlign": "center", "marginBottom": "10px"}),

                html.Label("Resolución N (discretización):"),
                dcc.Input(id="input-N", type="number", min=5, step=1, value=30,
                          style={"width": "100%", "marginBottom": "10px"}),

                html.Label("Constante de permitividad ε₀ (F/m):"),
                dcc.Input(id="input-epsilon0", type="number", step=1e-13, value=8.8e-12,
                          style={"width": "100%", "marginBottom": "15px"}),

                html.Label("Ángulo inicial de la cámara:"),
                html.Div([
                    html.Div([
                        html.Label("x:"),
                        dcc.Input(id="input-camx", type="number", step=0.1, value=1.8,
                                  style={"width": "90%"})
                    ], style={"display": "inline-block", "width": "32%", "marginRight": "1%"}),
                    html.Div([
                        html.Label("y:"),
                        dcc.Input(id="input-camy", type="number", step=0.1, value=1.6,
                                  style={"width": "90%"})
                    ], style={"display": "inline-block", "width": "32%", "marginRight": "1%"}),
                    html.Div([
                        html.Label("z:"),
                        dcc.Input(id="input-camz", type="number", step=0.1, value=1.3,
                                  style={"width": "90%"})
                    ], style={"display": "inline-block", "width": "32%"})
                ])
            ], style=CARD_STYLE)
        ], style={"flex": "1", "marginRight": "20px"}),

        # === SIMULACIÓN ===
        html.Div([
            html.Div(id="graph-container", children=[],
                     style={"backgroundColor": "#fff",
                            "borderRadius": "12px",
                            "boxShadow": "0 4px 10px rgba(0,0,0,0.15)",
                            "padding": "10px"})
        ], style={"flex": "3"})

    ], style={"display": "flex", "flexDirection": "row", "width": "95%", "margin": "auto"}),

    dcc.Store(id="particle-state", data={"simulated": False, "activo": False}),
    dcc.Interval(id="animation-interval", interval=100, disabled=True)
])


# ===== CALLBACKS =====
@app.callback(
    Output("geometry-controls", "children"),
    Input("geometry-dropdown", "value")
)
def update_controls(geometry):
    controls = []

    show_sigma = geometry in ["charged_plate", "charged_sphere", "charged_cylinder",
                              "parallel_plates", "two_spheres", "charged_ring"]
    controls.append(html.Div([
        html.Label("Densidad de carga (C/m²):"),
        dcc.Input(id="input-sigma", type="number", step=1e-7, value=1e-6)
    ], style={} if show_sigma else {"display": "none"}))

    show_distance = geometry in ["parallel_plates", "two_spheres"]
    controls.append(html.Div([
        html.Label("Distancia entre superficies (m):"),
        dcc.Input(id="input-distance", type="number", step=0.1, value=1.0)
    ], style={} if show_distance else {"display": "none"}))

    show_radius = geometry in ["charged_ring", "charged_cylinder"]
    controls.append(html.Div([
        html.Label("Radio (m):"),
        dcc.Input(id="input-radius", type="number", step=0.1, value=1.0)
    ], style={} if show_radius else {"display": "none"}))

    controls.append(html.Div([
        dcc.Checklist(
            options=[{"label": "Mostrar superficies equipotenciales", "value": "equipotentials"}],
            value=["equipotentials"], id="input-equipotentials"
        ),    
    ], style={"marginTop": "10px"}))

    show_invert = geometry in ["two_spheres", "parallel_plates"]
    controls.append(html.Div([
        dcc.Checklist(
            options=[{"label": "Invertir signo de una superficie", "value": "invert"}],
            value=["invert"], id="input-invert"
        )
    ], style={} if show_invert else {"display": "none"}))

    return controls


@app.callback(
    Output("graph-container", "children"),
    Output("particle-state", "data", allow_duplicate=True),
    Input("simulate-btn", "n_clicks"),
    State("geometry-dropdown", "value"),
    State("input-sigma", "value"),
    State("input-distance", "value"),
    State("input-radius", "value"),
    State("input-equipotentials", "value"),
    State("input-invert", "value"),
    State("input-N", "value"),
    State("input-epsilon0", "value"),
    State("input-camx", "value"),
    State("input-camy", "value"),
    State("input-camz", "value"),
    prevent_initial_call=True
)
def actualizar_grafico(n_clicks_simulate, geometry, sigma, distance, radius,
                       equipotentials, invert_signo, N, epsilon_0, camx, camy, camz):

    fig = generar_figura(geometry, sigma, distance, radius, equipotentials,
                         invert_signo, N, epsilon_0, camx, camy, camz)

    return [
        dcc.Graph(
            figure=fig,
            style={"height": "100vh", "width": "100%"},
            config={"scrollZoom": True, "doubleClick": "reset", "displayModeBar": True},
            className="simulacion-grafico"
        )
    ], {"simulated": True, "activo": False}


if __name__ == '__main__':
    app.run(debug=True)
