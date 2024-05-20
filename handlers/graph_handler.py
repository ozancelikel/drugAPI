from fastapi import HTTPException
from py2neo import Graph, Node, Relationship


class GraphHandler:
    def __init__(self, uri, auth):
        self.__graph = Graph(f"{uri}", auth=auth)

    def add_new_relation(self, node_1_lbl: str, node_2_lbl: str):
        node_1 = Node("Atc", name=node_1_lbl)
        node_2 = Node("Atc", name=node_2_lbl)
        try:
            self.__graph.create(Relationship(node_1, "INTERACTS", node_2, level="SEVERE"))
            self.__graph.create(Relationship(node_2, "INTERACTS", node_1, level="SEVERE"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_relationship(self, atc_1, atc_2):
        node_1 = self.get_node(atc_1)
        node_2 = self.get_node(atc_2)

        res = self.__graph.match((node_1, node_2)).first()
        if res:
            return res
        else:
            raise HTTPException(status_code=500, detail=f"Relationship {atc_1} - {atc_2} not found.")

    def get_node(self, node_name):
        res = self.__graph.nodes.match("Atc", name=node_name).first()
        if res:
            return res
        else:
            raise HTTPException(status_code=500, detail=f"Node {node_name} not found.")

