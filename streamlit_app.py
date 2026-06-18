import streamlit as st
import math
import pandas as pd
from abc import ABC, abstractmethod

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

# Configuración de la página
st.set_page_config(
    page_title="Ecuaciones Diferenciales",
    page_icon="📊",
    layout="wide"
)

# ============================================
# SISTEMA MODULAR DE ECUACIONES DIFERENCIALES
# ============================================

class EcuacionDiferencial(ABC):
    """Clase base para ecuaciones diferenciales"""
    
    def __init__(self, nombre, ecuacion, parametros, eje_y="y(t)", color="blue"):
        self.nombre = nombre
        self.ecuacion = ecuacion
        self.parametros = parametros
        self.eje_y = eje_y
        self.color = color
    
    @abstractmethod
    def calcular_solucion(self, t, **params):
        pass

# ECUACIONES DISPONIBLES

class ColaDiferencial(EcuacionDiferencial):
    def __init__(self):
        super().__init__(
            nombre="Cola de Solicitudes",
            ecuacion="dq/dt = a + q/t",
            parametros=['a', 't0', 'q0', 'tf', 'paso'],
            eje_y="Cola q(t)",
            color="#1f77b4"
        )
    
    def calcular_solucion(self, t, a, t0, q0, **kwargs):
        C = (q0 / t0) - a * math.log(t0)
        return t * (a * math.log(t) + C)

class CrecimientoExponencial(EcuacionDiferencial):
    def __init__(self):
        super().__init__(
            nombre="Crecimiento Exponencial",
            ecuacion="dy/dt = ky",
            parametros=['k', 't0', 'y0', 'tf', 'paso'],
            eje_y="y(t)",
            color="#2ca02c"
        )
    
    def calcular_solucion(self, t, k, t0, y0, **kwargs):
        return y0 * math.exp(k * (t - t0))

class EnfriamientoNewton(EcuacionDiferencial):
    def __init__(self):
        super().__init__(
            nombre="Enfriamiento de Newton",
            ecuacion="dy/dt = -k(y - T)",
            parametros=['k', 'T', 't0', 'y0', 'tf', 'paso'],
            eje_y="Temperatura y(t)",
            color="#d62728"
        )
    
    def calcular_solucion(self, t, k, T, t0, y0, **kwargs):
        return T + (y0 - T) * math.exp(-k * (t - t0))

class EcuacionLogistica(EcuacionDiferencial):
    def __init__(self):
        super().__init__(
            nombre="Ecuación Logística",
            ecuacion="dy/dt = ry(1 - y/K)",
            parametros=['r', 'K', 't0', 'y0', 'tf', 'paso'],
            eje_y="Población y(t)",
            color="#9467bd"
        )
    
    def calcular_solucion(self, t, r, K, t0, y0, **kwargs):
        exp_term = math.exp(-r * (t - t0)) * (K - y0) / y0
        return K / (1 + exp_term)

class CircuitoRC(EcuacionDiferencial):
    def __init__(self):
        super().__init__(
            nombre="Circuito RC",
            ecuacion="dV/dt = -V/(RC)",
            parametros=['R', 'C', 't0', 'V0', 'tf', 'paso'],
            eje_y="Voltaje V(t)",
            color="#ff7f0e"
        )
    
    def calcular_solucion(self, t, R, C, t0, V0, **kwargs):
        tau = R * C
        return V0 * math.exp(-(t - t0) / tau)

# Registro de ecuaciones
ECUACIONES = {
    'cola': ColaDiferencial(),
    'exponencial': CrecimientoExponencial(),
    'newton': EnfriamientoNewton(),
    'logistica': EcuacionLogistica(),
    'rc': CircuitoRC()
}

def calcular(tipo_eq, **params):
    """Calcula la solución de una ecuación"""
    ecuacion = ECUACIONES[tipo_eq]
    t0 = params['t0']
    tf = params['tf']
    paso = params['paso']
    
    tiempos = []
    valores = []
    
    t = t0
    while t <= tf:
        try:
            valor = ecuacion.calcular_solucion(t, **params)
            tiempos.append(round(t, 4))
            valores.append(round(valor, 4))
        except:
            continue
        t += paso
    
    return tiempos, valores, ecuacion


