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

    Idea de la iteracion a punto fijo: como los no terminales pueden
    depender unos de otros (incluso de si mismos, por recursion), no
    podemos calcular FIRST de una sola pasada. En vez de eso, repetimos el
    proceso de "agregar lo que falte" una y otra vez hasta que en una
    vuelta completa no se agregue nada nuevo: ese es el punto fijo.

    Returns:
        dict que mapea cada simbolo (terminal o no terminal) a su conjunto FIRST.
    """
    first_sets: dict[str, set[str]] = {}

    # Regla 1: FIRST(terminal) = {terminal}.
    for terminal in grammar.terminals:
        first_sets[terminal] = {terminal}

    # Los no terminales empiezan con FIRST vacio; se va llenando abajo.
    for no_terminal in grammar.nonterminals:
        first_sets[no_terminal] = set()

    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False

        for produccion in grammar.productions:
            cabeza = produccion.head
            cuerpo = produccion.body

            # Regla 2: A -> epsilon agrega epsilon a FIRST(A).
            if cuerpo == (EPSILON,):
                if EPSILON not in first_sets[cabeza]:
                    first_sets[cabeza].add(EPSILON)
                    hubo_cambios = True
                continue

            # Regla 3: recorremos Y1, Y2, ... del cuerpo mientras cada uno
            # pueda producir epsilon (es decir, mientras "se pueda saltar").
            todos_producen_epsilon = True
            for simbolo in cuerpo:
                simbolos_sin_epsilon = first_sets[simbolo] - {EPSILON}
                if not simbolos_sin_epsilon.issubset(first_sets[cabeza]):
                    first_sets[cabeza] |= simbolos_sin_epsilon
                    hubo_cambios = True

                if EPSILON not in first_sets[simbolo]:
                    todos_producen_epsilon = False
                    break

            # Si Y1...Yk pueden producir epsilon todos, entonces A tambien.
            if todos_producen_epsilon and EPSILON not in first_sets[cabeza]:
                first_sets[cabeza].add(EPSILON)
                hubo_cambios = True

    return first_sets


def first_of_string(symbols: tuple[str, ...], first_sets: dict[str, set[str]]) -> set[str]:
    """Extiende FIRST a una cadena de simbolos X1 X2 ... Xn (necesario para
    construir la tabla LL(1) y los lookaheads del SLR(1)).

    Reglas:
        - FIRST(X1 X2 ... Xn) agrega todo lo que no sea epsilon de FIRST(X1).
        - Si epsilon esta en FIRST(X1), continuar con FIRST(X2), etc.
        - Si epsilon esta en FIRST(Xi) para todo i, entonces epsilon esta en
          FIRST(X1...Xn).

    Es el mismo razonamiento de la regla 3 de compute_first_sets, pero
    aplicado directamente a una cadena ya dada (el cuerpo de una
    produccion), no a toda la gramatica.
    """
    resultado: set[str] = set()

    # Una cadena vacia o la alternativa epsilon producen solo epsilon.
    if len(symbols) == 0 or symbols == (EPSILON,):
        resultado.add(EPSILON)
        return resultado

    todos_producen_epsilon = True
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
    """Calcula FOLLOW(A) para cada no terminal A, siguiendo las reglas de la
    Seccion 4.4.2:
        1. Agregar '$' a FOLLOW(S), donde S es el simbolo inicial.
        2. Si A -> alpha B beta es una produccion:
            - Todo lo que no sea epsilon de FIRST(beta) se agrega a FOLLOW(B).
        3. Si A -> alpha B es una produccion, o A -> alpha B beta donde
           epsilon esta en FIRST(beta):
            - Todo lo de FOLLOW(A) se agrega a FOLLOW(B).
        Iterar hasta que no haya cambios (punto fijo).

    FOLLOW(B) responde a la pregunta: "que terminal puede aparecer
    inmediatamente despues de B en alguna derivacion valida". Por eso
    miramos, para cada no terminal B que aparece en el cuerpo de una
    produccion, que hay despues de el (beta) y, si beta puede desaparecer
    (producir epsilon) o B esta al final, lo que venga despues de la
    cabeza A tambien puede venir despues de B.
    """
    follow_sets: dict[str, set[str]] = {
        no_terminal: set() for no_terminal in grammar.nonterminals
    }

    # Regla 1: $ esta en FOLLOW del simbolo inicial.
    follow_sets[grammar.start_symbol].add(END_MARKER)

    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False

        for produccion in grammar.productions:
            cabeza = produccion.head
            cuerpo = produccion.body

            if cuerpo == (EPSILON,):
                continue

            # Recorremos cada no terminal B del cuerpo, junto con lo que
            # viene despues de el (beta = cuerpo[posicion + 1:]).
            for posicion, simbolo in enumerate(cuerpo):
                if not grammar.is_nonterminal(simbolo):
                    continue

                beta = cuerpo[posicion + 1:]
                primero_de_beta = first_of_string(beta, first_sets)

                # Regla 2: lo que no sea epsilon de FIRST(beta) va a FOLLOW(B).
                sin_epsilon = primero_de_beta - {EPSILON}
                if not sin_epsilon.issubset(follow_sets[simbolo]):
                    follow_sets[simbolo] |= sin_epsilon
                    hubo_cambios = True

                # Regla 3: si beta puede desaparecer (o no hay beta, B esta
                # al final), entonces FOLLOW(A) tambien es FOLLOW(B).
                if EPSILON in primero_de_beta:
                    if not follow_sets[cabeza].issubset(follow_sets[simbolo]):
                        follow_sets[simbolo] |= follow_sets[cabeza]
                        hubo_cambios = True

    return follow_sets


def format_set(symbols: set[str]) -> str:
    """Formatea un conjunto de simbolos para impresion segun la Seccion 2.2:
    terminales en orden ASCII, luego 'e' si esta presente, luego '$' si esta
    presente. Ejemplo: {a, d} o {b, $}.
    """
    # Separamos 'e' y '$' porque van al final en un orden fijo; el resto
    # (los terminales normales) se ordena alfabeticamente (orden ASCII).
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
    """Imprime First(A) y Follow(A) para cada no terminal A, en orden
    alfabetico de no terminales, con el formato exacto exigido por el
    enunciado (argumento --sets).
    """
    # Para cada no terminal (en orden alfabetico) se imprimen sus dos
    # lineas: primero First(A), luego Follow(A).
    for no_terminal in sorted(grammar.nonterminals):
        print(f"First({no_terminal}) = {format_set(first_sets[no_terminal])}")
        print(f"Follow({no_terminal}) = {format_set(follow_sets[no_terminal])}")
