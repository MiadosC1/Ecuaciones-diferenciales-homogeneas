import importlib
import math

import pandas as pd
import streamlit as st

try:
    go = importlib.import_module("plotly.graph_objects")
except Exception:
    go = None


st.set_page_config(
    page_title="Ecuaciones Diferenciales",
    page_icon="📈",
    layout="wide",
)


def calcular_cola(a, t0, q0, tf, paso):
    tiempos = []
    valores = []
    t = t0

    while t <= tf:
        if t <= 0:
            t += paso
            continue

        c = (q0 / t0) - a * math.log(t0)
        valor = t * (a * math.log(t) + c)
        tiempos.append(round(t, 4))
        valores.append(round(valor, 4))
        t += paso

    return tiempos, valores


def calcular_constantes(alpha, omega, x0, dx0):
    if alpha >= omega:
        return None

    beta = math.sqrt(omega ** 2 - alpha ** 2)
    c1 = x0
    c2 = (dx0 + alpha * x0) / beta
    return c1, c2, beta


def generar_puntos(alpha, omega, x0, dx0, t_max, n_puntos=20):
    constantes = calcular_constantes(alpha, omega, x0, dx0)
    if constantes is None:
        return None

    c1, c2, beta = constantes
    tiempos = [i * t_max / (n_puntos - 1) for i in range(n_puntos)]
    valores = [math.exp(-alpha * t) * (c1 * math.cos(beta * t) + c2 * math.sin(beta * t)) for t in tiempos]
    return tiempos, valores, c1, c2, beta


def crear_figura_lineas(series, titulo, y_title):
    try:
        go_local = importlib.import_module("plotly.graph_objects")
    except Exception:
        return None

    figura = go_local.Figure()
    colores = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for indice, serie in enumerate(series):
        figura.add_trace(
            go.Scatter(
                x=serie["x"],
                y=serie["y"],
                mode="lines+markers",
                name=serie["name"],
                line=dict(color=colores[indice % len(colores)], width=3),
                marker=dict(size=6),
            )
        )

    figura.update_layout(
        title=titulo,
        xaxis_title="Tiempo (t)",
        yaxis_title=y_title,
        template="plotly_white",
        height=520,
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title="Series",
    )
    return figura


st.title("Simulador de Ecuaciones Diferenciales")
st.markdown("Elige entre la cola de solicitudes y la EDO de segundo orden para control de carga en servidor.")

with st.sidebar:
    st.header("Configuración")
    modo = st.selectbox(
        "Tipo de simulación",
        options=["Cola de solicitudes", "Control de carga con EDO de orden 2"],
    )

