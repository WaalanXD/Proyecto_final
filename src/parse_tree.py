"""
parse_tree.py
-------------
Construccion del arbol de derivacion (parse tree) de una cadena, a partir
del parser de Item 2 (LL(1) o SLR(1)). El arbol es la entrada para la
construccion del grafo de dependencias de la SDD (Item 3, Secciones 5.1-5.2).

Cada nodo guarda:
    - symbol: el simbolo gramatical (terminal o no terminal).
    - production: la Production usada para expandir el nodo (None si es
      una hoja/terminal).
    - children: lista de nodos hijos, en el orden del cuerpo de la produccion.
    - attributes: dict atributo -> valor, llenado despues por el evaluador
      de la SDD (dependency_graph.py). Los terminales reciben su lexval
      (el caracter mismo) como atributo sintetizado.
"""

from dataclasses import dataclass, field
from grammar import Production


@dataclass
class ParseTreeNode:
    symbol: str
    production: Production | None = None
    children: list["ParseTreeNode"] = field(default_factory=list)
    attributes: dict[str, object] = field(default_factory=dict)

    def is_leaf(self) -> bool:
        return not self.children

    def pretty_print(self, depth: int = 0) -> str:
        """Imprime el arbol anotado, un nodo por linea, indentado por
        profundidad, con sus atributos (Item 3, Paso 5, salida esperada).

        TODO: formatear cada linea como, por ejemplo:
            "  " * depth + f"{self.symbol} {self.attributes}"
        y concatenar recursivamente con los hijos.
        """
        raise NotImplementedError


def build_parse_tree_ll1(grammar, table, input_string: str) -> ParseTreeNode | None:
    """Construye el arbol de derivacion usando el parser LL(1) dirigido por
    tabla (Seccion 4.4.4), registrando cada expansion como un nodo del
    arbol en lugar de solo validar la cadena.

    TODO: adaptar el algoritmo de ll1.parse_ll1 para, en cada paso en que se
    usa una produccion X -> Y1...Yk, crear un ParseTreeNode para X con hijos
    Y1...Yk (tambien como nodos), en vez de solo manipular la pila de
    simbolos. Una tecnica comun es mantener una pila paralela de nodos.

    Returns:
        La raiz del arbol (nodo del simbolo inicial) si la cadena es
        aceptada, o None si es rechazada.
    """
    raise NotImplementedError


def build_parse_tree_slr1(grammar, tables, input_string: str) -> ParseTreeNode | None:
    """Construye el arbol de derivacion usando el parser SLR(1) (Seccion
    4.6.3), registrando cada reduccion como la creacion de un nodo padre
    que agrupa a los nodos de la cima de la pila.

    TODO: adaptar el algoritmo de slr1.parse_slr1 para mantener, junto a la
    pila de estados, una pila paralela de ParseTreeNode. En cada shift, se
    apila un nodo hoja (terminal). En cada reduce A -> beta, se hace pop de
    |beta| nodos (los hijos, en orden), se crea un nodo A con esos hijos, y
    se apila el nuevo nodo A.

    Returns:
        La raiz del arbol si la cadena es aceptada, o None si es rechazada.
    """
    raise NotImplementedError
