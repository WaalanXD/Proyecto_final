from dataclasses import dataclass, field
from parse_tree import ParseTreeNode
import sdd


class CircularSDDError(Exception):
   


@dataclass(frozen=True)
class GraphNode:
    tree_node_id: int  


def _id_del_nodo(nodo: ParseTreeNode) -> int:
    return id(nodo)


def build_dependency_graph(
    root: ParseTreeNode,
) -> tuple[dict[GraphNode, set[GraphNode]], dict[GraphNode, tuple]]:
    edges: dict[GraphNode, set[GraphNode]] = {}
    rule_for_node: dict[GraphNode, tuple] = {}

    def agregar_arista(desde: GraphNode, hacia: GraphNode) -> None:
        edges.setdefault(desde, set()).add(hacia)
        edges.setdefault(hacia, set())

    def resolver_atributo(nodo: ParseTreeNode, referencia) -> GraphNode:
        if referencia.position == 0:
            simbolo_del_nodo = nodo
        else:
            simbolo_del_nodo = nodo.children[referencia.position - 1]
        return GraphNode(_id_del_nodo(simbolo_del_nodo), referencia.name)

    def recorrer(nodo: ParseTreeNode) -> None:
        if nodo.is_leaf():
            vertice_lexval = GraphNode(_id_del_nodo(nodo), "lexval")
            edges.setdefault(vertice_lexval, set())
            return

        clave_produccion = (nodo.symbol, nodo.production.body)
        reglas = sdd.SDD_RULES.get(clave_produccion, [])

        for regla in reglas:
            nodo_definido = resolver_atributo(nodo, regla.target)
            nodos_de_los_que_depende = [
                resolver_atributo(nodo, referencia) for referencia in regla.depends_on
            ]

            for nodo_usado in nodos_de_los_que_depende:
                agregar_arista(nodo_usado, nodo_definido)

            edges.setdefault(nodo_definido, set())
            rule_for_node[nodo_definido] = (regla, nodos_de_los_que_depende)

        for hijo in nodo.children:
            recorrer(hijo)

    recorrer(root)
    return edges, rule_for_node


def topological_order(
    edges: dict[GraphNode, set[GraphNode]], all_nodes: set[GraphNode]
) -> list[GraphNode]:
    grado_de_entrada: dict[GraphNode, int] = {nodo: 0 for nodo in all_nodes}
    for vecinos in edges.values():
        for vecino in vecinos:
            grado_de_entrada[vecino] = grado_de_entrada.get(vecino, 0) + 1

    # Empezamos con todos los vertices que no dependen de nada.
    sin_dependencias_pendientes = [
        nodo for nodo in all_nodes if grado_de_entrada[nodo] == 0
    ]

    orden: list[GraphNode] = []
    while sin_dependencias_pendientes:
        actual = sin_dependencias_pendientes.pop()
        orden.append(actual)

        for vecino in edges.get(actual, set()):
            grado_de_entrada[vecino] -= 1
            if grado_de_entrada[vecino] == 0:
                sin_dependencias_pendientes.append(vecino)

    if len(orden) != len(all_nodes):
        # Quedaron vertices con dependencias que nunca se resolvieron:
        # solo puede pasar si hay un ciclo en el grafo.
        raise CircularSDDError("La SDD es circular para este arbol de derivacion.")

    return orden


def _todos_los_nodos_del_arbol(root: ParseTreeNode) -> list[ParseTreeNode]:
    nodos = [root]
    for hijo in root.children:
        nodos.extend(_todos_los_nodos_del_arbol(hijo))
    return nodos


def evaluate_sdd(root: ParseTreeNode) -> list[GraphNode]:
    for nodo in _todos_los_nodos_del_arbol(root):
        if nodo.is_leaf() and "lexval" not in nodo.attributes:
            nodo.attributes["lexval"] = nodo.symbol
            
    edges, rule_for_node = build_dependency_graph(root)

    orden = topological_order(edges, set(edges.keys()))

    nodo_por_id = {_id_del_nodo(nodo): nodo for nodo in _todos_los_nodos_del_arbol(root)}
    valores: dict[GraphNode, object] = {}

    for vertice in orden:
        nodo_arbol = nodo_por_id[vertice.tree_node_id]

        if vertice.attribute == "lexval" and vertice not in rule_for_node:
            valores[vertice] = nodo_arbol.attributes["lexval"]
            continue

        regla, dependencias = rule_for_node[vertice]
        argumentos = [valores[dependencia] for dependencia in dependencias]
        valor_calculado = regla.compute(*argumentos)

        valores[vertice] = valor_calculado
        nodo_arbol.attributes[vertice.attribute] = valor_calculado

    return orden
