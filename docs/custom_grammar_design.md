# Gramática propia para los Items 1 y 2

> Este documento resuelve, para la gramática propia usada en el informe o
> la sustentación de los Items 1–2, lo que el enunciado pide poder
> mostrar: FIRST/FOLLOW, la tabla LL(1) o el automata LR(0)+tabla SLR(1),
> y una cadena parseada paso a paso. El archivo ejecutable correspondiente
> es `tests/custom_grammar.txt`.

## Gramática

```
S -> (L) x
L -> SM
M -> SM e
```

Es decir (una alternativa por línea):

- `S -> ( L ) | x`
- `L -> S M`
- `M -> S M | e`

Cumple los mismos requisitos que se exigieron para la SDD (G1–G3 del
enunciado, aplicados aquí a Items 1–2):

- [x] Convenciones de la Sección 2.2: `S` inicial, no terminales en
      mayúscula (`S`, `L`, `M`), terminales de un carácter (`(`, `)`, `x`),
      `e` para épsilon.
- [x] 3 no terminales (≥3) y 5 producciones (≥3 producciones normalmente
      exigidas para Items 1-2, cumple con margen).
- [x] Recursión: `S`, `L` y `M` son mutuamente recursivas (`S` puede
      contener `L`, que contiene `S` y `M`, que a su vez puede volver a
      contener `S`).
- [x] No coincide con `example1_slr.txt` (expresiones `+ * ( )`),
      `example2_ll.txt` (`S->AB`, `A->aA|d`, `B->bBc|e`),
      `example3_neither.txt` (`S->SS|a`), ni con gramáticas típicas del
      libro (expresiones con precedencia, declaraciones, etc.).

### Lenguaje que reconoce

Listas no vacías de átomos `x` o de sublistas anidadas entre paréntesis,
cada elemento de una lista pegado al siguiente sin separador explícito.
Ejemplos: `x`, `(x)`, `(xx)`, `((x)x(xx))`.

## Verificación con el programa (Item 2)

```powershell
"3`nS -> (L) x`nL -> SM`nM -> SM e`n" | py .\src\main.py --sets
```

Salida real obtenida:

```
First(L) = {(, x}
Follow(L) = {)}
First(M) = {(, x, e}
Follow(M) = {)}
First(S) = {(, x}
Follow(S) = {(, ), x, $}
Select a parser (T: for LL(1), B: for SLR(1), Q: quit):
```

Es decir, la gramática es **tanto LL(1) como SLR(1)** (Caso 1 del
enunciado, Sección 2.2.2): el programa ofrece elegir el parser en bucle.

## Tabla de parsing LL(1)

Producciones numeradas: (1) `S->(L)`, (2) `S->x`, (3) `L->SM`,
(4) `M->SM`, (5) `M->e`.

| | `(` | `)` | `x` | `$` |
|---|---|---|---|---|
| `S` | (1) `S->(L)` | | (2) `S->x` | |
| `L` | (3) `L->SM` | | (3) `L->SM` | |
| `M` | (4) `M->SM` | (5) `M->e` | (4) `M->SM` | |

Ninguna celda tiene más de una entrada: confirma que es LL(1).

### Trazado paso a paso (parser LL(1)) de `(xx)`

| Pila (tope a la derecha) | Entrada restante | Acción |
|---|---|---|
| `$ S` | `(xx)$` | `M[S,(] = S->(L)` |
| `$ ) L (` | `(xx)$` | match `(` |
| `$ ) L` | `xx)$` | `M[L,x] = L->SM` |
| `$ ) M S` | `xx)$` | `M[S,x] = S->x` |
| `$ ) M x` | `xx)$` | match `x` |
| `$ ) M` | `x)$` | `M[M,x] = M->SM` |
| `$ ) M S` | `x)$` | `M[S,x] = S->x` |
| `$ ) M x` | `x)$` | match `x` |
| `$ ) M` | `)$` | `M[M,)] = M->e` |
| `$ )` | `)$` | match `)` |
| `$` | `$` | **aceptar** |

## Automata LR(0) y tabla SLR(1)

Gramática aumentada: `S' -> S`.

| Estado | Items (resumen) | Transiciones |
|---|---|---|
| I0 | `S'→·S`, `S→·(L)`, `S→·x` | `(`→I2, `x`→I3, `S`→I1 |
| I1 | `S'→S·` | (aceptar) |
| I2 | `S→(·L)`, `L→·SM`, `S→·(L)`, `S→·x` | `(`→I2, `x`→I3, `L`→I4, `S`→I5 |
| I3 | `S→x·` | reduce `S→x` |
| I4 | `S→(L·)` | `)`→I8 |
| I5 | `L→S·M`, `M→·SM`, `M→·e`, `S→·(L)`, `S→·x` | `(`→I2, `x`→I3, `M`→I9, `S`→I10 (reduce `M→e` con lookahead `)`) |
| I8 | `S→(L)·` | reduce `S→(L)` |
| I9 | `L→SM·` | reduce `L→SM` |
| I10 | `M→S·M`, `M→·SM`, `M→·e`, `S→·(L)`, `S→·x` | `(`→I2, `x`→I3, `M`→I11 (reduce `M→e` con lookahead `)`) |
| I11 | `M→SM·` | reduce `M→SM` |

### Trazado paso a paso (parser SLR(1)) de `(xx)`

| Pila de estados | Entrada restante | Acción |
|---|---|---|
| `0` | `(xx)$` | shift `(` → 2 |
| `0 2` | `xx)$` | shift `x` → 3 |
| `0 2 3` | `x)$` | reduce `S→x`; GOTO(2,S)=5 |
| `0 2 5` | `x)$` | shift `x` → 3 |
| `0 2 5 3` | `)$` | reduce `S→x`; GOTO(5,S)=10 |
| `0 2 5 10` | `)$` | reduce `M→e` (lookahead `)`); GOTO(10,M)=11 |
| `0 2 5 10 11` | `)$` | reduce `M→SM`; GOTO(5,M)=9 |
| `0 2 5 9` | `)$` | reduce `L→SM`; GOTO(2,L)=4 |
| `0 2 4` | `)$` | shift `)` → 8 |
| `0 2 4 8` | `$` | reduce `S→(L)`; GOTO(0,S)=1 |
| `0 1` | `$` | **aceptar** |

Ambos parsers aceptan `(xx)` siguiendo caminos distintos pero
consistentes con el mismo árbol de derivación.

## Plan de pruebas

Archivo: `tests/custom_grammar.txt`. Ejecutado con:

```powershell
Get-Content .\tests\custom_grammar.txt | py .\src\main.py
```

Salida real (idéntica para T y B, como debe ser al coincidir ambos
parsers en el mismo lenguaje):

| Cadena | Esperado | LL(1) (T) | SLR(1) (B) |
|---|---|---|---|
| `x` | pertenece | `yes` | `yes` |
| `(xx)` | pertenece | `yes` | `yes` |
| `((x)x(xx))` | pertenece (anidamiento profundo) | `yes` | `yes` |
| `(x` | NO pertenece (paréntesis sin cerrar) | `no` | `no` |
| `)` | NO pertenece (empieza con cierre) | `no` | `no` |
