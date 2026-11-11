# Diseño de la SDD (Item 3)

> Este documento resuelve los Pasos 1 a 4 y 6 de la Sección 3 del
> enunciado para la SDD propia implementada en `src/sdd.py`. La SDD de
> ejemplo del enunciado (profundidad de paréntesis balanceados) ya fue
> remplazada; no se entrega.

## Paso 1: Gramática elegida

```
S -> L
L -> TL e
T -> +N -N
N -> dN d
```

Es decir (formato de alternativas separadas por espacio, Sección 2.2.1):

- `S -> L`
- `L -> T L | e`
- `T -> + N | - N`
- `N -> d N | d`

Cumple G1–G3:

- [x] Sigue las convenciones de la Sección 2.2: `S` es el inicial, los no
      terminales (`S`, `L`, `T`, `N`) son mayúsculas, los terminales
      (`+`, `-`, `d`) son de un carácter, `e` representa épsilon.
- [x] Es SLR(1) según el propio programa (ver verificación abajo). No es
      LL(1) (el programa no pregunta por el parser, solo imprime
      `Grammar is SLR(1).`), pero el enunciado solo exige una de las dos.
- [x] Tiene 4 no terminales (≥3) y 7 producciones (≥6): `S->L`, `L->TL`,
      `L->e`, `T->+N`, `T->-N`, `N->dN`, `N->d`.
- [x] `L` y `N` son recursivas (por la derecha).
- [x] No es ninguna gramática del libro ni del enunciado: no es la
      gramática de expresiones con `+ * ( )`, ni `S -> AB` con
      `A -> aA|d`/`B -> bBc|e`, ni `S -> SS|a`, ni la SDD de ejemplo de
      profundidad de paréntesis (`S -> P`, `P -> (P)P | e`).

### Verificación con el programa (Item 2)

```powershell
"4`nS -> L`nL -> TL e`nT -> +N -N`nN -> dN d`n" | py .\src\main.py --sets
```

Salida real obtenida:

```
First(L) = {+, -, e}
Follow(L) = {$}
First(N) = {d}
Follow(N) = {+, -, $}
First(S) = {+, -, e}
Follow(S) = {$}
First(T) = {+, -}
Follow(T) = {+, -, $}
Grammar is SLR(1).
```

### Lenguaje que reconoce

Secuencias (posiblemente vacías) de operaciones `+N` o `-N`, donde `N` es
una o más repeticiones de `d` y su longitud representa una magnitud
entera. Por ejemplo, `+dd-d` se lee como "sumar 2, luego restar 1".

## Paso 2: Definición de la SDD

### Tabla de atributos

| Símbolo | Atributo | Tipo | Dominio | Significado |
|---|---|---|---|---|
| `N` | `val` | sintetizado | entero ≥ 1 | cantidad de `d` en `N` (magnitud de la operación) |
| `T` | `val` | sintetizado | entero | valor con signo de la operación (`+N.val` o `-N.val`) |
| `L` | `acc` | **heredado** | entero | acumulador antes de procesar esta sublista |
| `L` | `val` | sintetizado | entero | acumulador después de procesar esta sublista |
| `S` | `val` | sintetizado | entero | resultado final de la cadena completa |

Cumple la Sección 5.1.1:

- [x] Hay al menos dos atributos distintos (`acc`, `val`), con al menos
      uno sintetizado y uno heredado.
- [x] `S` no tiene atributos heredados (solo `val`, sintetizado).
- [x] Cada regla define exactamente un atributo usando solo atributos de
      la misma producción (ver tabla de reglas abajo: nunca se accede a
      un atributo de un nieto, solo de head/hijos directos).
- [x] Cada atributo sintetizado del head y cada atributo heredado de cada
      no terminal del cuerpo se define exactamente una vez por producción
      (verificado al implementar `SDD_RULES` en `src/sdd.py`: una
      `SemanticRule` por atributo y producción).

### Reglas semánticas (formato Fig. 5.1 del libro)

Notación: posición 0 = head, posición *i* (1-indexada) = *i*-ésimo símbolo
del cuerpo. En `L -> T L`, `L₁` es el head (posición 0) y `L₂` es el `L`
del cuerpo (posición 2).

| Producción | Reglas semánticas |
|---|---|
| `S -> L` | `L.acc = 0` <br> `S.val = L.val` |
| `L -> T L` | `L₂.acc = L₁.acc + T.val` <br> `L₁.val = L₂.val` |
| `L -> e` | `L.val = L.acc` |
| `T -> + N` | `T.val = N.val` |
| `T -> - N` | `T.val = -N.val` |
| `N -> d N` | `N₁.val = 1 + N₂.val` |
| `N -> d` | `N.val = 1` |

Implementación exacta en `src/sdd.py` (`SDD_RULES`).

## Paso 3: Ejemplo a mano

Cadena elegida: `+dd-d` (4 terminales: "sumar 2, luego restar 1").

### Árbol de derivación anotado

```
S {val: 1}
└── L {acc: 0, val: 1}
    ├── T {val: 2}
    │   ├── + {lexval: '+'}
    │   └── N {val: 2}
    │       ├── d {lexval: 'd'}
    │       └── N {val: 1}
    │           └── d {lexval: 'd'}
    └── L {acc: 2, val: 1}
        ├── T {val: -1}
        │   ├── - {lexval: '-'}
        │   └── N {val: 1}
        │       └── d {lexval: 'd'}
        └── L {acc: 1, val: 1}
            └── e {lexval: 'e'}
