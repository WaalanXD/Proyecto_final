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

    TODO: construir una copia de la gramatica original agregando la
    produccion AUGMENTED_START -> grammar.start_symbol, y usando
    AUGMENTED_START como nuevo simbolo inicial interno (solo para la
    construccion del automata; la gramatica original no se modifica para
    efectos de FIRST/FOLLOW/LL(1)).
    """
    raise NotImplementedError


def closure(items: set[LR0Item], grammar: Grammar) -> set[LR0Item]:
    """CLOSURE(I) segun la Seccion 4.6.2:
        - Todo item de I esta en CLOSURE(I).
        - Si A -> alpha . B beta esta en CLOSURE(I) y B -> gamma es una
          produccion, agregar B -> . gamma a CLOSURE(I) (si no estaba).
        - Repetir hasta que no haya cambios.

    TODO: implementar el algoritmo de punto fijo descrito arriba.
    """
    raise NotImplementedError


def goto(items: set[LR0Item], symbol: str, grammar: Grammar) -> set[LR0Item]:
    """GOTO(I, X) segun la Seccion 4.6.2: CLOSURE del conjunto de items
    A -> alpha X . beta tales que A -> alpha . X beta esta en I.

    TODO: implementar.
    """
    raise NotImplementedError


def build_canonical_collection(
    grammar: Grammar,
) -> tuple[list[frozenset[LR0Item]], dict[tuple[int, str], int]]:
    """Construye la coleccion canonica de conjuntos de items LR(0) y las
    transiciones GOTO entre estados (Seccion 4.6.2).

    TODO:
        1. Aumentar la gramatica (augment_grammar).
        2. I0 = CLOSURE({S' -> . S}).
        3. Mientras haya cambios: para cada estado Ii y cada simbolo X,
           calcular GOTO(Ii, X); si es no vacio y no esta ya en la
           coleccion, agregarlo.
        4. Registrar las transiciones (indice_estado, simbolo) -> indice_estado.

    Returns:
        (estados, transiciones)
    """
    raise NotImplementedError


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

    TODO: implementar el algoritmo descrito arriba, usando
    build_canonical_collection.

    Returns:
        (tablas, is_slr1)
        tablas: dict con, por ejemplo, claves 'action' y 'goto', o None si
                se prefiere no exponer tablas invalidas.
        is_slr1: True si no hay conflictos, False si no.
    """
    raise NotImplementedError


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

    TODO: implementar el algoritmo descrito arriba.

    Returns:
        True si input_string pertenece al lenguaje de la gramatica, False si no.
    """
    raise NotImplementedError
