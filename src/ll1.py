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
    una produccion (condicion dada al inicio de la Seccion 4.4.3). Es decir,
    el parser, viendo solo el no terminal actual A y el siguiente simbolo de
    entrada a, siempre sabe sin ambiguedad que produccion usar.

    Returns:
        (tabla, is_ll1)
        tabla: dict (no_terminal, terminal_o_$) -> Production. Si hay un
               conflicto en una celda, se deja la primera produccion
               encontrada (la tabla ya no es confiable, pero is_ll1 avisa
               de eso).
        is_ll1: True si la gramatica cumple la condicion LL(1), False si no.
    """
    tabla: dict[tuple[str, str], Production] = {}
    es_ll1 = True

    def agregar_a_tabla(no_terminal: str, terminal: str, produccion: Production) -> None:
        nonlocal es_ll1
        clave = (no_terminal, terminal)
        if clave in tabla and tabla[clave] != produccion:
            # Dos producciones distintas caben en la misma celda: conflicto.
            es_ll1 = False
            return
        tabla[clave] = produccion

    for produccion in grammar.productions:
        cabeza = produccion.head
        primero_del_cuerpo = first_of_string(produccion.body, first_sets)

        # Paso 1: un terminal a en FIRST(alpha) => M[A, a] = A -> alpha.
        for terminal in primero_del_cuerpo - {EPSILON}:
            agregar_a_tabla(cabeza, terminal, produccion)

        # Paso 2: si alpha puede desaparecer (epsilon en su FIRST), miramos
        # que puede venir despues de A (FOLLOW(A)) para esas celdas.
        if EPSILON in primero_del_cuerpo:
            for terminal in follow_sets[cabeza]:
                agregar_a_tabla(cabeza, terminal, produccion)

    return tabla, es_ll1


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

    Returns:
        True si input_string pertenece al lenguaje de la gramatica, False si no.
    """
    entrada = list(input_string) + [END_MARKER]
    posicion_entrada = 0

    # Usamos una lista de Python como pila: el final de la lista (pila[-1])
    # es el tope. Apilamos el simbolo inicial, con $ debajo de el.
    pila = [END_MARKER, grammar.start_symbol]

    while pila[-1] != END_MARKER:
        tope = pila[-1]
        simbolo_actual = entrada[posicion_entrada]

        if grammar.is_terminal(tope):
            # El tope es un terminal: debe coincidir exactamente con la
            # entrada actual para poder consumirla.
            if tope != simbolo_actual:
                return False
            pila.pop()
            posicion_entrada += 1
        else:
            # El tope es un no terminal: buscamos en la tabla que
            # produccion usar segun el simbolo actual de entrada.
            clave = (tope, simbolo_actual)
            if clave not in table:
                return False

            produccion = table[clave]
            pila.pop()
            if produccion.body != (EPSILON,):
                # Apilamos el cuerpo en orden inverso para que el primer
                # simbolo del cuerpo quede en el tope de la pila.
                for simbolo in reversed(produccion.body):
                    pila.append(simbolo)

    # Si llegamos aqui, la pila solo tiene $. Se acepta si la entrada
    # tambien esta exactamente en el marcador de fin.
    return entrada[posicion_entrada] == END_MARKER
