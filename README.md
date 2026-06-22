# Ecuaciones diferenciales homogéneas

Repositorio de apoyo para el estudio y práctica de **ecuaciones diferenciales homogéneas** (EDO de primer orden), con teoría, ejemplos resueltos y ejercicios propuestos.

## 📘 Descripción

Este proyecto reúne material educativo para comprender, resolver e interpretar ecuaciones diferenciales homogéneas de la forma:

\[
\frac{dy}{dx} = F\left(\frac{y}{x}\right)
\]

Incluye explicaciones paso a paso, técnicas de sustitución y ejercicios para reforzar el aprendizaje.

## 🎯 Objetivos

- Entender qué es una ecuación diferencial homogénea.
- Aplicar la sustitución \( y = vx \) (o \( x = vy \), según convenga).
- Resolver ejercicios de forma ordenada.
- Verificar soluciones y analizar su comportamiento.

## 🧠 Temas cubiertos

- Definición de EDO homogénea.
- Criterios para identificar homogeneidad.
- Método de sustitución.
- Integración y solución general.
- Ejemplos resueltos paso a paso.
- Ejercicios propuestos.

## 🗂️ Estructura del repositorio

```text
.
├── README.md
├── teoria/            # Explicaciones conceptuales
├── ejemplos/          # Ejercicios resueltos
└── ejercicios/        # Problemas para practicar
```

> Si aún no tienes estas carpetas, puedes crearlas conforme crezca el contenido.

## 🚀 Cómo usar este repositorio

1. Lee la sección de teoría.
2. Revisa los ejemplos resueltos.
3. Intenta resolver los ejercicios por tu cuenta.
4. Compara tus resultados y verifica procedimientos.

## ✅ Ejemplo rápido

Ecuación:
\[
\frac{dy}{dx} = \frac{x+y}{x}
\]

Reescritura:
\[
\frac{dy}{dx} = 1 + \frac{y}{x}
\]
Depende de \(y/x\), por lo tanto es homogénea (tras reorganizar).

Sustitución:
\[
y = vx \Rightarrow \frac{dy}{dx} = v + x\frac{dv}{dx}
\]

A partir de aquí se obtiene una ecuación en \(v\) y \(x\) que se resuelve por separación de variables.

## 🤝 Contribuciones

Si deseas aportar más ejercicios, correcciones o mejoras de redacción, abre un *pull request* o un *issue*.

## 📄 Licencia

Puedes usar una licencia abierta como **MIT** para facilitar reutilización académica.
