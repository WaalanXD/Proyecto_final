"""
sdd.py
------
Representacion de la Definicion Dirigida por la Sintaxis (SDD) como DATOS,
no como codigo imperativo (enunciado, Item 3, Paso 5.1): el evaluador
generico (dependency_graph.py) no debe conocer nada especifico de esta SDD.
Para cambiar de SDD solo se debe modificar este archivo.

===========================================================================
IMPORTANTE: este archivo contiene la SDD de EJEMPLO del enunciado
(profundidad maxima de parentesis balanceados, Seccion 3, Paso 2) SOLO como
ilustracion del formato. El enunciado prohibe explicitamente entregar esa
SDD (regla G3). Deben reemplazar GRAMMAR_PRODUCTIONS y SDD_RULES por su
propia gramatica y su propia SDD antes de la entrega.
===========================================================================

Como modelar una regla semantica:
    Cada regla se representa con un objeto SemanticRule que indica:
        - target: el atributo que la regla define, como (simbolo, atributo)
          donde 'simbolo' se refiere a una posicion en el cuerpo de la
          produccion: 0 es el head (lado izquierdo), 1..k son los simbolos
          del cuerpo en orden (asi se distingue, por ejemplo, P1 de P2 en
          P -> ( P1 ) P2).
        - depends_on: lista de atributos (posicion, atributo) de los que
          depende el calculo.
        - compute: funcion que recibe los valores de depends_on (en el
          mismo orden) y devuelve el valor del atributo target.

Esto permite que dependency_graph.py, dado un nodo del arbol y su
produccion, instancie las reglas (Paso 5.3 del enunciado) sin conocer el
significado de ningun atributo.
"""

from dataclasses import dataclass
from typing import Callable
from grammar import Production


@dataclass(frozen=True)
class AttributeRef:
    """Referencia a un atributo de un simbolo dentro de una produccion.

    position: 0 para el head (lado izquierdo), 1..k para el i-esimo simbolo
              del cuerpo (1-indexado, en el orden en que aparece).
    name: nombre del atributo (p. ej. "val", "depth", "lexval").
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


# ---------------------------------------------------------------------
# EJEMPLO (reemplazar por su propia gramatica/SDD antes de entregar)
# Gramatica: S -> P ; P -> ( P ) P | e
# Atributos: P.d (heredado, profundidad); P.m / S.m (sintetizado, max profundidad)
# ---------------------------------------------------------------------

GRAMMAR_PRODUCTIONS: dict[str, list[tuple[str, ...]]] = {
    "S": [("P",)],
    "P": [("(", "P", ")", "P"), ("e",)],
}

# SDD_RULES: dict productions_key -> lista de SemanticRule
# La clave identifica la produccion de forma unica. Se recomienda usar
# (head, body) tal como aparece en Production, para evitar ambiguedad
# cuando un no terminal tiene varias alternativas.
SDD_RULES: dict[tuple[str, tuple[str, ...]], list[SemanticRule]] = {
    ("S", ("P",)): [
        # P.d = 0  (posicion 1 = P en el cuerpo)
        SemanticRule(AttributeRef(1, "d"), (), lambda: 0),
        # S.m = P.m  (posicion 0 = head S)
        SemanticRule(AttributeRef(0, "m"), (AttributeRef(1, "m"),), lambda m: m),
    ],
    ("P", ("(", "P", ")", "P")): [
        # P1.d = P.d + 1   (P1 es el primer P del cuerpo, posicion 2)
        SemanticRule(AttributeRef(2, "d"), (AttributeRef(0, "d"),), lambda d: d + 1),
        # P2.d = P.d       (P2 es el segundo P del cuerpo, posicion 4)
        SemanticRule(AttributeRef(4, "d"), (AttributeRef(0, "d"),), lambda d: d),
        # P.m = max(P1.m, P2.m)
        SemanticRule(
            AttributeRef(0, "m"),
            (AttributeRef(2, "m"), AttributeRef(4, "m")),
            lambda m1, m2: max(m1, m2),
        ),
    ],
    ("P", ("e",)): [
        # P.m = P.d
        SemanticRule(AttributeRef(0, "m"), (AttributeRef(0, "d"),), lambda d: d),
    ],
}

# Nombre del atributo principal del simbolo inicial, el que se debe
# imprimir como resultado final (Item 3, Paso 5, salida esperada).
MAIN_ATTRIBUTE = "m"
START_SYMBOL = "S"
