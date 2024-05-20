from fastapi import HTTPException
from py2neo import Graph, Node, Relationship


class GraphHandler:
    def __init__(self, uri: str, auth: tuple):
        self.__graph = Graph(f"{uri}", auth=auth)

    def add_new_relation(self, node_1_lbl: str, node_2_lbl: str, level: dict):
        node_1 = self.get_node(node_1_lbl)
        node_2 = self.get_node(node_2_lbl)
        if node_1 is None:
            node_1 = Node("Atc", name=node_1_lbl)
        if node_2 is None:
            node_2 = Node("Atc", name=node_2_lbl)
        try:
            self.__graph.create(Relationship(node_1, "INTERACTS", node_2, level=level[0]["interactionLevel"]))
            self.__graph.create(Relationship(node_2, "INTERACTS", node_1, level=level[0]["interactionLevel"]))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_relationship(self, atc_1, atc_2):
        node_1 = self.get_node(atc_1)
        node_2 = self.get_node(atc_2)
        if node_1 is None or node_2 is None:
            return None
        res = self.__graph.match((node_1, node_2)).first()
        return res

    def get_node(self, node_name):
        res = self.__graph.nodes.match("Atc", name=node_name).first()
        return res
       # raise HTTPException(status_code=500, detail=f"Node {node_name} not found.")
