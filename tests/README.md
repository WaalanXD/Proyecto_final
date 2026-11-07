# Casos de prueba

Estos archivos reproducen los ejemplos del enunciado (`ENUNCIADO_PROYECTO_FINAL.pdf`,
Seccion 5) para validar la implementacion de los Items 1 y 2 antes de probar
con gramaticas propias.

| Archivo | Gramatica | Resultado esperado |
|---|---|---|
| `example1_slr.txt` | Expresiones con +,* y parentesis | `Grammar is SLR(1).` luego `yes`, `yes`, `no` |
| `example2_ll.txt` | `S -> AB`, `A -> aA | d`, `B -> bBc | e` | `Select a parser...`, con T: `yes`, `yes`, `no`, luego vuelve a preguntar y termina con Q |
| `example3_neither.txt` | `S -> SS | a` (ambigua, recursiva izq.) | `Grammar is neither LL(1) nor SLR(1).` |

## Como ejecutar (una vez main.py este implementado)

```powershell
Get-Content .\tests\example1_slr.txt | python .\src\main.py
Get-Content .\tests\example2_ll.txt | python .\src\main.py
Get-Content .\tests\example3_neither.txt | python .\src\main.py
```

## Pendiente de agregar

- `custom_grammar.txt`: gramatica propia (no debe coincidir con las de este
  documento ni con las del libro) para el informe de los Items 1 y 2, con su
  FIRST/FOLLOW, tabla LL(1) o automata LR(0)+tabla SLR(1), y una cadena
  parseada paso a paso.
- `sdd_tests.txt`: al menos 5 cadenas para el Item 3 (ver `src/sdd.py` una
  vez tengan su propia gramatica/SDD), incluyendo:
  - la cadena mas corta del lenguaje,
  - una cadena que NO pertenezca al lenguaje,
  - una cadena con anidamiento o recursion profunda,
  - evidencia de deteccion de SDD circular (modificando temporalmente una
    regla, segun el Paso 6 del enunciado).
