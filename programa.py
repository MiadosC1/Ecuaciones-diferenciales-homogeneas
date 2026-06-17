import math
import matplotlib.pyplot as plt

def calcular_cola(t, a, C):
    return t * (a * math.log(t) + C)

def main():
    print("Modelo de cola de solicitudes en un servidor web")
    print("Ecuación diferencial: dq/dt = a + q/t")

    a = float(input("Ingrese el valor de a, factor de crecimiento de la cola: "))
    t0 = float(input("Ingrese el tiempo inicial t0, mayor que 0: "))
    q0 = float(input("Ingrese la cola inicial q0: "))
    tf = float(input("Ingrese el tiempo final: "))
    paso = float(input("Ingrese el paso de tiempo: "))

    if t0 <= 0 or tf <= 0:
        print("Error: t0 y tf deben ser mayores que 0.")
        return

    C = (q0 / t0) - a * math.log(t0)

    tiempos = []
    colas = []

    t = t0
    while t <= tf:
        q = calcular_cola(t, a, C)
        tiempos.append(t)
        colas.append(q)
        print(f"t = {t:.2f}, q(t) = {q:.4f}")
        t += paso

    plt.plot(tiempos, colas, marker="o")
    plt.xlabel("Tiempo normalizado t")
    plt.ylabel("Solicitudes pendientes q(t)")
    plt.title("Evolución de la cola de solicitudes en un servidor web")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()