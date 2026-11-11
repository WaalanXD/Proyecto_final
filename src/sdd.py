"""
sdd.py
------
Representacion de la Definicion Dirigida por la Sintaxis (SDD) como DATOS,
no como codigo imperativo (enunciado, Item 3, Paso 5.1): el evaluador
generico (dependency_graph.py) no debe conocer nada especifico de esta SDD.
Para cambiar de SDD solo se debe modificar este archivo.

Como modelar una regla semantica:
    Cada regla se representa con un objeto SemanticRule que indica:
        - target: el atributo que la regla define, como (simbolo, atributo)
          donde 'simbolo' se refiere a una posicion en el cuerpo de la
          produccion: 0 es el head (lado izquierdo), 1..k son los simbolos
          del cuerpo en orden (asi se distingue, por ejemplo, L1 de L2 en
          L -> T L).
        - depends_on: lista de atributos (posicion, atributo) de los que
          depende el calculo.
        - compute: funcion que recibe los valores de depends_on (en el
          mismo orden) y devuelve el valor del atributo target.

Esto permite que dependency_graph.py, dado un nodo del arbol y su
produccion, instancie las reglas (Paso 5.3 del enunciado) sin conocer el
significado de ningun atributo.

===========================================================================
SDD PROPIA (Item 3): "cinta de incrementos/decrementos".
===========================================================================

Gramatica (ver docs/sdd_design.md, Paso 1, para la justificacion de que
cumple G1-G3 del enunciado y de que es SLR(1)):

    S -> L
    L -> TL | e
    T -> +N | -N
    N -> dN | d

El lenguaje son listas (posiblemente vacias) de "operaciones" +N o -N,
donde N es una secuencia de uno o mas caracteres 'd' cuya longitud
representa la magnitud de la operacion (p. ej. 'ddd' vale 3). La cadena
'+dd-d' representa "sumar 2, luego restar 1".

Atributos (ver docs/sdd_design.md, Paso 2, para la tabla completa y la
clasificacion L-attributed):
    N.val  (sintetizado) cantidad de 'd' en N (su magnitud, entero >= 1).
    T.val  (sintetizado) valor con signo de la operacion (+N.val o -N.val).
    L.acc  (heredado)    acumulador ANTES de procesar esta lista.
    L.val  (sintetizado) acumulador DESPUES de procesar esta lista.
    S.val  (sintetizado) resultado final (acumulador total de la cadena).
"""

from dataclasses import dataclass
from typing import Callable
from grammar import Production


@dataclass(frozen=True)
class AttributeRef:
    """Referencia a un atributo de un simbolo dentro de una produccion.

    position: 0 para el head (lado izquierdo), 1..k para el i-esimo simbolo
              del cuerpo (1-indexado, en el orden en que aparece).
    name: nombre del atributo (p. ej. "val", "acc", "lexval").
    """
    position: int
    name: str


@dataclass
class SemanticRule:
    """Una regla semantica de una produccion: define `target` calculandolo
    a partir de los atributos listados en `depends_on`, en ese orden."""
    target: AttributeRef
    depends_on: tuple[AttributeRef, ...]
    compute: Callable[..., object]


GRAMMAR_PRODUCTIONS: dict[str, list[tuple[str, ...]]] = {
    "S": [("L",)],
    "L": [("T", "L"), ("e",)],
    "T": [("+", "N"), ("-", "N")],
    "N": [("d", "N"), ("d",)],
}

# SDD_RULES: dict productions_key -> lista de SemanticRule
# La clave identifica la produccion de forma unica: (head, body), tal como
# aparece en Production, para evitar ambiguedad cuando un no terminal tiene
# varias alternativas (p. ej. distinguir L -> T L de L -> e).
SDD_RULES: dict[tuple[str, tuple[str, ...]], list[SemanticRule]] = {
    # S -> L
    #   L.acc = 0            (posicion 1: L es el unico simbolo del cuerpo)
    #   S.val = L.val        (posicion 0: head S)
    ("S", ("L",)): [
        SemanticRule(AttributeRef(1, "acc"), (), lambda: 0),
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(1, "val"),), lambda v: v),
    ],
    # L -> T L   (L1 es el head/posicion 0; T es posicion 1; L2 es posicion 2)
    #   L2.acc = L1.acc + T.val   (heredado: fluye hacia la cola de la lista)
    #   L1.val = L2.val           (sintetizado: se propaga desde la cola)
    ("L", ("T", "L")): [
        SemanticRule(
            AttributeRef(2, "acc"),
            (AttributeRef(0, "acc"), AttributeRef(1, "val")),
            lambda acc, t_val: acc + t_val,
        ),
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(2, "val"),), lambda v: v),
    ],
    # L -> e
    #   L.val = L.acc   (caso base: no quedan operaciones, se devuelve el
    #                    acumulador recibido tal cual).
    ("L", ("e",)): [
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(0, "acc"),), lambda acc: acc),
    ],
    # T -> + N
    #   T.val = N.val   (suma: se conserva el signo positivo).
    ("T", ("+", "N")): [
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(2, "val"),), lambda n: n),
    ],
    # T -> - N
    #   T.val = -N.val  (resta: se invierte el signo).
    ("T", ("-", "N")): [
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(2, "val"),), lambda n: -n),
    ],
    # N -> d N   (N1 es el head/posicion 0; N2 es posicion 2)
    #   N1.val = 1 + N2.val
    ("N", ("d", "N")): [
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(2, "val"),), lambda n: 1 + n),
    ],
    # N -> d   (caso base: una sola 'd' vale 1).
    ("N", ("d",)): [
        SemanticRule(AttributeRef(0, "val"), (), lambda: 1),
    ],
}

# Nombre del atributo principal del simbolo inicial, el que se debe
# imprimir como resultado final (Item 3, Paso 5, salida esperada).
MAIN_ATTRIBUTE = "val"
START_SYMBOL = "S"
