# Casos de prueba

Estos archivos reproducen los ejemplos del enunciado (`ENUNCIADO_PROYECTO_FINAL.pdf`,
Seccion 5) para validar la implementacion de los Items 1 y 2 antes de probar
con gramaticas propias.

| Archivo | Gramatica | Resultado esperado |
|---|---|---|
| `example1_slr.txt` | Expresiones con +,* y parentesis | `Grammar is SLR(1).` luego `yes`, `yes`, `no` |
| `example2_ll.txt` | `S -> AB`, `A -> aA | d`, `B -> bBc | e` | `Select a parser...`, con T: `yes`, `yes`, `no`, luego vuelve a preguntar y termina con Q |
| `example3_neither.txt` | `S -> SS | a` (ambigua, recursiva izq.) | `Grammar is neither LL(1) nor SLR(1).` |
| `custom_grammar.txt` | Gramática propia: `S -> (L) | x`, `L -> SM`, `M -> SM | e` (listas anidadas entre paréntesis) | `Select a parser...`; con T y con B: `yes`, `yes`, `yes`, `no`, `no` (ver `docs/custom_grammar_design.md`) |
| `sdd_tests.txt` | Gramática propia del Item 3: `S -> L`, `L -> TL | e`, `T -> +N | -N`, `N -> dN | d` | Ver `docs/sdd_design.md` para el detalle de cada cadena |

## Como ejecutar

```powershell
Get-Content .\tests\example1_slr.txt | python .\src\main.py
Get-Content .\tests\example2_ll.txt | python .\src\main.py
Get-Content .\tests\example3_neither.txt | python .\src\main.py
Get-Content .\tests\custom_grammar.txt | python .\src\main.py
Get-Content .\tests\sdd_tests.txt | python .\src\main.py --sdd
```