def mostrar_grafica(tiempos, valores, eq):
    df_grafica = pd.DataFrame({
        'Tiempo (t)': tiempos,
        eq.eje_y: valores
    })

    if plt is not None:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(tiempos, valores, marker="o", linestyle="-",
                linewidth=2, color=eq.color, markersize=6, label=eq.eje_y)
        ax.set_xlabel("Tiempo (t)", fontsize=12)
        ax.set_ylabel(eq.eje_y, fontsize=12)
        ax.set_title(f"{eq.nombre}: {eq.ecuacion}", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.line_chart(df_grafica.set_index('Tiempo (t)'))

# INTERFAZ PRINCIPAL
st.title("📊 Simulador de Ecuaciones Diferenciales")
st.markdown("Visualiza y resuelve diferentes ecuaciones diferenciales de forma interactiva")

# Sidebar con selección
with st.sidebar:
    st.header("⚙️ Configuración")
    
    tipo_ecuacion = st.selectbox(
        "Selecciona una ecuación:",
        options=list(ECUACIONES.keys()),
        format_func=lambda x: ECUACIONES[x].nombre
    )
    
    ecuacion_actual = ECUACIONES[tipo_ecuacion]
    
    st.markdown(f"**Ecuación:** `{ecuacion_actual.ecuacion}`")
    st.markdown(f"**Eje Y:** {ecuacion_actual.eje_y}")
    st.divider()
    
    # Parámetros dinámicos
    params = {}
    labels = {
        'a': 'Factor de crecimiento (a)',
        'k': 'Constante de decaimiento (k)',
        'K': 'Capacidad máxima (K)',
        'r': 'Tasa de crecimiento (r)',
        'R': 'Resistencia (R) Ω',
        'C': 'Capacitancia (C) F',
        'T': 'Temperatura ambiente (T)',
        't0': 'Tiempo inicial (t₀)',
        'y0': 'Valor inicial (y₀)',
        'q0': 'Cola inicial (q₀)',
        'V0': 'Voltaje inicial (V₀)',
        'tf': 'Tiempo final (tₓ)',
        'paso': 'Paso de tiempo'
    }
    
    defaults = {
        'cola': {'a': 0.5, 't0': 1, 'q0': 5, 'tf': 10, 'paso': 0.5},
        'exponencial': {'k': 0.3, 't0': 0, 'y0': 1, 'tf': 10, 'paso': 0.5},
        'newton': {'k': 0.1, 'T': 20, 't0': 0, 'y0': 100, 'tf': 50, 'paso': 1},
        'logistica': {'r': 0.3, 'K': 1000, 't0': 0, 'y0': 10, 'tf': 30, 'paso': 0.5},
        'rc': {'R': 1000, 'C': 0.001, 't0': 0, 'V0': 10, 'tf': 5, 'paso': 0.1}
    }
    
    default_vals = defaults.get(tipo_ecuacion, {})
    
    for param in ecuacion_actual.parametros:
        # Streamlit requires all numeric args (value/step/min/max) to share type.
        if param in ['paso']:
            params[param] = st.number_input(
                labels[param],
                value=float(default_vals.get(param, 0.5)),
                step=0.01,
                min_value=0.01
            )
        elif param in ['t0', 'y0', 'q0', 'V0']:
            params[param] = st.number_input(
                labels[param],
                value=float(default_vals.get(param, 0.0)),
                step=0.1
            )
        else:
            params[param] = st.number_input(
                labels[param],
                value=float(default_vals.get(param, 1.0)),
                step=0.1
            )
    
    st.divider()
    calcular_btn = st.button("🚀 Calcular", width="stretch", type="primary")

# CÁLCULO Y VISUALIZACIÓN
if calcular_btn:
    try:
        # Validaciones
        if params['t0'] <= 0 or params['tf'] <= 0:
            st.error("❌ El tiempo inicial y final deben ser mayores que 0")
        elif params['t0'] > params['tf']:
            st.error("❌ El tiempo inicial debe ser menor que el final")
        elif params['paso'] <= 0:
            st.error("❌ El paso debe ser mayor que 0")
        else:
            # Calcular
            tiempos, valores, eq = calcular(tipo_ecuacion, **params)
            
            if valores:
                # Crear columnas
                col1, col2 = st.columns(2)
                
                # Gráfica
                with col1:
                    mostrar_grafica(tiempos, valores, eq)
                
                # Estadísticas
                with col2:
                    valor_max = max(valores)
                    valor_min = min(valores)
                    valor_prom = sum(valores) / len(valores)
                    
                    st.subheader("📈 Estadísticas")
                    
                    col_stat1, col_stat2 = st.columns(2)
                    with col_stat1:
                        st.metric("Máximo", f"{valor_max:.4f}")
                        st.metric("Mínimo", f"{valor_min:.4f}")
                    with col_stat2:
                        st.metric("Promedio", f"{valor_prom:.4f}")
                        st.metric("Puntos", len(valores))
                
                # Tabla de datos
                st.subheader("📋 Datos Calculados")
                df = pd.DataFrame({
                    'Tiempo (t)': tiempos,
                    eq.eje_y: valores
                })
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.dataframe(df, width="stretch", height=300)
                with col2:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"{tipo_ecuacion}_datos.csv",
                        mime="text/csv"
                    )
            else:
                st.error("❌ No se pudieron calcular valores válidos")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
