# Simulador de Campo Eléctrico y superficies equipotenciales / Electric field and equipotential surface simulator

---

## 🇪🇸 Español

### Descripción
Este proyecto es un **simulador interactivo 3D de campos eléctricos** hecho con **Plotly Dash** en Python. Permite seleccionar distintas **configuraciones (geometrías)** cargadas — placa, esfera, cilindro, anillo, placas paralelas, dos esferas — visualizar vectores de campo, superficies equipotenciales y **simular la trayectoria de una partícula cargada** bajo la influencia del campo.

Enfoque educativo: explorar visualmente cómo cambia el campo al modificar parámetros (densidad de carga, distancia, radio, permitividad, discretización, cámara) y observar la dinámica de una partícula de prueba.

---

### Características principales
- Visualización 3D del campo (vectores) y superficies equipotenciales.  
- Animación de una partícula cargada con integración numérica simple (velocidad, aceleración por `E` en cada paso).  
- Controles en la UI para:
  - Selección de geometría.
  - Parámetros físicos: densidad `sigma`, radio, distancia, invertir signo, etc.
  - Controles de la partícula: posición/velocidad/masa/carga.
  - Opciones avanzadas: `N` (discretización), `ε₀` (permitividad), y cámara (eye x,y,z).
- Detección de colisiones (inelástica: la partícula se detiene al tocar una geometría).  
- `dcc.Store` para mantener el estado de la partícula; `dcc.Interval` controla los pasos de la animación.
- Estilo y cámara preservados entre redraws (uso de `uirevision`, `scene_camera`, `dragmode="orbit"`).

---

### Requisitos
(Usar un entorno virtual recomendado)

- Python 3.9+ (probado con 3.10/3.11/3.13)
- Paquetes:
  - dash
  - plotly
  - numpy
  - numba (opcional — acelera cálculos)
  - (otros utilitarios incluidos en el repo)

Instalación rápida:
```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate.bat     # Windows
pip install -r requirements.txt
```

---

### Estructura del proyecto
```
.
├── main.py
├── callbacks/
│   └── particle_simulation.py
├── components/
│   └── particle_controls.py
├── geometries/
│   ├── charged_plate.py
│   ├── charged_sphere.py
│   ├── charged_cylinder.py
│   ├── charged_ring.py
│   ├── parallel_plates.py
│   └── two_spheres.py
├── utils/
│   └── math_utils.py
├── config.py
├── requirements.txt
└── README.md
```

---

### Ejecución
```bash
python main.py
```
Abrir en navegador `http://127.0.0.1:8050/`.

---

### Controles de la interfaz
- **Dropdown**: elegir configuración.  
- **Inputs**: `sigma`, `radio`, `distancia`, `invert`.  
- **Equipotenciales**: activa/desactiva superficies equipotenciales.  
- **Partícula**: posición inicial, velocidad, masa, carga.  
- **Botones**:
  - **Simular**: dibuja figura.  
  - **Iniciar animación**: mueve la partícula.  
  - **Detener**: pausa la animación.  
- **Avanzado**:
  - `N`: discretización.  
  - `ε₀`: permitividad.  
  - `Cámara (x,y,z)`: posición inicial del ojo.

---

### Escalas de color
Consulta los colores disponibles en Plotly:  
https://plotly.com/python/builtin-colorscales/

---

### Notas técnicas
- Aumentar `N` aumenta la precisión y el costo computacional.  
- `numba` acelera el cálculo.  
- Usa `dcc.Interval` para controlar la frecuencia de actualización.  
- Las colisiones son inelásticas (la partícula se detiene).  

---

### Añadir una geometría
1. Crear `geometries/mi_geometria.py` con:
   - `simulate(..., N=20, epsilon_0=8.854e-12, camera_eye=None, **kwargs)`
   - `E_point(r_point, ..., epsilon_0=..., **kwargs)`
2. Registrar la geometría en `main.py`.
3. Añadir inputs en `update_controls`.
4. Definir colisión en `callbacks/particle_simulation.py::check_collision`.

---

### Nota para la comunidad

Este proyecto ha sido desarrollado con el propósito de apoyar la enseñanza y el aprendizaje de la física, brindando una herramienta interactiva para visualizar conceptos de electrostática de forma clara e intuitiva.

Invito a toda la comunidad académica y de desarrolladores a probarlo, compartirlo y contribuir con ideas o mejoras.
Estoy completamente abierto a recibir comentarios, sugerencias o retroalimentación, ya que esto ayudará a seguir perfeccionando el simulador y a hacerlo más útil para estudiantes y docentes.

Si deseas contactarme directamente, puedes escribirme a:
juanma240906@gmail.com

---

### Créditos y Licencia
Autor: Juan Manuel Cancino.
MIT License — uso libre y abierto.

---

## 🇬🇧 English

### Description
This project is a **3D interactive electric field simulator** built with **Plotly Dash** in Python. It supports various charged **configurations** — plate, sphere, cylinder, ring, parallel plates, and two spheres — and visualizes field vectors, equipotential surfaces, and particle motion under the electric field.

---

### Main Features
- 3D visualization (vectors + Isosurface).  
- Particle motion via numerical integration.  
- UI controls for geometry, parameters, particle, and camera.  
- Collision detection (inelastic).  
- Customizable resolution (`N`), permittivity (`ε₀`), and camera view.

---

### Requirements
- Python 3.9+
- Libraries:
  - dash, plotly, numpy, numba
```bash
pip install -r requirements.txt
```

---

### Run
```bash
python main.py
```

Visit `http://127.0.0.1:8050/` in your browser.

---

### Colorscales
List of available Plotly built-in color maps:  
https://plotly.com/python/builtin-colorscales/

---

### Community Note

This project was created to support physics education and learning, providing an interactive tool to help visualize electrostatic concepts in a clear and intuitive way.

I warmly invite the academic and developer community to try it, share it, and contribute with ideas or improvements.
I’m completely open to receiving feedback, comments, and suggestions to keep improving the simulator and make it even more useful for students and teachers.

If you wish to reach out, feel free to contact me at:
juanma240906@gmail.com

---

### Credits & License
Author: Juan Manuel Cancino.
MIT License — free and open use.


