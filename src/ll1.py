"""
ll1.py
------
Construccion de la tabla de parsing predictivo LL(1) y el parser dirigido
por tabla (no recursivo) de la Seccion 4.4.4, usando el algoritmo de
construccion de la tabla de la Seccion 4.4.3.

Importante (regla del enunciado): NO transformar la gramatica de entrada
(no eliminar recursion izquierda, no factorizar) antes de construir la tabla
o de comprobar si es LL(1). Si la gramatica no es LL(1) tal cual se dio,
el resultado debe reflejar eso.
"""

from grammar import Grammar, Production, EPSILON, END_MARKER
from first_follow import first_of_string


class LL1ConflictError(Exception):
    """Se lanza (o se usa internamente) cuando se detecta una celda con mas
    de una entrada en la tabla, es decir, la gramatica no es LL(1)."""


def build_ll1_table(
    grammar: Grammar,
    first_sets: dict[str, set[str]],
    follow_sets: dict[str, set[str]],
) -> tuple[dict[tuple[str, str], Production] | None, bool]:
    """Construye la tabla de parsing M[A, a] siguiendo el algoritmo de la
    Seccion 4.4.3:

        Para cada produccion A -> alpha:
            1. Para cada terminal a en FIRST(alpha), agregar A -> alpha a M[A, a].
            2. Si epsilon esta en FIRST(alpha):
                - Para cada terminal b en FOLLOW(A), agregar A -> alpha a M[A, b].
                - Si $ esta en FOLLOW(A), agregar A -> alpha a M[A, $].

    La gramatica es LL(1) si y solo si ninguna celda M[A, a] recibe mas de
    una produccion (condicion dada al inicio de la Seccion 4.4.3).

    TODO: implementar el algoritmo. Al detectar que una celda ya tiene una
    produccion distinta, marcar is_ll1 = False (pero se puede seguir
    construyendo para reportar conflictos si se desea).

    Returns:
        (tabla, is_ll1)
        tabla: dict (no_terminal, terminal_o_$) -> Production (puede tener
               solo la primera entrada encontrada en caso de conflicto, o
               None si se prefiere no exponer una tabla invalida).
        is_ll1: True si la gramatica cumple la condicion LL(1), False si no.
    """
    raise NotImplementedError


def parse_ll1(
    grammar: Grammar,
    table: dict[tuple[str, str], Production],
    input_string: str,
) -> bool:
    """Parser predictivo no recursivo dirigido por tabla (Seccion 4.4.4,
    algoritmo con pila explicita).

    Pasos (resumen del algoritmo del libro):
        1. Pila inicial: [$, S] (S en el tope).
        2. Puntero al primer simbolo de la entrada (la entrada ya debe tener
           el '$' agregado al final).
        3. Mientras el tope de la pila no sea $:
            - Si el tope X es terminal o $: si coincide con el simbolo actual
              de entrada, hacer pop y avanzar el puntero; si no, error.
            - Si el tope X es no terminal: consultar M[X, a] donde a es el
              simbolo actual de entrada.
                - Si hay produccion X -> Y1 Y2 ... Yk, hacer pop de X y
                  apilar Yk, ..., Y2, Y1 (Y1 queda en el tope). Si la
                  alternativa es epsilon, no se apila nada.
                - Si no hay entrada en la tabla, error (cadena rechazada).
        4. Aceptar si se llega a la pila vacia ($ en la pila y $ en la
           entrada) sin errores.

    TODO: implementar el algoritmo descrito arriba.

    Returns:
        True si input_string pertenece al lenguaje de la gramatica, False si no.
    """
    raise NotImplementedError
