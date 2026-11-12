from dataclasses import dataclass, field

EPSILON = "e"
END_MARKER = "$"


@dataclass(frozen=True)
class Production:
    head: str
    body: tuple[str, ...]

    def __str__(self) -> str:
        body_str = "".join(self.body) if self.body != (EPSILON,) else EPSILON
        return f"{self.head} -> {body_str}"


class Grammar:
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
    numero_de_no_terminales = int(input_stream.readline().strip())

    lineas_de_produccion = []
    for _ in range(numero_de_no_terminales):
        lineas_de_produccion.append(input_stream.readline())

    return Grammar.from_lines(lineas_de_produccion)
