from grammar import Grammar, Production, EPSILON, END_MARKER
from first_follow import first_of_string


class LL1ConflictError(Exception):
def build_ll1_table(
    grammar: Grammar,
    first_sets: dict[str, set[str]],
    follow_sets: dict[str, set[str]],
) -> tuple[dict[tuple[str, str], Production] | None, bool]:
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

        for terminal in primero_del_cuerpo - {EPSILON}:
            agregar_a_tabla(cabeza, terminal, produccion)

        if EPSILON in primero_del_cuerpo:
            for terminal in follow_sets[cabeza]:
                agregar_a_tabla(cabeza, terminal, produccion)

    return tabla, es_ll1


def parse_ll1(
    grammar: Grammar,
    table: dict[tuple[str, str], Production],
    input_string: str,
) -> bool:
    entrada = list(input_string) + [END_MARKER]
    posicion_entrada = 0

    pila = [END_MARKER, grammar.start_symbol]

    while pila[-1] != END_MARKER:
        tope = pila[-1]
        simbolo_actual = entrada[posicion_entrada]

        if grammar.is_terminal(tope):
            if tope != simbolo_actual:
                return False
            pila.pop()
            posicion_entrada += 1
        else:
            clave = (tope, simbolo_actual)
            if clave not in table:
                return False

            produccion = table[clave]
            pila.pop()
            if produccion.body != (EPSILON,):
                for simbolo in reversed(produccion.body):
                    pila.append(simbolo)

    return entrada[posicion_entrada] == END_MARKER
