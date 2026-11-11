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
from grammar import Production, EPSILON, END_MARKER


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

        Cada nivel de profundidad agrega dos espacios de indentacion, para
        que se vea claramente la forma del arbol (los hijos mas indentados
        que su padre).
        """
        linea_actual = "  " * depth + f"{self.symbol} {self.attributes}"
        lineas = [linea_actual]
        for hijo in self.children:
            lineas.append(hijo.pretty_print(depth + 1))
        return "\n".join(lineas)


def build_parse_tree_ll1(grammar, table, input_string: str) -> ParseTreeNode | None:
    """Construye el arbol de derivacion usando el parser LL(1) dirigido por
    tabla (Seccion 4.4.4), registrando cada expansion como un nodo del
    arbol en lugar de solo validar la cadena.

    Es el mismo algoritmo de ll1.parse_ll1, pero ademas de la pila de
    simbolos mantenemos una pila paralela de ParseTreeNode: cada vez que se
    apila/desapila un simbolo, se apila/desapila su nodo correspondiente.
    Cuando se usa una produccion X -> Y1...Yk, el nodo de X (que ya existia
    en la pila de nodos) recibe como hijos los nuevos nodos de Y1...Yk.

    Returns:
        La raiz del arbol (nodo del simbolo inicial) si la cadena es
        aceptada, o None si es rechazada.
    """
    entrada = list(input_string) + [END_MARKER]
    posicion_entrada = 0

    nodo_raiz = ParseTreeNode(grammar.start_symbol)

    # Pila de simbolos (igual que en ll1.parse_ll1) y pila paralela de nodos.
    pila_simbolos = [END_MARKER, grammar.start_symbol]
    pila_nodos = [None, nodo_raiz]

    while pila_simbolos[-1] != END_MARKER:
        tope = pila_simbolos[-1]
        nodo_tope = pila_nodos[-1]
        simbolo_actual = entrada[posicion_entrada]

        if grammar.is_terminal(tope):
            if tope != simbolo_actual:
                return None
            # El terminal es una hoja: su atributo lexval es el caracter mismo.
            nodo_tope.attributes["lexval"] = tope
            pila_simbolos.pop()
            pila_nodos.pop()
            posicion_entrada += 1
        else:
            clave = (tope, simbolo_actual)
            if clave not in table:
                return None

            produccion = table[clave]
            nodo_tope.production = produccion

            pila_simbolos.pop()
            pila_nodos.pop()

            if produccion.body != (EPSILON,):
                # Creamos un nodo hijo por cada simbolo del cuerpo, en orden,
                # y los apilamos en orden inverso (igual que los simbolos).
                hijos = [ParseTreeNode(simbolo) for simbolo in produccion.body]
                nodo_tope.children = hijos
                for simbolo, hijo in zip(reversed(produccion.body), reversed(hijos)):
                    pila_simbolos.append(simbolo)
                    pila_nodos.append(hijo)
            else:
                # Produccion X -> epsilon: se agrega un hijo hoja especial
                # para que el arbol muestre la epsilon, con su propio nodo.
                nodo_tope.children = [ParseTreeNode(EPSILON)]

    if entrada[posicion_entrada] != END_MARKER:
        return None

    return nodo_raiz


def build_parse_tree_slr1(grammar, tables, input_string: str) -> ParseTreeNode | None:
    """Construye el arbol de derivacion usando el parser SLR(1) (Seccion
    4.6.3), registrando cada reduccion como la creacion de un nodo padre
    que agrupa a los nodos de la cima de la pila.

    Es el mismo algoritmo de slr1.parse_slr1, pero junto a la pila de
    estados mantenemos una pila paralela de ParseTreeNode. En cada shift se
    apila un nodo hoja (el terminal leido). En cada reduce A -> beta, se
    hace pop de |beta| nodos (que quedan como hijos, en el orden en que
    estaban en la pila) y se crea el nuevo nodo A con esos hijos.

    Returns:
        La raiz del arbol si la cadena es aceptada, o None si es rechazada.
    """
    tabla_action = tables["action"]
    tabla_goto = tables["goto"]

    entrada = list(input_string) + [END_MARKER]
    posicion_entrada = 0

    pila_de_estados = [0]
    pila_de_nodos: list[ParseTreeNode] = []

    while True:
        estado_actual = pila_de_estados[-1]
        simbolo_actual = entrada[posicion_entrada]

        clave = (estado_actual, simbolo_actual)
        if clave not in tabla_action:
            return None

        accion = tabla_action[clave]

        if accion[0] == "shift":
            _, estado_destino = accion
            pila_de_estados.append(estado_destino)

            nodo_hoja = ParseTreeNode(simbolo_actual)
            nodo_hoja.attributes["lexval"] = simbolo_actual
            pila_de_nodos.append(nodo_hoja)

            posicion_entrada += 1

        elif accion[0] == "reduce":
            _, produccion = accion
            es_epsilon = produccion.body == (EPSILON,)
            longitud_del_cuerpo = 0 if es_epsilon else len(produccion.body)

            for _ in range(longitud_del_cuerpo):
                pila_de_estados.pop()

            if es_epsilon:
                hijos = [ParseTreeNode(EPSILON)]
            else:
                # Los ultimos 'longitud_del_cuerpo' nodos de la pila son los
                # hijos, en el mismo orden en que aparecen en el cuerpo.
                hijos = pila_de_nodos[-longitud_del_cuerpo:]
                del pila_de_nodos[-longitud_del_cuerpo:]

            nuevo_nodo = ParseTreeNode(produccion.head, production=produccion, children=hijos)
            pila_de_nodos.append(nuevo_nodo)

            estado_tras_reducir = pila_de_estados[-1]
            estado_destino = tabla_goto[(estado_tras_reducir, produccion.head)]
            pila_de_estados.append(estado_destino)

        elif accion[0] == "accept":
            # Al aceptar, el unico nodo que queda en la pila es la raiz (S).
            return pila_de_nodos[-1]
