"""
grammar.py
----------
Representacion de una gramatica libre de contexto (CFG) y lectura de la
entrada en el formato descrito en la Seccion 2.2.1 del enunciado.

Convenciones (Seccion 2.2):
    - El simbolo inicial siempre es 'S'.
    - Los no terminales son letras mayusculas.
    - Los terminales son cualquier simbolo que no sea mayuscula (nunca espacio).
    - La cadena vacia (epsilon) se representa con la letra 'e'.
    - '$' es el marcador de fin de cadena, nunca aparece en la gramatica de entrada.

Formato de entrada:
    n
    <no_terminal> -> <alt_1> <alt_2> ... <alt_k>

    Ejemplo:
        3
        S -> AB
        A -> aA d
        B -> bBc e
"""

from dataclasses import dataclass, field

EPSILON = "e"
END_MARKER = "$"


@dataclass(frozen=True)
class Production:
    """Una produccion A -> alpha, donde alpha es una tupla de simbolos.

    alpha == (EPSILON,) representa la alternativa vacia (A -> epsilon).
    """
    head: str
    body: tuple[str, ...]

    def __str__(self) -> str:
        body_str = "".join(self.body) if self.body != (EPSILON,) else EPSILON
        return f"{self.head} -> {body_str}"


class Grammar:
    """Representa una gramatica libre de contexto.

    Atributos:
        nonterminals: conjunto de no terminales (letras mayusculas).
        terminals: conjunto de terminales.
        productions: lista de Production en el orden leido de la entrada.
        productions_by_head: dict no_terminal -> lista de Production.
        start_symbol: siempre 'S' segun el enunciado.
    """

    def __init__(self) -> None:
        self.nonterminals: set[str] = set()
        self.terminals: set[str] = set()
        self.productions: list[Production] = []
        self.productions_by_head: dict[str, list[Production]] = {}
        self.start_symbol: str = "S"

    def add_production(self, head: str, body: tuple[str, ...]) -> None:
        prod = Production(head, body)
        self.productions.append(prod)
        self.productions_by_head.setdefault(head, []).append(prod)

    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self.nonterminals

    def is_terminal(self, symbol: str) -> bool:
        return symbol in self.terminals

    @classmethod
    def from_lines(cls, lines: list[str]) -> "Grammar":
        """Construye la gramatica a partir de las n lineas de produccion.

        TODO: implementar el parseo real siguiendo el formato de la Seccion 2.2.1:
            1. Separar cada linea en '<head> -> <alt_1> <alt_2> ...'.
            2. Registrar el no terminal 'head'.
            3. Para cada alternativa, separar simbolo por simbolo (sin espacios
               dentro de la alternativa). Si la alternativa es 'e', es la
               produccion vacia.
            4. Clasificar cada simbolo de cada alternativa como terminal o no
               terminal (mayuscula => no terminal).
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return "\n".join(str(p) for p in self.productions)


def read_grammar(input_stream) -> Grammar:
    """Lee la gramatica desde un stream (p. ej. sys.stdin).

    Formato:
        linea 1: n (numero de no terminales)
        siguientes n lineas: producciones

    TODO: leer n, luego leer n lineas y delegar a Grammar.from_lines.
    """
    raise NotImplementedError