```

(Coincide exactamente con la salida real de `python src/main.py --sdd`
para esta cadena.)

### Grafo de dependencias

Un vértice por atributo de cada nodo concreto del árbol; una arista desde
cada atributo usado hacia el atributo que lo usa para definirse:

```
N(dd interior).val  ──┐
                       ├──> N(dd exterior).val ──> T(primero).val ──┐
                                                                      │
                                                                      ▼
L(raíz).acc = 0 ───────────────────────────────────────────────> L(segundo).acc
                                                                      │
N(tercera d).val ──> T(segundo).val ─────────────────────────────────┘
                                                                      │
                                                                      ▼
                                                              L(tercero, vacío).acc
                                                                      │
                                                                      ▼ (L->e: val = acc)
                                                              L(tercero).val
                                                                      │
                                                                      ▼ (L1.val = L2.val)
                                                              L(segundo).val
                                                                      │
                                                                      ▼
                                                              L(raíz).val ──> S.val
```

### Orden de evaluación (orden topológico)

Uno de los órdenes válidos (coincide con el calculado por
`dependency_graph.topological_order`, usando el algoritmo de Kahn):

1. `N(dd interior).val = 1`
2. `N(dd exterior).val = 1 + 1 = 2`
3. `T(primero).val = 2`
4. `N(tercera d).val = 1`
5. `T(segundo).val = -1`
6. `L(raíz).acc = 0`
7. `L(segundo).acc = 0 + 2 = 2`
8. `L(tercero, vacío).acc = 2 + (-1) = 1`
9. `L(tercero).val = 1` (caso base `L -> e`)
10. `L(segundo).val = 1`
11. `L(raíz).val = 1`
12. `S.val = 1`

Resultado final: **`val = 1`**, que coincide con `2 - 1 = 1` y con la
salida real del programa.

## Paso 4: Clasificación de la SDD

- **¿Es S-attributed?** No. `L.acc` es un atributo heredado (no se calcula
  a partir de los atributos de los propios hijos de `L`, sino de su
  hermano izquierdo `T` y del heredado de su padre). Basta un atributo
  heredado para que la SDD no sea S-attributed.

- **¿Es L-attributed?** Sí. La Sección 5.2.4 exige que cada atributo
  heredado de un símbolo del cuerpo dependa solo de: (a) atributos
  heredados del head, (b) atributos (heredados o sintetizados) de los
  símbolos a su izquierda en el mismo cuerpo, o (c) atributos del propio
  símbolo, sin ciclos. El único atributo heredado de la SDD es `L₂.acc`
  (producción `L -> T L`), y depende de `L₁.acc` (heredado del head) y de
  `T.val` (sintetizado de `T`, que está a la izquierda de `L₂` en el
  cuerpo). Ningún otro no terminal del cuerpo recibe atributos heredados
  en ninguna producción. Por lo tanto, la condición se cumple en todas
  las producciones.

- **Justificación:** al ser L-attributed (y no S-attributed), en principio
  se podría evaluar con una sola pasada durante un análisis descendente
  con acciones intercaladas. Aun así, siguiendo el enunciado, el proyecto
  implementa el método general de evaluación por grafo de dependencias y
  orden topológico (`dependency_graph.py`), válido para cualquier SDD
  cuyo grafo de dependencias no tenga ciclos, no solo para las
  L-attributed.

## Paso 6: Plan de pruebas

Archivo: `tests/sdd_tests.txt` (gramática + 7 cadenas). Ejecutado con:

```powershell
Get-Content .\tests\sdd_tests.txt | py .\src\main.py --sdd
```

| # | Cadena | Resultado esperado | Resultado real |
|---|---|---|---|
| 1 | `e` (lista vacía, más corta del lenguaje) | `val = 0` | `val = 0` ✓ |
| 2 | `+d` | `val = 1` | `val = 1` ✓ |
| 3 | `+dd-d` (ejemplo del Paso 3) | `val = 1` | `val = 1` ✓ |
| 4 | `-ddd` | `val = -3` | `val = -3` ✓ |
| 5 | `+ddd-dd+d-dddd` (recursión profunda, 4 operaciones anidadas) | `3 - 2 + 1 - 4 = -2` | `val = -2` ✓ |
| 6 | `+d+` (NO pertenece al lenguaje: signo sin dígitos al final) | `no` | `no` ✓ |
| 7 | `d` (NO pertenece al lenguaje: dígito sin signo) | `no` | `no` ✓ |

### Evidencia de detección de SDD circular

Procedimiento reproducible (modifica temporalmente la regla de
`L -> T L` en `src/sdd.py`): cambiar la dependencia de `L₂.acc` de
`L₁.acc` a `L₁.val`, lo que crea el ciclo `L₁.val → L₂.acc → L₂.val → L₁.val`
(porque `L₁.val` ya depende de `L₂.val`, y `L₂.val` depende de `L₂.acc`
en la producción `L -> e` o `L -> T L` siguiente):

```python
# Cambio temporal introducido en SDD_RULES[("L", ("T", "L"))]:
SemanticRule(
    AttributeRef(2, "acc"),
    (AttributeRef(0, "val"), AttributeRef(1, "val")),  # antes: AttributeRef(0, "acc")
    lambda val, t_val: val + t_val,
),
```

Con este cambio, ejecutar:

```powershell
"4`nS -> L`nL -> TL e`nT -> +N -N`nN -> dN d`n+d`n" | py .\src\main.py --sdd
```

produce:

```
La SDD es circular para esta cadena.
```

tal como exige `main.py` (ver `dependency_graph.CircularSDDError`). Tras
esta verificación, el cambio se revirtió y `src/sdd.py` quedó con la regla
original (`L₂.acc = L₁.acc + T.val`), re-verificada con `+d` → `val = 1`.
