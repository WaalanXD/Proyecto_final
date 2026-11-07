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
    """Calcula FIRST(X) para cada simbolo (terminal y no terminal) de la gramatica.

    Reglas (Section 4.4.2):
        1. Si X es terminal, FIRST(X) = {X}.
        2. Si X -> epsilon es una produccion, agregar epsilon a FIRST(X).
        3. Si X es no terminal y X -> Y1 Y2 ... Yk es una produccion:
            - Agregar a FIRST(X) todo lo que no sea epsilon de FIRST(Y1).
            - Si epsilon esta en FIRST(Y1), agregar lo que no sea epsilon de
              FIRST(Y2), y asi sucesivamente.
            - Si epsilon esta en FIRST(Y1)...FIRST(Yk), agregar epsilon a FIRST(X).
        Iterar hasta que no haya cambios (punto fijo).

    TODO: implementar el algoritmo descrito arriba.

    Returns:
        dict que mapea cada simbolo (terminal o no terminal) a su conjunto FIRST.
    """
    raise NotImplementedError


def first_of_string(symbols: tuple[str, ...], first_sets: dict[str, set[str]]) -> set[str]:
    """Extiende FIRST a una cadena de simbolos X1 X2 ... Xn (necesario para
    construir la tabla LL(1) y los lookaheads del SLR(1)).

    Reglas:
        - FIRST(X1 X2 ... Xn) agrega todo lo que no sea epsilon de FIRST(X1).
        - Si epsilon esta en FIRST(X1), continuar con FIRST(X2), etc.
        - Si epsilon esta en FIRST(Xi) para todo i, entonces epsilon esta en
          FIRST(X1...Xn).

    TODO: implementar.
    """
    raise NotImplementedError


def compute_follow_sets(
    grammar: Grammar, first_sets: dict[str, set[str]]
) -> dict[str, set[str]]:
    """Calcula FOLLOW(A) para cada no terminal A, siguiendo las reglas de la
    Seccion 4.4.2:
        1. Agregar '$' a FOLLOW(S), donde S es el simbolo inicial.
        2. Si A -> alpha B beta es una produccion:
            - Todo lo que no sea epsilon de FIRST(beta) se agrega a FOLLOW(B).
        3. Si A -> alpha B es una produccion, o A -> alpha B beta donde
           epsilon esta en FIRST(beta):
            - Todo lo de FOLLOW(A) se agrega a FOLLOW(B).
        Iterar hasta que no haya cambios (punto fijo).

    TODO: implementar el algoritmo descrito arriba.

    Returns:
        dict que mapea cada no terminal a su conjunto FOLLOW.
    """
    raise NotImplementedError


def format_set(symbols: set[str]) -> str:
    """Formatea un conjunto de simbolos para impresion segun la Seccion 2.2:
    terminales en orden ASCII, luego 'e' si esta presente, luego '$' si esta
    presente. Ejemplo: {a, d} o {b, $}.

    TODO: implementar el ordenamiento y formato exacto "a, b, c".
    """
    raise NotImplementedError


def print_sets(
    grammar: Grammar,
    first_sets: dict[str, set[str]],
    follow_sets: dict[str, set[str]],
) -> None:
    """Imprime First(A) y Follow(A) para cada no terminal A, en orden
    alfabetico de no terminales, con el formato exacto exigido por el
    enunciado (argumento --sets).

    TODO: implementar la impresion usando format_set.
    """
    raise NotImplementedError
