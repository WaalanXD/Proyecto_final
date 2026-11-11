"""
slr1.py
-------
Construccion del automata LR(0) (CLOSURE, GOTO, coleccion canonica de
conjuntos de items) y de la tabla ACTION/GOTO del parser SLR(1), siguiendo
las Secciones 4.6.2 (items LR(0), CLOSURE, GOTO) y 4.6.4 (construccion de
la tabla SLR) del libro. El algoritmo de parsing es el de la Seccion 4.6.3.

Importante: se debe aumentar la gramatica con un nuevo simbolo inicial S'
y la produccion S' -> S (Seccion 4.6.2).
"""

from dataclasses import dataclass
from grammar import Grammar, Production, EPSILON, END_MARKER

AUGMENTED_START = "S'"


@dataclass(frozen=True)
class LR0Item:
    """Un item LR(0): una produccion con un punto (dot) en alguna posicion
    de su cuerpo. dot_position indica cuantos simbolos del cuerpo ya se
    reconocieron (0 <= dot_position <= len(body))."""
    production: Production
    dot_position: int

    def is_complete(self) -> bool:
        """True si el punto esta al final (item de reduccion)."""
        body = self.production.body
        if body == (EPSILON,):
            return True
        return self.dot_position == len(body)

    def symbol_after_dot(self) -> str | None:
        """Simbolo inmediatamente despues del punto, o None si el item esta
        completo."""
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
    """Devuelve una nueva gramatica aumentada con S' -> S.

    Por que se necesita: el algoritmo LR necesita un unico estado de
    aceptacion claro. Si usaramos S directamente, no podriamos distinguir
    "ya reconoci toda la cadena, aceptar" de "ya reconoci S, pero podria
    seguir usandolo dentro de otra produccion". Por eso se agrega un nuevo
    simbolo inicial S' con la unica produccion S' -> S: cuando el punto
    llega al final de esa produccion (item [S' -> S .]), sabemos que la
    cadena completa fue reconocida.

    Construimos una copia nueva de la gramatica (no modificamos la
    original, que se sigue usando para FIRST/FOLLOW/LL(1)) y le agregamos
    esa produccion extra.
    """
    gramatica_aumentada = Grammar()
    gramatica_aumentada.nonterminals = set(grammar.nonterminals)
    gramatica_aumentada.nonterminals.add(AUGMENTED_START)
    gramatica_aumentada.terminals = set(grammar.terminals)
    gramatica_aumentada.start_symbol = AUGMENTED_START

    # La nueva produccion S' -> S va primero, para que sea facil encontrarla.
    gramatica_aumentada.add_production(AUGMENTED_START, (grammar.start_symbol,))
    for produccion in grammar.productions:
        gramatica_aumentada.add_production(produccion.head, produccion.body)

    return gramatica_aumentada


