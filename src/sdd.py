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

SDD_RULES: dict[tuple[str, tuple[str, ...]], list[SemanticRule]] = {
    ("S", ("L",)): [
        SemanticRule(AttributeRef(1, "acc"), (), lambda: 0),
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(1, "val"),), lambda v: v),
    ],
    ("L", ("T", "L")): [
        SemanticRule(
            AttributeRef(2, "acc"),
            (AttributeRef(0, "acc"), AttributeRef(1, "val")),
            lambda acc, t_val: acc + t_val,
        ),
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(2, "val"),), lambda v: v),
    ],
    
    ("L", ("e",)): [
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(0, "acc"),), lambda acc: acc),
    ],
    
    ("T", ("+", "N")): [
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(2, "val"),), lambda n: n),
    ],
    
    ("T", ("-", "N")): [
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(2, "val"),), lambda n: -n),
    ],
    
    ("N", ("d", "N")): [
        SemanticRule(AttributeRef(0, "val"), (AttributeRef(2, "val"),), lambda n: 1 + n),
    ],

    ("N", ("d",)): [
        SemanticRule(AttributeRef(0, "val"), (), lambda: 1),
    ],
}

MAIN_ATTRIBUTE = "val"
START_SYMBOL = "S"
