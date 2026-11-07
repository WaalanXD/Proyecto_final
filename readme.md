
# Proyecto Final — Formal Languages (SI2002 / ST0270 / CM0081)

Implementación de los algoritmos de FIRST/FOLLOW, los parsers LL(1) y
SLR(1), y un evaluador de SDD por grafo de dependencias, siguiendo
Aho et al., *Compilers: Principles, Techniques, and Tools* (2nd Edition),
Secciones 4.4, 4.5, 4.6, 5.1 y 5.2.

> **Nota sobre el entregable:** para esta sección del curso no se exige
> informe PDF; el trabajo se sustenta de forma presencial explicando y
> modificando el código en vivo. Este README funciona como guía personal
> de build/run y como referencia rápida para la sustentación (secciones
> del libro seguidas, decisiones de diseño, pendientes).

## Group members

- Kenny Daniel Diaz Diaz
- Salome Bedoya Echavarria

## Environment / versions used

> Completar con los valores reales antes de entregar.

- Operating System: `(pendiente, ej. Windows 11 23H2)`
- Python version: `(pendiente, ej. Python 3.12.x)` — verificar con `python --version`
- Other tools: `(pendiente, ej. LaTeX distribution si se usa para el informe)`

## Project structure

```
Proyecto_final/
├── readme.md                  # este archivo
├── ENUNCIADO_PROYECTO_FINAL.pdf
├── requirements.txt            # dependencias (solo stdlib por defecto)
├── .gitignore
├── src/                        # código fuente (ver detalle abajo)
├── tests/                      # gramáticas y cadenas de prueba
└── docs/                       # notas de diseño de la SDD (Item 3) — útil para la sustentación oral
```

### `src/`

| Archivo                 | Contenido                                                                                                           | Sección del libro             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| `grammar.py`          | Representación de la gramática y lectura de la entrada (Sección 2.2.1 del enunciado)                             | —                             |
| `first_follow.py`     | Cálculo de FIRST(X) y FOLLOW(A)                                                                                    | 4.4.2                          |
| `ll1.py`              | Construcción de la tabla LL(1) y parser predictivo no recursivo                                                    | 4.4.3 – 4.4.4                 |
| `slr1.py`             | Items LR(0), CLOSURE, GOTO, colección canónica, tabla ACTION/GOTO y parser SLR(1)                                 | 4.5, 4.6.2 – 4.6.4            |
| `parse_tree.py`       | Construcción del árbol de derivación a partir de los parsers de Item 2                                           | 5.1.2                          |
| `sdd.py`              | Representación de la SDD **como datos** (producciones, atributos, reglas semánticas)                        | 5.1.1, 5.1.2                   |
| `dependency_graph.py` | Evaluador genérico: construcción del grafo de dependencias, orden topológico, detección de ciclos y evaluación | 5.2.1 – 5.2.2                 |
| `main.py`             | Punto de entrada: maneja `--sets`, selección de parser y flujo de E/S                                            | Sección 2.2 y 3 del enunciado |

> **Estado actual:** el esqueleto contiene las firmas de todas las
> funciones, con docstrings que describen el algoritmo del libro a
> implementar y `raise NotImplementedError` donde falta la lógica. La
> `src/sdd.py` trae además la SDD de ejemplo del libro (profundidad de
> paréntesis balanceados) **solo como referencia de formato**: debe
> remplazarse por una gramática y SDD propias antes de entregar (regla G3
> del enunciado).

## Building and running

Requiere Python 3.10+ (se usa sintaxis `X | None` y `match` en el diseño).
No hay dependencias externas por defecto (ver `requirements.txt`).

### Items 1 y 2 (FIRST/FOLLOW, LL(1), SLR(1))

```powershell
# Leyendo la gramática y las cadenas desde un archivo:
Get-Content .\tests\example1_slr.txt | python .\src\main.py

# Con impresión de los conjuntos First/Follow:
Get-Content .\tests\example1_slr.txt | python .\src\main.py --sets

# De forma interactiva (escribir la gramática y las cadenas por teclado):
python .\src\main.py
```

### Item 3 (SDD)

```powershell
Get-Content .\tests\sdd_tests.txt | python .\src\main.py --sdd
```

Esto imprime, para cada cadena aceptada: el árbol de derivación anotado, el
orden de evaluación de los atributos, y el valor del atributo principal del
símbolo inicial. Si la SDD resulta circular para alguna cadena, se reporta
el ciclo en lugar de evaluar.

## Generative AI tools used

> Completar antes de entregar, según la Sección 1 y 4.2 del enunciado.
> Indicar la herramienta y el propósito exacto (por ejemplo: "se usó
> [herramienta] para aclarar el algoritmo de CLOSURE de la Sección 4.6.2" o
> "para revisar la redacción del informe"), o declarar explícitamente que
> no se usó ninguna.

- `(pendiente)`

## Oral defense checklist

Como la sustentación es presencial y en vivo sobre el código, conviene
tener listo (para cualquier miembro del grupo, el enunciado exige que
todos puedan responder):

- [ ] Poder señalar, para cada algoritmo, la sección/figura exacta del
  libro que se siguió (ver tabla de `src/` arriba).
- [ ] Poder trazar FIRST/FOLLOW, la tabla LL(1) o el automaton LR(0)+tabla
  SLR(1) a mano sobre una gramática nueva, no solo la propia.
- [ ] Poder explicar por qué la SDD propia es S-attributed, L-attributed,
  ambas o ninguna (`docs/sdd_design.md`, Paso 4).
- [ ] Poder modificar una regla semántica en vivo y mostrar que el
  evaluador detecta el ciclo resultante (Paso 6 del enunciado).

## Status / pending work

- [ ] Implementar `grammar.py` (lectura y representación de la gramática).
- [ ] Implementar `first_follow.py` (FIRST, FOLLOW, impresión `--sets`).
- [ ] Implementar `ll1.py` (tabla LL(1) + parser).
- [ ] Implementar `slr1.py` (CLOSURE, GOTO, tabla SLR(1) + parser).
- [ ] Implementar `parse_tree.py` y `dependency_graph.py`.
- [ ] Elegir gramática propia para Items 1–2 (distinta a los ejemplos del enunciado) — ver `tests/README.md`.
- [ ] Elegir gramática y diseñar la SDD propia para el Item 3 (ver `docs/sdd_design.md`), reemplazando el contenido de `src/sdd.py`.
- [ ] Completar las pruebas del Item 3 (5+ cadenas, incluyendo caso circular).
- [ ] Completar las secciones "Environment / versions used" y "Generative AI tools used" de este README.
