"""
first_follow.py
----------------
Calculo de los conjuntos FIRST(X) y FOLLOW(A) de una gramatica libre de
contexto, siguiendo el algoritmo de la Seccion 4.4.2 del libro
(Aho et al., Compilers: Principles, Techniques, and Tools, 2nd Edition).

Debe funcionar correctamente con gramaticas que tengan producciones con
epsilon (representado como EPSILON = 'e' en grammar.py).

Uso esperado (ver Seccion 2.2 del enunciado):
    Al ejecutar el programa con el argumento --sets, se debe imprimir, para
    cada no terminal en orden alfabetico:
        First(A) = {a, d}
        Follow(A) = {b, $}
    Los terminales dentro de las llaves van en orden ASCII, seguidos de 'e'
    (si epsilon pertenece al conjunto) y luego '$' (si pertenece).
"""

from grammar import Grammar, EPSILON, END_MARKER


def compute_first_sets(grammar: Grammar) -> dict[str, set[str]]:
    first_sets: dict[str, set[str]] = {}

    # Regla 1: FIRST(terminal) = {terminal}.
    for terminal in grammar.terminals:
        first_sets[terminal] = {terminal}

    # Los no terminales empiezan con FIRST vacio; se va llenando abajo.
    for no_terminal in grammar.nonterminals:
        first_sets[no_terminal] = set()

    hubo_cambios=True
    while hubo_cambios:
        hubo_cambios= False

        for produccion in grammar.productions:
            cabeza=produccion.head
            cuerpo=produccion.body

            if cuerpo == (EPSILON,):
                if EPSILON not in first_sets[cabeza]:
                    first_sets[cabeza].add(EPSILON)
                    hubo_cambios = True
                continue

            todos_producen_epsilon = True
            for simbolo in cuerpo:
                simbolos_sin_epsilon = first_sets[simbolo] - {EPSILON}
                if not simbolos_sin_epsilon.issubset(first_sets[cabeza]):
                    first_sets[cabeza] |= simbolos_sin_epsilon
                    hubo_cambios = True

                if EPSILON not in first_sets[simbolo]:
                    todos_producen_epsilon = False
                    break

            if todos_producen_epsilon and EPSILON not in first_sets[cabeza]:
                first_sets[cabeza].add(EPSILON)
                hubo_cambios = True

    return first_sets


def first_of_string(symbols: tuple[str, ...], first_sets: dict[str, set[str]]) -> set[str]:
    resultado: set[str]=set()

    if len(symbols) ==0 or symbols == (EPSILON,):
        resultado.add(EPSILON)
        return resultado

    todos_producen_epsilon=True
    for simbolo in symbols:
        resultado |= first_sets[simbolo] - {EPSILON}
        if EPSILON not in first_sets[simbolo]:
            todos_producen_epsilon = False
            break

    if todos_producen_epsilon:
        resultado.add(EPSILON)

    return resultado


def compute_follow_sets(
    grammar: Grammar, first_sets: dict[str, set[str]]
) -> dict[str, set[str]]:
    follow_sets: dict[str, set[str]] = {
        no_terminal: set() for no_terminal in grammar.nonterminals
    }

    follow_sets[grammar.start_symbol].add(END_MARKER)

    hubo_cambios=True
    while hubo_cambios:
        hubo_cambios =False

        for produccion in grammar.productions:
            cabeza =produccion.head
            cuerpo =produccion.body

            if cuerpo==(EPSILON,):
                continue

            for posicion, simbolo in enumerate(cuerpo):
                if not grammar.is_nonterminal(simbolo):
                    continue

                beta=cuerpo[posicion + 1:]
                primero_de_beta=first_of_string(beta, first_sets)

                sin_epsilon = primero_de_beta - {EPSILON}
                if not sin_epsilon.issubset(follow_sets[simbolo]):
                    follow_sets[simbolo] |= sin_epsilon
                    hubo_cambios = True

                if EPSILON in primero_de_beta:
                    if not follow_sets[cabeza].issubset(follow_sets[simbolo]):
                        follow_sets[simbolo] |= follow_sets[cabeza]
                        hubo_cambios = True

    return follow_sets


def format_set(symbols: set[str]) -> str:
    terminales_normales = sorted(symbols - {EPSILON, END_MARKER})

    simbolos_en_orden = list(terminales_normales)
    if EPSILON in symbols:
        simbolos_en_orden.append(EPSILON)
    if END_MARKER in symbols:
        simbolos_en_orden.append(END_MARKER)

    return "{" + ", ".join(simbolos_en_orden) + "}"


def print_sets(
    grammar: Grammar,
    first_sets: dict[str, set[str]],
    follow_sets: dict[str, set[str]],
) -> None:
    for no_terminal in sorted(grammar.nonterminals):
        print(f"First({no_terminal}) = {format_set(first_sets[no_terminal])}")
        print(f"Follow({no_terminal}) = {format_set(follow_sets[no_terminal])}")
