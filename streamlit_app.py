import importlib
import math

import pandas as pd
import streamlit as st

try:
    import sympy as sp
    from sympy.parsing.sympy_parser import (
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )
except Exception:
    sp = None
    parse_expr = None
    standard_transformations = None
    implicit_multiplication_application = None

try:
    go = importlib.import_module("plotly.graph_objects")
except Exception:
    go = None


st.set_page_config(
    page_title="Ecuaciones Diferenciales",
    page_icon="📈",
    layout="wide",
)


TRANSFORMACIONES_LAPLACE = None
if parse_expr is not None:
    TRANSFORMACIONES_LAPLACE = standard_transformations + (implicit_multiplication_application,)


def calcular_api_rest(y0, tf, paso, tasa_llegada=12.0, capacidad=3.0):
    tiempos = []
    valores = []
    t = 0.0
    equilibrio = tasa_llegada / capacidad

    while t <= tf:
        valor = equilibrio + (y0 - equilibrio) * math.exp(-capacidad * t)
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


def _simbolos_laplace():
    if sp is None:
        return None

    t, s = sp.symbols("t s", positive=True, real=True)
    locales = {
        "t": t,
        "s": s,
        "e": sp.E,
        "E": sp.E,
        "pi": sp.pi,
        "oo": sp.oo,
        "Heaviside": sp.Heaviside,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "exp": sp.exp,
        "log": sp.log,
        "sqrt": sp.sqrt,
        "Abs": sp.Abs,
    }
    return t, s, locales


def resolver_laplace_directa(expresion_texto):
    simbolos = _simbolos_laplace()
    if simbolos is None:
        return None, None, "La dependencia sympy no está disponible en este entorno."

    t, s, locales = simbolos
    try:
        expresion = parse_expr(
            expresion_texto,
            local_dict=locales,
            transformations=TRANSFORMACIONES_LAPLACE,
            evaluate=True,
        )
    except Exception as error:
        return None, None, f"No se pudo interpretar f(t): {error}"

    try:
        transformada = sp.laplace_transform(expresion, t, s, noconds=True)
    except Exception as error:
        return expresion, None, f"No se pudo calcular la transformada: {error}"

    return expresion, transformada, None


def resolver_laplace_inversa(expresion_texto):
    simbolos = _simbolos_laplace()
    if simbolos is None:
        return None, None, "La dependencia sympy no está disponible en este entorno."

    t, s, locales = simbolos
    try:
        expresion = parse_expr(
            expresion_texto,
            local_dict=locales,
            transformations=TRANSFORMACIONES_LAPLACE,
            evaluate=True,
        )
    except Exception as error:
        return None, None, f"No se pudo interpretar F(s): {error}"

    try:
        inversa = sp.inverse_laplace_transform(expresion, s, t)
    except Exception as error:
        return expresion, None, f"No se pudo calcular la transformada inversa: {error}"

    return expresion, inversa, None


st.title("Simulador de Ecuaciones Diferenciales")
st.markdown("Elige entre el procesamiento de solicitudes en una API REST, la EDO de segundo orden y la transformada de Laplace.")

with st.sidebar:
    st.header("Configuración")
    modo = st.selectbox(
        "Tipo de simulación",
        options=["Procesamiento de solicitudes en una API REST", "Control de carga con EDO de orden 2", "Transformada de Laplace"],
    )

