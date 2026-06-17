from flask import Flask, render_template, request, jsonify
import math
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
from io import BytesIO
import base64

app = Flask(__name__)

def calcular_cola(t, a, C):
    return t * (a * math.log(t) + C)

def generar_grafica(tiempos, colas):
    """Genera una gráfica y la convierte a base64 para mostrar en HTML"""
    plt.figure(figsize=(10, 6))
    plt.plot(tiempos, colas, marker="o", linestyle="-", linewidth=2, 
             color="blue", markersize=6, label="q(t)")
    plt.xlabel("Tiempo normalizado t", fontsize=12)
    plt.ylabel("Solicitudes pendientes q(t)", fontsize=12)
    plt.title("Evolución de la cola de solicitudes", fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()
    
    # Convertir a base64 para mostrar en HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return imagen_base64

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        datos = request.json
        a = float(datos['a'])
        t0 = float(datos['t0'])
        q0 = float(datos['q0'])
        tf = float(datos['tf'])
        paso = float(datos['paso'])
        
        # Validaciones
        if t0 <= 0 or tf <= 0:
            return jsonify({'error': 'El tiempo inicial y final deben ser mayores que 0'}), 400
        
        if t0 > tf:
            return jsonify({'error': 'El tiempo inicial debe ser menor que el final'}), 400
        
        if paso <= 0:
            return jsonify({'error': 'El paso debe ser mayor que 0'}), 400
        
        # Calcular constante C
        C = (q0 / t0) - a * math.log(t0)
        
        # Generar datos
        tiempos = []
        colas = []
        
        t = t0
        while t <= tf:
            q = calcular_cola(t, a, C)
            tiempos.append(round(t, 4))
            colas.append(round(q, 4))
            t += paso
        
        # Generar gráfica
        imagen = generar_grafica(tiempos, colas)
        
        # Calcular estadísticas
        q_max = max(colas)
        q_min = min(colas)
        q_promedio = sum(colas) / len(colas)
        
        return jsonify({
            'exito': True,
            'tiempos': tiempos,
            'colas': colas,
            'imagen': imagen,
            'q_max': round(q_max, 4),
            'q_min': round(q_min, 4),
            'q_promedio': round(q_promedio, 4),
            'puntos': len(colas)
        })
    
    except ValueError:
        return jsonify({'error': 'Por favor ingresa valores numéricos válidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
