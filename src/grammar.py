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

        Cada linea tiene la forma '<head> -> <alt_1> <alt_2> ...', por
        ejemplo: "B -> bBc e" (dos alternativas: "bBc" y la vacia "e").

        Pasos que seguimos (formato de la Seccion 2.2.1):
            1. Separamos la linea en el no terminal (head) y las alternativas,
               usando "->" como separador.
            2. Registramos ese no terminal.
            3. Cada alternativa es una palabra sin espacios: la recorremos
               caracter por caracter para obtener los simbolos de su cuerpo
               (no hay espacios entre simbolos de una misma alternativa).
               Si la alternativa es exactamente 'e', es la produccion vacia.
            4. Un simbolo es no terminal si es una letra mayuscula; de lo
               contrario es terminal (puede ser letra minuscula, digito o
               cualquier otro caracter que no sea espacio).
        """
        gramatica = cls()

        for linea in lines:
            linea = linea.strip()
            if not linea:
                continue

            lado_izquierdo, lado_derecho = linea.split("->")
            no_terminal = lado_izquierdo.strip()
            gramatica.nonterminals.add(no_terminal)

            alternativas = lado_derecho.split()
            for alternativa in alternativas:
                if alternativa == EPSILON:
                    cuerpo = (EPSILON,)
                else:
                    cuerpo = tuple(alternativa)
                    for simbolo in cuerpo:
                        if simbolo.isupper():
                            gramatica.nonterminals.add(simbolo)
                        else:
                            gramatica.terminals.add(simbolo)
                gramatica.add_production(no_terminal, cuerpo)

        return gramatica

    def __str__(self) -> str:
        return "\n".join(str(p) for p in self.productions)


def read_grammar(input_stream) -> Grammar:
    """Lee la gramatica desde un stream (p. ej. sys.stdin).

    Formato (Seccion 2.2.1):
        linea 1: n (numero de no terminales)
        siguientes n lineas: producciones
    """
    numero_de_no_terminales = int(input_stream.readline().strip())

    lineas_de_produccion = []
    for _ in range(numero_de_no_terminales):
        lineas_de_produccion.append(input_stream.readline())

    return Grammar.from_lines(lineas_de_produccion)