if modo == "Procesamiento de solicitudes en una API REST":
    st.subheader("Procesamiento de solicitudes en una API REST")
    st.markdown(
        """
        Una API REST expone endpoints HTTP para recibir, procesar y responder solicitudes.

        **Variables del sistema**
        - Variable dependiente: $y(t)$, número de solicitudes en cola en el instante $t$.
        - Variable independiente: $t$, tiempo transcurrido desde el inicio.
        - Parámetros: tasa de llegada $\lambda$, capacidad de procesamiento $\mu$ y condición inicial $y(0)$.

        **Modelo diferencial**
        - Se usa la ecuación $y'(t) + 3y(t) = 12$ para representar la dinámica de carga.
        - El término $3y(t)$ modela la capacidad de procesamiento proporcional al estado actual.
        - El término $12$ representa la llegada constante de solicitudes.
        - La solución estacionaria es $y^* = 4$.
        """
    )

    with st.sidebar:
        y0 = st.slider("y(0)", min_value=0.0, max_value=100.0, value=2.0, step=0.5)
        tf = st.slider("tf", min_value=0.5, max_value=20.0, value=10.0, step=0.5)
        paso = st.slider("paso", min_value=0.05, max_value=2.0, value=0.5, step=0.05)

    tiempos, valores = calcular_api_rest(y0, tf, paso)
    if not tiempos:
        st.warning("No se pudieron generar puntos válidos para el procesamiento de solicitudes.")
        st.stop()

    fig = crear_figura_lineas(
        [{"x": tiempos, "y": valores, "name": "Solicitudes en cola y(t)"}],
        "Procesamiento de solicitudes en una API REST",
        "Solicitudes en cola y(t)",
    )
    if fig is None:
        st.line_chart(pd.DataFrame({"t": tiempos, "y(t)": valores}).set_index("t"), use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)

    columna_1, columna_2, columna_3 = st.columns(3)
    with columna_1:
        st.metric("Tasa de llegada λ", "12.0")
    with columna_2:
        st.metric("Capacidad μ", "3.0")
    with columna_3:
        st.metric("Estado estacionario", "4.0")

    st.markdown(f"**Solución cerrada:** $y(t) = 4 + ({y0:.2f} - 4)e^{{-3t}}$")

    tabla = pd.DataFrame({"t": tiempos, "y(t)": valores})
    st.subheader("Tabla de puntos")
    st.dataframe(tabla, use_container_width=True, height=360)

elif modo == "Control de carga con EDO de orden 2":
    st.subheader("Control de carga en servidor")
    st.markdown(
        r"Modelo: $x''(t) + 2\alpha x'(t) + \omega^2 x(t) = 0$. Se valida el caso subamortiguado con $\alpha < \omega$."
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

else:
    st.subheader("Transformada de Laplace")
    st.markdown(
        r"Calcula la transformada directa $\mathcal{L}\{f(t)\}$ y la inversa $\mathcal{L}^{-1}\{F(s)\}$ para expresiones simbólicas."
    )

    if sp is None:
        st.warning("Para usar esta sección instala la dependencia `sympy`.")
        st.stop()

    ejemplos_directa = ["sin(t)", "t**2", "exp(-2*t)*sin(3*t)"]
    ejemplos_inversa = ["1/(s+1)", "s/(s**2 + 4)", "1/(s*(s+2))"]

    tab_directa, tab_inversa = st.tabs(["Transformada directa", "Transformada inversa"])

    with tab_directa:
        expresion_directa = st.text_input(
            "Ingresa f(t)",
            value=ejemplos_directa[0],
            help="Usa expresiones como sin(t), t**2 o exp(-2*t)*sin(3*t).",
            key="laplace_directa_entrada",
        )
        if st.button("Calcular transformada", key="laplace_directa_boton") or expresion_directa:
            expresion, resultado, error = resolver_laplace_directa(expresion_directa)
            if error is not None:
                st.error(error)
            else:
                st.latex(r"f(t) = " + sp.latex(expresion))
                st.latex(r"\mathcal{L}\{f(t)\} = " + sp.latex(resultado))
                st.caption("Ejemplos rápidos: " + ", ".join(ejemplos_directa))

    with tab_inversa:
        expresion_inversa = st.text_input(
            "Ingresa F(s)",
            value=ejemplos_inversa[0],
            help="Usa expresiones como 1/(s+1), s/(s**2 + 4) o 1/(s*(s+2)).",
            key="laplace_inversa_entrada",
        )
        if st.button("Calcular inversa", key="laplace_inversa_boton") or expresion_inversa:
            expresion, resultado, error = resolver_laplace_inversa(expresion_inversa)
            if error is not None:
                st.error(error)
            else:
                st.latex(r"F(s) = " + sp.latex(expresion))
                st.latex(r"\mathcal{L}^{-1}\{F(s)\} = " + sp.latex(resultado))
                st.caption("Ejemplos rápidos: " + ", ".join(ejemplos_inversa))
