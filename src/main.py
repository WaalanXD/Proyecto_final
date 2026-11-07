"""
main.py
-------
Punto de entrada del programa. Implementa el flujo de entrada/salida
descrito en las Secciones 2.2 y 3 del enunciado:

    1. Lee la gramatica (Seccion 2.2.1).
    2. Si se invoco con --sets, imprime First(A)/Follow(A) por cada no
       terminal en orden alfabetico (Seccion 2.2, parrafo del Item 1).
    3. Calcula si la gramatica es LL(1) y si es SLR(1).
    4. Segun el caso (Seccion 2.2.2):
        a) Ambas: preguntar "Select a parser (T: for LL(1), B: for SLR(1), Q: quit):"
           en bucle hasta Q.
        b) Solo LL(1): imprimir "Grammar is LL(1)." y parsear con LL(1).
        c) Solo SLR(1): imprimir "Grammar is SLR(1)." y parsear con SLR(1).
        d) Ninguna: imprimir "Grammar is neither LL(1) nor SLR(1)." y terminar.
    5. En los casos a/b/c, leer cadenas una por linea hasta linea vacia,
       imprimiendo "yes"/"no" por cada una (la cadena vacia se da como "e").

Uso:
    python main.py                 # modo normal (parsers LL1/SLR1, Items 1-2)
    python main.py --sets          # igual, pero imprime antes First/Follow
    python main.py --sdd           # modo Item 3: parsea y evalua la SDD de sdd.py
"""

import sys

from grammar import read_grammar, EPSILON, END_MARKER
from first_follow import compute_first_sets, compute_follow_sets, print_sets
from ll1 import build_ll1_table, parse_ll1
from slr1 import build_slr_table, parse_slr1
from parse_tree import build_parse_tree_ll1, build_parse_tree_slr1
from dependency_graph import evaluate_sdd, CircularSDDError

PROMPT = "Select a parser (T: for LL(1), B: for SLR(1), Q: quit):"


def read_strings_until_blank() -> list[str]:
    """Lee lineas de entrada hasta encontrar una linea vacia (sin incluirla).
    Segun el enunciado, la cadena vacia se escribe como una linea con solo 'e'.

    TODO: implementar la lectura desde sys.stdin.
    """
    raise NotImplementedError


def normalize_input_string(line: str) -> str:
    """Convierte una linea leida en la cadena real a parsear: si la linea
    es exactamente 'e', la cadena real es la cadena vacia; si no, la linea
    misma es la cadena (sin el caracter de nueva linea).

    TODO: implementar.
    """
    raise NotImplementedError


def run_items_1_and_2(argv: list[str]) -> None:
    """Flujo principal para los Items 1 y 2 (ver Secciones 2.2 y 5 del
    enunciado, incluye el manejo de --sets y los 4 casos de 2.2.2).

    TODO:
        1. grammar = read_grammar(sys.stdin)
        2. first_sets = compute_first_sets(grammar)
           follow_sets = compute_follow_sets(grammar, first_sets)
        3. Si "--sets" in argv: print_sets(grammar, first_sets, follow_sets)
        4. ll1_table, is_ll1 = build_ll1_table(grammar, first_sets, follow_sets)
        5. slr_tables, is_slr1 = build_slr_table(grammar, follow_sets)
        6. Segun (is_ll1, is_slr1), seguir el caso correspondiente de la
           Seccion 2.2.2 (ver docstring del modulo).
    """
    raise NotImplementedError


def run_item_3() -> None:
    """Flujo principal para el Item 3 (SDD). Ver Seccion 3, Paso 5.5 del
    enunciado (salida esperada).

    TODO:
        1. grammar = read_grammar(sys.stdin)
        2. Calcular first/follow, tabla LL(1) o SLR(1) (la gramatica de la
           SDD debe ser LL(1) o SLR(1) por la regla G1).
        3. Leer cadenas hasta linea vacia. Para cada cadena:
            a. Construir el arbol de derivacion (parse_tree.build_parse_tree_*).
            b. Si la cadena no pertenece al lenguaje: imprimir "no".
            c. Si pertenece:
                - evaluation_order = evaluate_sdd(root)  (puede lanzar
                  CircularSDDError si la SDD resulta circular para ese arbol)
                - Imprimir el arbol anotado (root.pretty_print()).
                - Imprimir el orden de evaluacion.
                - Imprimir el valor del atributo principal del simbolo inicial
                  (sdd.MAIN_ATTRIBUTE en root.attributes).
            d. Si evaluate_sdd lanza CircularSDDError: reportar que la SDD
               es circular para esa cadena y continuar con la siguiente.
    """
    raise NotImplementedError


def main() -> None:
    argv = sys.argv[1:]
    if "--sdd" in argv:
        run_item_3()
    else:
        run_items_1_and_2(argv)


if __name__ == "__main__":
    main()
