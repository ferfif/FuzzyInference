# FuzzyInference

Calculadora de becas basada en el desempeño del estudiante. Es un sistema difuso Mamdani hecho con
scikit-fuzzy para la **Práctica 8 de Fundamentos de Inteligencia Artificial**.

A partir de dos entradas:

- el **desempeño en evaluaciones** (0–100),
- la **entrega de actividades** (0–100 %),

recomienda una **beca** en porcentaje del salario mínimo mensual de referencia ($9,582.47 MXN):

```
Importe de beca = (Porcentaje de beca / 100) × $9,582.47
```

Inferencia Mamdani:

- AND = mínimo
- implicación = mínimo
- agregación = máximo
- defuzzificación por centroide

Los universos van de 0 a 100 con paso 1 y ambos extremos incluidos.

## Instalación

Requiere Python 3.10 o superior (probado con 3.12 en Windows 11).

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt        # para ejecutar
pip install -r requirements-dev.txt    # además, para correr las pruebas
```

En Linux, tkinter puede requerir un paquete del sistema (por ejemplo, `sudo apt install python3-tk`).

## Ejecución

| Comando | Qué hace |
|---|---|
| `python main.py` | Abre la interfaz gráfica |
| `python main.py --verify` | Imprime las verificaciones de cobertura y monotonía y la tabla de casos de prueba |
| `python main.py --export out` | Genera en `out/` las figuras y tablas para el reporte |
| `pytest` | Ejecuta las pruebas automáticas |
| `python scripts/make_zip.py` | Crea `Practica08_Beca_Difusa.zip` para la entrega |

### Interfaz

- **Barra lateral**:
  - Slider y campo numérico sincronizados para cada entrada.
  - Beca en % y en pesos.
  - Botones *Ejemplo 70 / 75* y *Restablecer*.
  - Selector de tema claro/oscuro y control de **opacidad de la ventana** (70–100 %).
- **Inferencia**: funciones de pertenencia de las entradas y de la salida con el valor actual marcado, y salida difusa agregada con su centroide.
- **Reglas**:
  - Grados de pertenencia de cada entrada.
  - Matriz 3×3 con las reglas activas resaltadas.
  - Lista R1–R9 con su fuerza de disparo y su justificación.
- **Superficie**: superficie 3D de la beca en función de ambas entradas, con el punto actual marcado. Se puede rotar con el ratón.
- **Verificación**: cobertura, monotonía y casos de prueba, calculados en segundo plano, y exportación de evidencias.

Los valores fuera de 0–100 o que no son números se rechazan, y el campo vuelve al último valor válido.

## Funciones de pertenencia

| Variable | Conjunto | Función |
|---|---|---|
| Desempeño | Bajo | Trapezoidal(0, 0, **25**, 50) |
| Desempeño | Regular | Triangular(25, 50, 75) |
| Desempeño | Alto | Trapezoidal(50, **75**, 100, 100) |
| Entrega | Baja | Trapezoidal(0, 0, **25**, 50) |
| Entrega | Regular | Triangular(25, 50, 75) |
| Entrega | Alta | Trapezoidal(50, **75**, 100, 100) |
| Beca | Mínima | Z(0, 20) |
| Beca | Baja | Triangular(10, 25, 40) |
| Beca | Regular | Triangular(30, 50, 70) |
| Beca | Alta | Triangular(60, 75, 90) |
| Beca | Excelencia | S(80, 100) |

### Ajuste por monotonía

Con los parámetros de ejemplo de la práctica, Bajo = (0, 0, 20, 50) y Alto = (50, 80, 100, 100), la verificación numérica encontró **descensos de hasta 0.0128 puntos porcentuales**. Ocurren entre 20 y 25 y entre 75 y 80 de cada entrada.

La causa es un hueco entre conjuntos. Bajo empieza a caer en 20, pero Regular no sube hasta 25. En ese tramo, aumentar la entrada solo le quita fuerza a las reglas que concluyen *Baja*, mientras *Mínima* se mantiene igual, así que el centroide retrocede. Ningún cambio en la salida puede evitarlo.

**Solución:** alinear los hombros en 25 y 75. Así las entradas forman una partición complementaria (Bajo + Regular = 1 y Regular + Alto = 1). Con este cambio, la superficie es monótona no decreciente en toda la malla de 101 × 101 (0 descensos). El ajuste está registrado en `app/fuzzy/config.py` (`AJUSTES`) y lo fija una prueba automática.

## Reglas

| Desempeño \ Entrega | Baja | Regular | Alta |
|---|---|---|---|
| **Bajo** | Mínima | Baja | Regular |
| **Regular** | Baja | Regular | Alta |
| **Alto** | Regular | Alta | Excelencia |

Las nueve reglas están implementadas explícitamente y con su justificación en `app/fuzzy/rules.py`.

Ambos indicadores pesan lo mismo: subir un nivel en cualquiera de las dos entradas sube un nivel la beca. Los casos cruzados reciben ambos **Regular**:

- desempeño alto con entrega baja (R4),
- desempeño bajo con entrega alta (R6).

Un indicador sobresaliente compensa en parte al otro, pero no basta para una beca alta.

## Resultados (casos de la práctica)

| Desempeño | Entrega | Reglas activas (fuerza) | Beca | Importe |
|---:|---:|---|---:|---:|
| 0 | 0 | R1 = 1.00 | 5.84 % | $559.78 |
| 100 | 100 | R9 = 1.00 | 94.16 % | $9,022.69 |
| 40 | 95 | R6 = 0.40, R8 = 0.60 | 62.26 % | $5,966.24 |
| 90 | 30 | R4 = 0.80, R7 = 0.20 | 54.97 % | $5,267.34 |
| 70 | 75 | R8 = 0.20, R9 = 0.80 | 86.90 % | $8,326.86 |

La inferencia no llega exactamente a 0 % ni a 100 %: el centroide de *Mínima* es ≈ 5.84 % y el de *Excelencia* ≈ 94.16 %.

`python main.py --export out` produce:

- `out/casos.md`: los casos de solapamiento y la explicación paso a paso de tres casos.
- `out/reglas.md`: funciones, matriz y justificaciones.
- `out/verificacion.txt`: el resumen de la verificación.
- Las figuras PNG.

## Estructura

```
main.py                 punto de entrada (GUI / --verify / --export)
app/fuzzy/              configuración, reglas, motor skfuzzy y evaluación vectorizada en malla
app/analysis/           verificación, gráficas y exportación
app/gui/                interfaz customtkinter (ventana, tema, pestañas)
tests/                  pruebas pytest
scripts/make_zip.py     empaquetado del entregable
```

El porcentaje oficial de cada inferencia lo calcula `skfuzzy.control.ControlSystemSimulation`.

La malla completa (cobertura, monotonía y superficie) se evalúa con una implementación vectorizada que replica el mismo algoritmo: sobremuestreo del universo y centroide lineal a tramos. Una prueba verifica que ambos cálculos coinciden con un error menor que 1e-6.
