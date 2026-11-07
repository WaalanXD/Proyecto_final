"""
dependency_graph.py
--------------------
Evaluador GENERICO de SDDs (Item 3, Paso 5.3-5.4). No debe contener nada
especifico de la SDD de sdd.py: toda la informacion sobre atributos y
reglas se lee de ese modulo como datos.

Pasos (Secciones 5.2.1 y 5.2.2 del libro):
    1. Para cada nodo interno del arbol de derivacion, instanciar las
       reglas semanticas de su produccion (sdd.SDD_RULES), creando un
       vertice por cada atributo de cada simbolo de la produccion y una
       arista desde cada atributo usado hacia el atributo definido.
    2. Las hojas (terminales) aportan su lexval directamente (ya conocido,
       sin necesidad de regla).
    3. Calcular un orden topologico del grafo de dependencias resultante.
       Si hay un ciclo, la SDD es circular: reportarlo y detenerse.
    4. Evaluar los atributos en el orden topologico.
"""

from dataclasses import dataclass, field
from parse_tree import ParseTreeNode
import sdd


class CircularSDDError(Exception):
    """Se lanza cuando el grafo de dependencias tiene un ciclo, es decir,
    la SDD es circular para el arbol dado."""


@dataclass(frozen=True)
class GraphNode:
    """Vertice del grafo de dependencias: un atributo de un nodo concreto
    del arbol de derivacion (no de una produccion abstracta)."""
    tree_node_id: int  # id() del ParseTreeNode, o un id secuencial asignado
    attribute: str


def build_dependency_graph(
    root: ParseTreeNode,
) -> tuple[dict[GraphNode, set[GraphNode]], dict[GraphNode, tuple]]:
    """Recorre el arbol y, para cada nodo interno, instancia las reglas de
    sdd.SDD_RULES correspondientes a su produccion (Paso 5.3).

    Debe resolver cada AttributeRef(position, name) de una regla hacia el
    ParseTreeNode concreto: position 0 es el nodo mismo (head), position i
    (i >= 1) es root.children[i - 1].

    TODO: implementar el recorrido y la construccion de:
        - edges: dict GraphNode -> conjunto de GraphNodes que dependen de el
          (aristas salientes: de "quien se usa" hacia "quien se define").
        - rule_for_node: dict GraphNode (el definido) -> (SemanticRule,
          lista de GraphNode de los que depende, en orden) para poder
          evaluarlo despues.

    Returns:
        (edges, rule_for_node)
    """
    raise NotImplementedError


def topological_order(
    edges: dict[GraphNode, set[GraphNode]], all_nodes: set[GraphNode]
) -> list[GraphNode]:
    """Calcula un orden topologico del grafo de dependencias (Seccion
    5.2.2), por ejemplo usando DFS con deteccion de ciclos o Kahn.

    TODO: implementar. Si se detecta un ciclo, lanzar CircularSDDError.

    Returns:
        Lista de GraphNode en un orden valido de evaluacion (toda
        dependencia aparece antes del atributo que la usa).
    """
    raise NotImplementedError


def evaluate_sdd(root: ParseTreeNode) -> list[GraphNode]:
    """Orquesta la evaluacion completa de la SDD sobre el arbol dado
    (Item 3, Paso 5.4):
        1. Asigna lexval a las hojas (terminales).
        2. Construye el grafo de dependencias (build_dependency_graph).
        3. Calcula el orden topologico (topological_order). Si hay ciclo,
           relanzar/propagar CircularSDDError para que main.py reporte
           "la SDD es circular" y detenga el procesamiento de esa cadena.
        4. Evalua cada atributo en ese orden, llamando a rule.compute(*args)
           y guardando el resultado en root/children .attributes[name].

    TODO: implementar la orquestacion descrita arriba.

    Returns:
        El orden topologico usado (para poder imprimirlo, segun el
        enunciado: "la evaluacion del orden").
    """
    raise NotImplementedError