if modo == "Cola de solicitudes":
    st.subheader("Cola de Solicitudes")
    st.markdown("Modelo: $dq/dt = a + q/t$ y solución cerrada $q(t) = t(a\ln(t) + C)$.")

    with st.sidebar:
        a = st.slider("a", min_value=0.01, max_value=5.0, value=0.5, step=0.01)
        t0 = st.slider("t0", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
        q0 = st.slider("q0", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
        tf = st.slider("tf", min_value=0.2, max_value=20.0, value=10.0, step=0.1)
        paso = st.slider("paso", min_value=0.05, max_value=2.0, value=0.5, step=0.05)

    if t0 >= tf:
        st.warning("El tiempo inicial debe ser menor que el tiempo final.")
        st.stop()

    tiempos, valores = calcular_cola(a, t0, q0, tf, paso)
    if not tiempos:
        st.warning("No se pudieron generar puntos válidos para la cola de solicitudes.")
        st.stop()

    c = (q0 / t0) - a * math.log(t0)
    fig = crear_figura_lineas(
        [{"x": tiempos, "y": valores, "name": "Cola q(t)"}],
        "Cola de solicitudes q(t)",
        "Cola q(t)",
    )
    if fig is None:
        st.line_chart(pd.DataFrame({"t": tiempos, "q(t)": valores}).set_index("t"), use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)

    st.metric("Constante C", f"{c:.4f}")
    tabla = pd.DataFrame({"t": tiempos, "q(t)": valores})
    st.subheader("Tabla de puntos")
    st.dataframe(tabla, use_container_width=True, height=360)

else:
    st.subheader("Control de carga en servidor")
    st.markdown(
        "Modelo: $x''(t) + 2\alpha x'(t) + \omega^2 x(t) = 0$. Se valida el caso subamortiguado con $\alpha < \omega$."
    )

    defaults = [
        {"alpha": 0.5, "omega": 2.0, "x0": 1.0, "dx0": 0.0, "t_max": 10.0},
        {"alpha": 0.35, "omega": 2.4, "x0": 0.8, "dx0": 0.6, "t_max": 12.0},
        {"alpha": 0.7, "omega": 2.8, "x0": 1.2, "dx0": -0.2, "t_max": 9.0},
    ]

    escenarios = []

    with st.sidebar:
        cantidad_escenarios = st.slider("Escenarios a comparar", min_value=1, max_value=3, value=1)
        st.caption("Ajusta hasta 3 escenarios y compáralos en una sola gráfica.")

        for indice in range(cantidad_escenarios):
            configuracion = defaults[indice]
            with st.expander(f"Escenario {indice + 1}", expanded=indice == 0):
                alpha = st.slider(
                    "alpha",
                    min_value=0.0,
                    max_value=5.0,
                    value=float(configuracion["alpha"]),
                    step=0.05,
                    key=f"alpha_{indice}",
                )
                omega = st.slider(
                    "omega",
                    min_value=0.1,
                    max_value=6.0,
                    value=float(configuracion["omega"]),
                    step=0.05,
                    key=f"omega_{indice}",
                )
                x0 = st.slider(
                    "x0",
                    min_value=-50.0,
                    max_value=50.0,
                    value=float(configuracion["x0"]),
                    step=0.1,
                    key=f"x0_{indice}",
                )
                dx0 = st.slider(
                    "dx0",
                    min_value=-50.0,
                    max_value=50.0,
                    value=float(configuracion["dx0"]),
                    step=0.1,
                    key=f"dx0_{indice}",
                )
                t_max = st.slider(
                    "t_max",
                    min_value=1.0,
                    max_value=30.0,
                    value=float(configuracion["t_max"]),
                    step=0.5,
                    key=f"tmax_{indice}",
                )

            escenarios.append(
                {
                    "nombre": f"Escenario {indice + 1}",
                    "alpha": alpha,
                    "omega": omega,
                    "x0": x0,
                    "dx0": dx0,
                    "t_max": t_max,
                }
            )

    escenarios_validos = []
    for escenario in escenarios:
        resultado = generar_puntos(
            escenario["alpha"],
            escenario["omega"],
            escenario["x0"],
            escenario["dx0"],
            escenario["t_max"],
        )

        if resultado is None:
            st.warning(
                f"{escenario['nombre']}: alpha ({escenario['alpha']:.2f}) debe ser menor que omega ({escenario['omega']:.2f}) para mantener el régimen subamortiguado."
            )
            continue

        tiempos, valores, c1, c2, beta = resultado
        escenarios_validos.append(
            {
                **escenario,
                "tiempos": tiempos,
                "valores": valores,
                "c1": c1,
                "c2": c2,
                "beta": beta,
            }
        )

    if not escenarios_validos:
        st.stop()

    escenario_activo_nombre = st.selectbox(
        "Escenario para revisar la tabla y los parámetros",
        options=[escenario["nombre"] for escenario in escenarios_validos],
    )
    escenario_activo = next(
        escenario for escenario in escenarios_validos if escenario["nombre"] == escenario_activo_nombre
    )

    columna_1, columna_2, columna_3 = st.columns(3)
    with columna_1:
        st.metric("C1", f"{escenario_activo['c1']:.4f}")
    with columna_2:
        st.metric("C2", f"{escenario_activo['c2']:.4f}")
    with columna_3:
        st.metric("beta", f"{escenario_activo['beta']:.4f}")

    st.markdown(
        f"**Ecuación:** $x(t) = e^{{-\\alpha t}}\\left(C_1 \\cos(\\beta t) + C_2 \\sin(\\beta t)\\right)$\n\n"
        f"**Escenario activo:** $\\alpha = {escenario_activo['alpha']:.2f}$, $\\omega = {escenario_activo['omega']:.2f}$, "
        f"$x_0 = {escenario_activo['x0']:.2f}$, $\\dot x_0 = {escenario_activo['dx0']:.2f}$"
    )

    figura = crear_figura_lineas(
        [
            {"x": escenario["tiempos"], "y": escenario["valores"], "name": escenario["nombre"]}
            for escenario in escenarios_validos
        ],
        "Respuesta subamortiguada x(t)",
        "Desplazamiento x(t)",
    )
    if figura is None:
        grafica = pd.DataFrame({escenario["nombre"]: escenario["valores"] for escenario in escenarios_validos})
        grafica.insert(0, "t", escenarios_validos[0]["tiempos"])
        st.line_chart(grafica.set_index("t"), use_container_width=True)
    else:
        st.plotly_chart(figura, use_container_width=True)

    st.subheader("Tabla de 20 puntos")
    tabla = pd.DataFrame(
        {
            "t": [round(valor, 4) for valor in escenario_activo["tiempos"]],
            "x(t)": [round(valor, 4) for valor in escenario_activo["valores"]],
        }
    )
    st.dataframe(tabla, use_container_width=True, height=360)

    st.caption(
        "Si comparas varios escenarios, la gráfica superpone sus respuestas y la tabla muestra el escenario seleccionado."
    )
