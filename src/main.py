"""
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
import sdd

PROMPT = "Select a parser (T: for LL(1), B: for SLR(1), Q: quit):"


def read_strings_until_blank() -> list[str]:
    lineas = []
    while True:
        linea = sys.stdin.readline()
        if linea == "" or linea.strip() == "":
            break
        lineas.append(linea.strip())
    return lineas


def normalize_input_string(line: str) -> str:
    if line == EPSILON:
        return ""
    return line


def responder_cadenas_ll1(grammar, ll1_table) -> None:
    for linea in read_strings_until_blank():
        cadena = normalize_input_string(linea)
        if parse_ll1(grammar, ll1_table, cadena):
            print("yes")
        else:
            print("no")


def responder_cadenas_slr1(grammar, slr_tables) -> None:
    for linea in read_strings_until_blank():
        cadena = normalize_input_string(linea)
        if parse_slr1(grammar, slr_tables, cadena):
            print("yes")
        else:
            print("no")


def run_items_1_and_2(argv: list[str]) -> None:
    grammar = read_grammar(sys.stdin)

    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)

    if "--sets" in argv:
        print_sets(grammar, first_sets, follow_sets)

    ll1_table, is_ll1 = build_ll1_table(grammar, first_sets, follow_sets)
    slr_tables, is_slr1 = build_slr_table(grammar, follow_sets)

    if is_ll1 and is_slr1:
        while True:
            print(PROMPT)
            linea_leida = sys.stdin.readline()

            if linea_leida == "":
                break

            opcion = linea_leida.strip()
            if opcion == "Q":
                break
            elif opcion == "T":
                responder_cadenas_ll1(grammar, ll1_table)
            elif opcion == "B":
                responder_cadenas_slr1(grammar, slr_tables)

    elif is_ll1:
        # Caso 2: solo LL(1).
        print("Grammar is LL(1).")
        responder_cadenas_ll1(grammar, ll1_table)

    elif is_slr1:
        # Caso 3: solo SLR(1).
        print("Grammar is SLR(1).")
        responder_cadenas_slr1(grammar, slr_tables)

    else:
        # Caso 4: ninguna de las dos.
        print("Grammar is neither LL(1) nor SLR(1).")


def run_item_3() -> None:
    grammar = read_grammar(sys.stdin)

    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)

    ll1_table, is_ll1 = build_ll1_table(grammar, first_sets, follow_sets)
    slr_tables, is_slr1 = build_slr_table(grammar, follow_sets)

    for linea in read_strings_until_blank():
        cadena = normalize_input_string(linea)

        if is_ll1:
            raiz = build_parse_tree_ll1(grammar, ll1_table, cadena)
        else:
            raiz = build_parse_tree_slr1(grammar, slr_tables, cadena)

        if raiz is None:
            print("no")
            continue

        try:
            orden_de_evaluacion = evaluate_sdd(raiz)
        except CircularSDDError:
            print("La SDD es circular para esta cadena.")
            continue

        print(raiz.pretty_print())
        print("Orden de evaluacion:", orden_de_evaluacion)
        print(sdd.MAIN_ATTRIBUTE, "=", raiz.attributes[sdd.MAIN_ATTRIBUTE])


def main() -> None:
    argv = sys.argv[1:]
    if "--sdd" in argv:
        run_item_3()
    else:
        run_items_1_and_2(argv)


if __name__ == "__main__":
    main()
