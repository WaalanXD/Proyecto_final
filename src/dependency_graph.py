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


def _id_del_nodo(nodo: ParseTreeNode) -> int:
    """Identificador unico para un ParseTreeNode concreto del arbol.
    Usamos id() de Python (la direccion de memoria del objeto), que es
    unica mientras el objeto exista, para poder distinguir, por ejemplo,
    dos nodos distintos que comparten el mismo simbolo (como P1 y P2)."""
    return id(nodo)


def build_dependency_graph(
    root: ParseTreeNode,
) -> tuple[dict[GraphNode, set[GraphNode]], dict[GraphNode, tuple]]:
    """Recorre el arbol y, para cada nodo interno, instancia las reglas de
    sdd.SDD_RULES correspondientes a su produccion (Paso 5.3).

    Debe resolver cada AttributeRef(position, name) de una regla hacia el
    ParseTreeNode concreto: position 0 es el nodo mismo (head), position i
    (i >= 1) es root.children[i - 1].

    Returns:
        (edges, rule_for_node)
        edges: dict GraphNode -> conjunto de GraphNodes que dependen de el
               (arista "A se usa para definir B" se guarda como
               edges[A] incluye a B).
        rule_for_node: dict GraphNode (el atributo definido) -> (SemanticRule,
               lista de GraphNode de los que depende, en el mismo orden
               que rule.depends_on) para poder evaluarlo despues.
    """
    edges: dict[GraphNode, set[GraphNode]] = {}
    rule_for_node: dict[GraphNode, tuple] = {}

    def agregar_arista(desde: GraphNode, hacia: GraphNode) -> None:
        edges.setdefault(desde, set()).add(hacia)
        # Nos asegura que todo GraphNode que participe tenga una entrada en
        # 'edges', aunque sea un conjunto vacio (facilita el paso 2, el
        # orden topologico, que necesita conocer TODOS los vertices).
        edges.setdefault(hacia, set())

    def resolver_atributo(nodo: ParseTreeNode, referencia) -> GraphNode:
        """Traduce un AttributeRef (posicion, nombre) al GraphNode real,
        usando el nodo actual del arbol como referencia para 'posicion 0'."""
        if referencia.position == 0:
            simbolo_del_nodo = nodo
        else:
            simbolo_del_nodo = nodo.children[referencia.position - 1]
        return GraphNode(_id_del_nodo(simbolo_del_nodo), referencia.name)

    def recorrer(nodo: ParseTreeNode) -> None:
        if nodo.is_leaf():
            # Las hojas (terminales) ya tienen su lexval asignado por el
            # parser (parse_tree.py); no tienen reglas semanticas propias,
            # pero igual deben existir como vertices del grafo.
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
    """Calcula un orden topologico del grafo de dependencias (Seccion
    5.2.2), usando el algoritmo de Kahn: una analogia sencilla es la de
    "tareas con requisitos": un atributo solo se puede evaluar despues de
    que todos los atributos de los que depende ya fueron evaluados.

    Algoritmo de Kahn:
        1. Calcular, para cada vertice, cuantas aristas le entran (su
           "grado de entrada", es decir, de cuantos atributos depende).
        2. Mientras haya vertices con grado de entrada 0 (sin dependencias
           pendientes): sacar uno, agregarlo al resultado, y "quitar" sus
           aristas salientes (restando 1 al grado de entrada de sus vecinos).
        3. Si al final quedan vertices que nunca llegaron a grado 0, hay un
           ciclo: la SDD es circular para este arbol.

    Returns:
        Lista de GraphNode en un orden valido de evaluacion (toda
        dependencia aparece antes del atributo que la usa).
    """
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
    """Devuelve una lista con el nodo raiz y todos sus descendientes
    (recorrido simple del arbol), para poder ubicar cada ParseTreeNode a
    partir de su id."""
    nodos = [root]
    for hijo in root.children:
        nodos.extend(_todos_los_nodos_del_arbol(hijo))
    return nodos


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

    Returns:
        El orden topologico usado (para poder imprimirlo, segun el
        enunciado: "la evaluacion del orden").
    """
    # Paso 1: las hojas ya tienen su lexval puesto por el parser, pero por
    # si alguna no lo tuviera (por ejemplo el nodo 'e' de una produccion
    # vacia), se lo asignamos aqui tambien.
    for nodo in _todos_los_nodos_del_arbol(root):
        if nodo.is_leaf() and "lexval" not in nodo.attributes:
            nodo.attributes["lexval"] = nodo.symbol

    # Paso 2: construir el grafo de dependencias.
    edges, rule_for_node = build_dependency_graph(root)

    # Paso 3: orden topologico (lanza CircularSDDError si hay un ciclo).
    orden = topological_order(edges, set(edges.keys()))

    # Para poder guardar/leer valores por GraphNode, necesitamos ubicar
    # rapidamente el ParseTreeNode real a partir de su id().
    nodo_por_id = {_id_del_nodo(nodo): nodo for nodo in _todos_los_nodos_del_arbol(root)}
    valores: dict[GraphNode, object] = {}

    # Paso 4: evaluar cada atributo en el orden topologico.
    for vertice in orden:
        nodo_arbol = nodo_por_id[vertice.tree_node_id]

        if vertice.attribute == "lexval" and vertice not in rule_for_node:
            # lexval de una hoja: ya esta en nodo.attributes, solo lo
            # reflejamos en 'valores' para que otras reglas puedan usarlo.
            valores[vertice] = nodo_arbol.attributes["lexval"]
            continue

        regla, dependencias = rule_for_node[vertice]
        argumentos = [valores[dependencia] for dependencia in dependencias]
        valor_calculado = regla.compute(*argumentos)

        valores[vertice] = valor_calculado
        nodo_arbol.attributes[vertice.attribute] = valor_calculado

    return orden
