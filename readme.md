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

> Completar con los valores reales de la máquina de cada integrante antes
> de entregar/sustentar (pueden diferir entre miembros del grupo).

- Operating System: Windows 11 25H2
- Python version: Python 3.14.4 — verificar con `py --version` (ver nota abajo)
- Other tools: ninguna dependencia externa (ver `requirements.txt`)

> **Nota sobre el comando de Python en Windows:** en Windows, `python` a
> veces no está en el PATH y en su lugar existe un *alias* de la
> Microsoft Store que falla con el mensaje `Python was not found; run without arguments to install from the Microsoft Store...`. Si eso pasa,
> usar `py` en vez de `python` (viene con el lanzador oficial de Python
> para Windows). Todos los comandos de este README usan `py`; si en la
> máquina de la sustentación sí funciona `python`, son intercambiables.

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

> **Estado actual:** todos los módulos (`grammar.py`, `first_follow.py`,
> `ll1.py`, `slr1.py`, `parse_tree.py`, `dependency_graph.py`, `main.py`)
> están implementados y probados contra los ejemplos de `tests/`.
> `src/sdd.py` ya tiene la SDD propia (ver `docs/sdd_design.md`): una
> "cinta de incrementos/decrementos" (`S -> L`, `L -> TL | e`,
> `T -> +N | -N`, `N -> dN | d`), no la de ejemplo del libro.

## Building and running

Requiere Python 3.10+ (se usa sintaxis `X | None` en el diseño).
No hay dependencias externas (ver `requirements.txt`), así que no hace
falta crear un entorno virtual ni instalar nada: solo tener Python.

Todos los comandos se ejecutan **desde la raíz del repo** (el directorio
`Proyecto_final/`), no desde `src/`.

### Items 1 y 2 (FIRST/FOLLOW, LL(1), SLR(1))

```powershell
# Caso 3: gramática SLR(1) pura -> "Grammar is SLR(1)." + yes/no por cadena
Get-Content .\tests\example1_slr.txt | py .\src\main.py

# Caso 1: gramática LL(1) Y SLR(1) -> deja elegir el parser (T/B) en bucle hasta Q
Get-Content .\tests\example2_ll.txt | py .\src\main.py

# Caso 4: ni LL(1) ni SLR(1) -> "Grammar is neither LL(1) nor SLR(1)."
Get-Content .\tests\example3_neither.txt | py .\src\main.py

# Gramática propia para Items 1-2 (ver docs/custom_grammar_design.md
# para FIRST/FOLLOW, tabla LL(1), automata LR(0)+SLR(1) y trazado a mano)
Get-Content .\tests\custom_grammar.txt | py .\src\main.py

# Con impresión de los conjuntos First/Follow (se puede combinar con
# cualquiera de los archivos anteriores):
Get-Content .\tests\example1_slr.txt | py .\src\main.py --sets

# De forma interactiva (escribir la gramática y las cadenas por teclado,
# sin redirigir un archivo): primero la línea con el número de no
# terminales, luego una producción por línea, luego las cadenas (una por
# línea, la cadena vacía se escribe como "e"), terminando con una línea
# en blanco.
py .\src\main.py
```

### Item 3 (SDD)

```powershell
Get-Content .\tests\sdd_tests.txt | py .\src\main.py --sdd
```

Esto imprime, para cada cadena aceptada: el árbol de derivación anotado, el
orden de evaluación de los atributos, y el valor del atributo principal del
símbolo inicial (`val` en la SDD propia, ver `docs/sdd_design.md`). Si la
cadena no pertenece al lenguaje, imprime `no`. Si la SDD resultara
circular para alguna cadena, se reporta `La SDD es circular para esta cadena.` en lugar de evaluar.

### Demostrar en vivo la detección de SDD circular (Paso 6 del enunciado)

No hay un flag para esto: se modifica temporalmente una regla en
`src/sdd.py` para introducir un ciclo, se ejecuta el programa, se muestra
el mensaje de error, y se revierte el cambio. El procedimiento exacto
(qué línea cambiar y qué salida esperar) está documentado paso a paso en
`docs/sdd_design.md`, sección "Evidencia de detección de SDD circular".

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

- [X] Implementar `grammar.py` (lectura y representación de la gramática).
- [X] Implementar `first_follow.py` (FIRST, FOLLOW, impresión `--sets`).
- [X] Implementar `ll1.py` (tabla LL(1) + parser).
- [X] Implementar `slr1.py` (CLOSURE, GOTO, tabla SLR(1) + parser).
- [X] Implementar `parse_tree.py` y `dependency_graph.py`.
- [X] Elegir gramática y diseñar la SDD propia para el Item 3 (ver `docs/sdd_design.md`), reemplazando el contenido de `src/sdd.py`.
- [X] Completar las pruebas del Item 3 (7 cadenas en `tests/sdd_tests.txt`, incluyendo caso circular documentado en `docs/sdd_design.md`).
- [X] Elegir gramática propia para Items 1–2 (distinta a los ejemplos del enunciado) — ver `tests/custom_grammar.txt` y `docs/custom_grammar_design.md`.
- [ ] Completar las secciones "Environment / versions used" y "Generative AI tools used" de este README.
