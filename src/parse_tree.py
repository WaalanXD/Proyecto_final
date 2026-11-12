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
        linea_actual = "  " * depth + f"{self.symbol} {self.attributes}"
        lineas = [linea_actual]
        for hijo in self.children:
            lineas.append(hijo.pretty_print(depth + 1))
        return "\n".join(lineas)


def build_parse_tree_ll1(grammar, table, input_string: str) -> ParseTreeNode | None:
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
                hijos = [ParseTreeNode(simbolo) for simbolo in produccion.body]
                nodo_tope.children = hijos
                for simbolo, hijo in zip(reversed(produccion.body), reversed(hijos)):
                    pila_simbolos.append(simbolo)
                    pila_nodos.append(hijo)
            else:
                nodo_tope.children = [ParseTreeNode(EPSILON)]

    if entrada[posicion_entrada] != END_MARKER:
        return None

    return nodo_raiz


def build_parse_tree_slr1(grammar, tables, input_string: str) -> ParseTreeNode | None:
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
