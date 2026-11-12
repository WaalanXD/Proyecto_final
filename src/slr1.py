from dataclasses import dataclass
from grammar import Grammar, Production, EPSILON, END_MARKER

AUGMENTED_START = "S'"


@dataclass(frozen=True)
class LR0Item:
    production: Production
    dot_position: int

    def is_complete(self) -> bool:
     
        body = self.production.body
        if body == (EPSILON,):
            return True
        return self.dot_position == len(body)

    def symbol_after_dot(self) -> str | None:
        body = self.production.body
        if body == (EPSILON,) or self.dot_position >= len(body):
            return None
        return body[self.dot_position]

    def __str__(self) -> str:
        body = self.production.body
        if body == (EPSILON,):
            return f"{self.production.head} -> ."
        before = "".join(body[: self.dot_position])
        after = "".join(body[self.dot_position :])
        return f"{self.production.head} -> {before}.{after}"


def augment_grammar(grammar: Grammar) -> Grammar:
    gramatica_aumentada = Grammar()
    gramatica_aumentada.nonterminals = set(grammar.nonterminals)
    gramatica_aumentada.nonterminals.add(AUGMENTED_START)
    gramatica_aumentada.terminals = set(grammar.terminals)
    gramatica_aumentada.start_symbol = AUGMENTED_START

    gramatica_aumentada.add_production(AUGMENTED_START, (grammar.start_symbol,))
    for produccion in grammar.productions:
        gramatica_aumentada.add_production(produccion.head, produccion.body)

    return gramatica_aumentada


def closure(items: set[LR0Item], grammar: Grammar) -> set[LR0Item]:
    resultado = set(items)

    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False

        for item in list(resultado):
            simbolo = item.symbol_after_dot()
            if simbolo is None or not grammar.is_nonterminal(simbolo):
                continue

            for produccion in grammar.productions_by_head.get(simbolo, []):
                nuevo_item = LR0Item(produccion, 0)
                if nuevo_item not in resultado:
                    resultado.add(nuevo_item)
                    hubo_cambios = True

    return resultado


def goto(items: set[LR0Item], symbol: str, grammar: Grammar) -> set[LR0Item]:
    items_con_punto_avanzado = set()

    for item in items:
        if item.symbol_after_dot() == symbol:
            items_con_punto_avanzado.add(
                LR0Item(item.production, item.dot_position + 1)
            )

    return closure(items_con_punto_avanzado, grammar)


def build_canonical_collection(
    grammar: Grammar,
) -> tuple[list[frozenset[LR0Item]], dict[tuple[int, str], int]]:
    
    gramatica_aumentada = augment_grammar(grammar)

    produccion_inicial = gramatica_aumentada.productions[0]
    item_inicial = LR0Item(produccion_inicial, 0)
    estado_inicial = frozenset(closure({item_inicial}, gramatica_aumentada))

    estados: list[frozenset[LR0Item]] = [estado_inicial]
    transiciones: dict[tuple[int, str], int] = {}

    todos_los_simbolos = gramatica_aumentada.nonterminals | gramatica_aumentada.terminals

    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False

        for indice_estado, estado in enumerate(list(estados)):
            for simbolo in todos_los_simbolos:
                nuevo_estado = frozenset(goto(estado, simbolo, gramatica_aumentada))
                if not nuevo_estado:
                    continue

                if nuevo_estado not in estados:
                    estados.append(nuevo_estado)
                    hubo_cambios = True

                indice_destino = estados.index(nuevo_estado)
                transiciones[(indice_estado, simbolo)] = indice_destino

    return estados, transiciones


ACTION_SHIFT = "shift"
ACTION_REDUCE = "reduce"
ACTION_ACCEPT = "accept"


def build_slr_table(
    grammar: Grammar,
    follow_sets: dict[str, set[str]],
) -> tuple[dict | None, bool]:
    
    estados, transiciones = build_canonical_collection(grammar)

    tabla_action: dict[tuple[int, str], tuple] = {}
    tabla_goto: dict[tuple[int, str], int] = {}
    es_slr1 = True

    def agregar_accion(estado: int, simbolo: str, accion: tuple) -> None:
        nonlocal es_slr1
        clave = (estado, simbolo)
        if clave in tabla_action and tabla_action[clave] != accion:
            
            es_slr1 = False
            return
        tabla_action[clave] = accion

    for indice_estado, estado in enumerate(estados):
        for item in estado:
            simbolo_siguiente = item.symbol_after_dot()

            if simbolo_siguiente is not None and grammar.is_terminal(simbolo_siguiente):
                
                destino = transiciones[(indice_estado, simbolo_siguiente)]
                agregar_accion(indice_estado, simbolo_siguiente, ("shift", destino))

            elif item.is_complete():
                if item.production.head == AUGMENTED_START:
                   
                    agregar_accion(indice_estado, END_MARKER, ("accept",))
                else:
                  
                    for terminal in follow_sets[item.production.head]:
                        agregar_accion(
                            indice_estado, terminal, ("reduce", item.production)
                        )


        for no_terminal in grammar.nonterminals:
            clave_transicion = (indice_estado, no_terminal)
            if clave_transicion in transiciones:
                tabla_goto[clave_transicion] = transiciones[clave_transicion]

    tablas = {"action": tabla_action, "goto": tabla_goto}
    return tablas, es_slr1


def parse_slr1(grammar: Grammar, tables: dict, input_string: str) -> bool:
    
    tabla_action = tables["action"]
    tabla_goto = tables["goto"]

    entrada = list(input_string) + [END_MARKER]
    posicion_entrada = 0

    pila_de_estados = [0]

    while True:
        estado_actual = pila_de_estados[-1]
        simbolo_actual = entrada[posicion_entrada]

        clave = (estado_actual, simbolo_actual)
        if clave not in tabla_action:
            return False

        accion = tabla_action[clave]

        if accion[0] == "shift":
            _, estado_destino = accion
            pila_de_estados.append(estado_destino)
            posicion_entrada += 1

        elif accion[0] == "reduce":
            _, produccion = accion
            longitud_del_cuerpo = (
                0 if produccion.body == (EPSILON,) else len(produccion.body)
            )
            for _ in range(longitud_del_cuerpo):
                pila_de_estados.pop()

            estado_tras_reducir = pila_de_estados[-1]
            estado_destino = tabla_goto[(estado_tras_reducir, produccion.head)]
            pila_de_estados.append(estado_destino)

        elif accion[0] == "accept":
            return True
