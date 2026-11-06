# Casos de prueba

| Tipo | Desempeño | Entrega | Reglas activas (fuerza) | Beca (%) | Importe |
|---|---:|---:|---|---:|---:|
| obligatorio | 0 | 0 | R1=1.00 | 5.84 | $559.78 MXN |
| obligatorio | 100 | 100 | R9=1.00 | 94.16 | $9,022.69 MXN |
| obligatorio | 40 | 95 | R6=0.40, R8=0.60 | 62.26 | $5,966.24 MXN |
| obligatorio | 90 | 30 | R4=0.80, R7=0.20 | 54.97 | $5,267.34 MXN |
| obligatorio | 70 | 75 | R8=0.20, R9=0.80 | 86.90 | $8,326.86 MXN |
| solapamiento | 35 | 35 | R1=0.60, R2=0.40, R3=0.40, R5=0.40 | 31.30 | $2,999.69 MXN |
| solapamiento | 50 | 60 | R5=0.60, R8=0.40 | 58.77 | $5,631.54 MXN |
| solapamiento | 65 | 40 | R2=0.40, R4=0.40, R5=0.40, R7=0.60 | 52.33 | $5,014.66 MXN |
| solapamiento | 30 | 70 | R3=0.20, R5=0.20, R6=0.80, R8=0.20 | 50.00 | $4,791.24 MXN |

## Casos explicados

### Desempeño = 40, entrega = 95

- Pertenencias de desempeño: Bajo = 0.40, Regular = 0.60, Alto = 0.00
- Pertenencias de entrega (%): Baja = 0.00, Regular = 0.00, Alta = 1.00
- Reglas activadas:
  - **R6** (IF desempeño IS bajo AND entrega IS alta THEN beca IS regular): fuerza = min(0.40, 1.00) = 0.40
  - **R8** (IF desempeño IS regular AND entrega IS alta THEN beca IS alta): fuerza = min(0.60, 1.00) = 0.60
- Recortes de la salida (agregación por máximo): Regular ≤ 0.40, Alta ≤ 0.60
- Centroide de la salida agregada: **62.26 %** → importe = 62.26 / 100 × $9,582.47 = **$5,966.24 MXN**

### Desempeño = 90, entrega = 30

- Pertenencias de desempeño: Bajo = 0.00, Regular = 0.00, Alto = 1.00
- Pertenencias de entrega (%): Baja = 0.80, Regular = 0.20, Alta = 0.00
- Reglas activadas:
  - **R4** (IF desempeño IS alto AND entrega IS baja THEN beca IS regular): fuerza = min(1.00, 0.80) = 0.80
  - **R7** (IF desempeño IS alto AND entrega IS regular THEN beca IS alta): fuerza = min(1.00, 0.20) = 0.20
- Recortes de la salida (agregación por máximo): Regular ≤ 0.80, Alta ≤ 0.20
- Centroide de la salida agregada: **54.97 %** → importe = 54.97 / 100 × $9,582.47 = **$5,267.34 MXN**

### Desempeño = 70, entrega = 75

- Pertenencias de desempeño: Bajo = 0.00, Regular = 0.20, Alto = 0.80
- Pertenencias de entrega (%): Baja = 0.00, Regular = 0.00, Alta = 1.00
- Reglas activadas:
  - **R8** (IF desempeño IS regular AND entrega IS alta THEN beca IS alta): fuerza = min(0.20, 1.00) = 0.20
  - **R9** (IF desempeño IS alto AND entrega IS alta THEN beca IS excelencia): fuerza = min(0.80, 1.00) = 0.80
- Recortes de la salida (agregación por máximo): Alta ≤ 0.20, Excelencia ≤ 0.80
- Centroide de la salida agregada: **86.90 %** → importe = 86.90 / 100 × $9,582.47 = **$8,326.86 MXN**
