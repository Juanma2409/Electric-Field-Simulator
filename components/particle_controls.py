from dash import html, dcc

def particle_controls():
    return html.Div([
        html.Div([
            html.Label("Masa (kg):"),
            dcc.Input(
                id="input-mass", type="number", value=1e-3,
                step=1e-5, debounce=True
            )
        ], style={"marginBottom": "10px"}),

        html.Div([
            html.Label("Carga (C):"),
            dcc.Input(
                id="input-charge", type="number", value=1e-9,
                step=1e-9, debounce=True
            )
        ], style={"marginBottom": "10px"}),

        html.Div([
            html.Label("Posición inicial (x, y, z) (m):"),
            dcc.Input(id="input-x0", type="number", value=0.0, step=0.1),
            dcc.Input(id="input-y0", type="number", value=0.0, step=0.1),
            dcc.Input(id="input-z0", type="number", value=0.0, step=0.1)
        ], style={"marginBottom": "10px"}),

        html.Div([
            html.Label("Velocidad inicial (vx, vy, vz) (m/s):"),
            dcc.Input(id="input-vx0", type="number", value=0.0, step=0.1),
            dcc.Input(id="input-vy0", type="number", value=0.0, step=0.1),
            dcc.Input(id="input-vz0", type="number", value=0.0, step=0.1)
        ], style={"marginBottom": "10px"}),

        html.Div([
            html.Button("Iniciar animación", id="start-button", n_clicks=0),
            html.Button("Detener", id="stop-button", n_clicks=0, style={"marginLeft": "10px"})
        ], style={"marginTop": "20px"})
    ])
