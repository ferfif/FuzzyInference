## Funciones de pertenencia

| Variable | Conjunto | Función |
|---|---|---|
| Desempeño | Bajo | Trapezoidal(0, 0, 25, 50) |
| Desempeño | Regular | Triangular(25, 50, 75) |
| Desempeño | Alto | Trapezoidal(50, 75, 100, 100) |
| Entrega (%) | Baja | Trapezoidal(0, 0, 25, 50) |
| Entrega (%) | Regular | Triangular(25, 50, 75) |
| Entrega (%) | Alta | Trapezoidal(50, 75, 100, 100) |
| Beca (%) | Mínima | Z(0, 20) |
| Beca (%) | Baja | Triangular(10, 25, 40) |
| Beca (%) | Regular | Triangular(30, 50, 70) |
| Beca (%) | Alta | Triangular(60, 75, 90) |
| Beca (%) | Excelencia | S(80, 100) |

### Ajustes respecto a la práctica

- **Desempeño / Bajo**: (0, 0, 20, 50) → (0, 0, 25, 50). Con (0,0,20,50) el conjunto bajo empieza a caer en 20 pero 'regular' (25,50,75) no sube hasta 25: entre 20 y 25 aumentar la entrada solo resta fuerza a las reglas que concluyen 'baja' mientras 'mínima' se mantiene, y el centroide desciende hasta 0.0128 pp (p. ej. desempeño 24→25 con entrega 47). Ningún ajuste de la salida puede evitarlo. Alinear la caída en 25 forma una partición complementaria (bajo + regular = 1) y elimina todos los descensos.
- **Desempeño / Alto**: (50, 80, 100, 100) → (50, 75, 100, 100). Simétrico al ajuste de 'bajo': 'regular' termina en 75 pero el conjunto alto solo empezaba a saturar en 80, provocando descensos entre 75 y 80. Con (50,75,100,100) regular + alto = 1.
- **Entrega (%) / Baja**: (0, 0, 20, 50) → (0, 0, 25, 50). Con (0,0,20,50) el conjunto bajo empieza a caer en 20 pero 'regular' (25,50,75) no sube hasta 25: entre 20 y 25 aumentar la entrada solo resta fuerza a las reglas que concluyen 'baja' mientras 'mínima' se mantiene, y el centroide desciende hasta 0.0128 pp (p. ej. desempeño 24→25 con entrega 47). Ningún ajuste de la salida puede evitarlo. Alinear la caída en 25 forma una partición complementaria (bajo + regular = 1) y elimina todos los descensos.
- **Entrega (%) / Alta**: (50, 80, 100, 100) → (50, 75, 100, 100). Simétrico al ajuste de 'bajo': 'regular' termina en 75 pero el conjunto alto solo empezaba a saturar en 80, provocando descensos entre 75 y 80. Con (50,75,100,100) regular + alto = 1.

## Matriz de reglas

| Desempeño \ Entrega | Baja | Regular | Alta |
|---|---|---|---|
| Bajo | Mínima | Baja | Regular |
| Regular | Baja | Regular | Alta |
| Alto | Regular | Alta | Excelencia |

## Reglas y justificación

R1. `IF desempeño IS bajo AND entrega IS baja THEN beca IS mínima` — Ningún indicador muestra compromiso académico; no hay mérito que respalde un apoyo más allá del mínimo.
R2. `IF desempeño IS regular AND entrega IS baja THEN beca IS baja` — Rendimiento aceptable con poca entrega: el conocimiento existe, pero la falta de constancia limita el apoyo a uno reducido.
R3. `IF desempeño IS bajo AND entrega IS regular THEN beca IS baja` — Cumplir con parte de las actividades muestra cierto esfuerzo pese a las evaluaciones bajas; se reconoce con un apoyo reducido. Simétrica a R2.
R4. `IF desempeño IS alto AND entrega IS baja THEN beca IS regular` — Caso cruzado: domina los contenidos pero casi no entrega actividades. Su capacidad justifica un apoyo intermedio; la falta de constancia impide uno alto. Recibe lo mismo que R6: un indicador sobresaliente compensa parcialmente al otro, pero no del todo.
R5. `IF desempeño IS regular AND entrega IS regular THEN beca IS regular` — Desempeño y entrega intermedios: estudiante promedio, apoyo intermedio.
R6. `IF desempeño IS bajo AND entrega IS alta THEN beca IS regular` — Caso cruzado: entrega casi todo pero no lo refleja en evaluaciones. El esfuerzo constante merece apoyo intermedio para que mejore su rendimiento, pero sin resultados no alcanza un apoyo alto. Es simétrica a R4 porque ambos indicadores pesan igual.
R7. `IF desempeño IS alto AND entrega IS regular THEN beca IS alta` — Evaluaciones altas con entrega aceptable: buen mérito académico, apoyo elevado.
R8. `IF desempeño IS regular AND entrega IS alta THEN beca IS alta` — Entrega sobresaliente con evaluaciones aceptables: compromiso alto que se premia con apoyo elevado. Simétrica a R7.
R9. `IF desempeño IS alto AND entrega IS alta THEN beca IS excelencia` — Ambos indicadores sobresalientes: perfil de excelencia, apoyo máximo.