def closure(items: set[LR0Item], grammar: Grammar) -> set[LR0Item]:
    """CLOSURE(I) segun la Seccion 4.6.2:
        - Todo item de I esta en CLOSURE(I).
        - Si A -> alpha . B beta esta en CLOSURE(I) y B -> gamma es una
          produccion, agregar B -> . gamma a CLOSURE(I) (si no estaba).
        - Repetir hasta que no haya cambios.

    Intuicion: si el punto esta justo antes de un no terminal B, significa
    que "en este punto se espera reconocer algo derivado de B". Por eso
    agregamos, con el punto al inicio, todas las formas posibles de empezar
    a reconocer B (cada una de sus producciones).
    """
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
    """GOTO(I, X) segun la Seccion 4.6.2: CLOSURE del conjunto de items
    A -> alpha X . beta tales que A -> alpha . X beta esta en I.

    En otras palabras: de todos los items de I donde el simbolo siguiente
    al punto es X, avanzamos el punto una posicion (ya "reconocimos" X), y
    le aplicamos CLOSURE al resultado.
    """
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
    """Construye la coleccion canonica de conjuntos de items LR(0) y las
    transiciones GOTO entre estados (Seccion 4.6.2).

    Cada conjunto de items representa un "estado" del automata LR(0): un
    resumen de en que punto de que producciones podriamos estar, dado lo
    que ya se leyo de la entrada. Partimos del estado inicial (justo antes
    de empezar a reconocer S) y vamos descubriendo nuevos estados al
    "avanzar" con cada simbolo posible (GOTO), hasta que no aparecen
    estados nuevos.

    Pasos:
        1. Aumentar la gramatica (augment_grammar).
        2. I0 = CLOSURE({S' -> . S}).
        3. Mientras haya cambios: para cada estado Ii y cada simbolo X,
           calcular GOTO(Ii, X); si es no vacio y no esta ya en la
           coleccion, agregarlo.
        4. Registrar las transiciones (indice_estado, simbolo) -> indice_estado.

    Returns:
        (estados, transiciones)
    """
    gramatica_aumentada = augment_grammar(grammar)

    # La produccion S' -> S es siempre la primera que agregamos en augment_grammar.
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
    """Construye las tablas ACTION y GOTO del parser SLR(1) (Seccion 4.6.4):

        Para cada estado Ii:
            - Si [A -> alpha . a beta] esta en Ii y GOTO(Ii, a) = Ij (a terminal):
                ACTION[i, a] = shift j
            - Si [A -> alpha .] esta en Ii (A != S'):
                Para cada terminal a en FOLLOW(A): ACTION[i, a] = reduce A -> alpha
            - Si [S' -> S .] esta en Ii:
                ACTION[i, $] = accept
            - Si GOTO(Ii, A) = Ij (A no terminal): GOTO_TABLE[i, A] = j

        La gramatica es SLR(1) si y solo si ninguna celda de ACTION recibe
        mas de una accion (conflicto shift/reduce o reduce/reduce).

    Returns:
        (tablas, is_slr1)
        tablas: dict con claves 'action' y 'goto'.
            action: dict (estado, terminal_o_$) -> ('shift', estado) o
                    ('reduce', Production) o ('accept',)
            goto: dict (estado, no_terminal) -> estado
        is_slr1: True si no hay conflictos, False si no.
    """
    estados, transiciones = build_canonical_collection(grammar)

    tabla_action: dict[tuple[int, str], tuple] = {}
    tabla_goto: dict[tuple[int, str], int] = {}
    es_slr1 = True

    def agregar_accion(estado: int, simbolo: str, accion: tuple) -> None:
        nonlocal es_slr1
        clave = (estado, simbolo)
        if clave in tabla_action and tabla_action[clave] != accion:
            # Dos acciones distintas en la misma celda: conflicto
            # shift/reduce o reduce/reduce. La gramatica no es SLR(1).
            es_slr1 = False
            return
        tabla_action[clave] = accion

    for indice_estado, estado in enumerate(estados):
        for item in estado:
            simbolo_siguiente = item.symbol_after_dot()

            if simbolo_siguiente is not None and grammar.is_terminal(simbolo_siguiente):
                # [A -> alpha . a beta]: desplazar (shift) leyendo "a".
                destino = transiciones[(indice_estado, simbolo_siguiente)]
                agregar_accion(indice_estado, simbolo_siguiente, ("shift", destino))

            elif item.is_complete():
                if item.production.head == AUGMENTED_START:
                    # [S' -> S .]: la cadena completa fue reconocida.
                    agregar_accion(indice_estado, END_MARKER, ("accept",))
                else:
                    # [A -> alpha .]: reducir usando A -> alpha, para cada
                    # terminal que pueda seguir a A segun FOLLOW(A).
                    for terminal in follow_sets[item.production.head]:
                        agregar_accion(
                            indice_estado, terminal, ("reduce", item.production)
                        )

        # Transiciones GOTO sobre no terminales (para despues de reducir).
        for no_terminal in grammar.nonterminals:
            clave_transicion = (indice_estado, no_terminal)
            if clave_transicion in transiciones:
                tabla_goto[clave_transicion] = transiciones[clave_transicion]

    tablas = {"action": tabla_action, "goto": tabla_goto}
    return tablas, es_slr1


def parse_slr1(grammar: Grammar, tables: dict, input_string: str) -> bool:
    """Algoritmo de parsing LR (Seccion 4.6.3) usando las tablas ACTION/GOTO.

    Pasos (resumen):
        1. Pila de estados inicializada con el estado inicial (0).
        2. Puntero al primer simbolo de entrada (con '$' ya agregado al final).
        3. Repetir:
            - Sea s el estado en el tope y a el simbolo actual de entrada.
            - Si ACTION[s, a] = shift t: apilar t, avanzar el puntero.
            - Si ACTION[s, a] = reduce A -> beta: hacer pop de |beta| estados,
              sea s' el nuevo tope, apilar GOTO[s', A].
            - Si ACTION[s, a] = accept: aceptar.
            - Si no hay accion definida: rechazar (error).

    Returns:
        True si input_string pertenece al lenguaje de la gramatica, False si no.
    """
    tabla_action = tables["action"]
    tabla_goto = tables["goto"]

    entrada = list(input_string) + [END_MARKER]
    posicion_entrada = 0

    # La pila guarda estados (numeros), no simbolos. El estado inicial
    # siempre es el 0 (el primero construido por build_canonical_collection).
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
