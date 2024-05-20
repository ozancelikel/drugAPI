from neo4j import GraphDatabase


class GraphHandler:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def read_node(self, node_name: str):
        with self.driver.session() as session:
            res = session.execute_read(self.select_node, node_name)
            return res

    def write_node(self, node_name: str):
        with self.driver.session() as session:
            session.execute_write(self.add_atc, node_name)

    def write_relation(self, node_1: str, node_2: str, level: str):
        self.write_node(node_1)
        self.write_node(node_2)
        with self.driver.session() as session:
            session.execute_write(self.create_interaction,
                                  node_1, node_2, level)

    def read_relation(self, node_1: str, node_2: str):
        with self.driver.session() as session:
            res = session.execute_read(self.select_interaction,
                                       node_1, node_2)
            return res

    @classmethod
    def select_node(cls, tx, node_name):
        res = tx.run("MATCH (n:Atc) "
                     "WHERE n.name = $node_name "
                     "RETURN n", node_name=node_name)
        if res.peek() is None:
            return None
        return res.single()[0]

    @classmethod
    def add_atc(cls, tx, name):
        tx.run("MERGE (a:Atc {name: $name})"
               "ON CREATE SET a.createdAt = timestamp()", name=name)

    @classmethod
    def create_interaction(cls, tx, name_a, name_b, level):
        tx.run("MATCH (a:Atc {name: $name_a}) "
               "MATCH (b:Atc {name: $name_b}) "
               "MERGE (a)-[r1:INTERACTS {level: $level}]->(b)"
               "MERGE (a)<-[r2:INTERACTS {level: $level}]-(b)",
               name_a=name_a, name_b=name_b, level=level)

    @classmethod
    def select_interaction(cls, tx, name_a, name_b):
        res = tx.run("MATCH (a:Atc {name: $name_a}) "
                     "-[r:INTERACTS]- "
                     "(b:Atc {name: $name_b})"
                     "RETURN r.level AS RelationshipLevel",
                     name_a=name_a, name_b=name_b)
        if res.peek() is None:
            return None
        return res.single()[0]


if __name__ == "__main__":
    greeter = GraphHandler("bolt://localhost:7687", "neo4j", "password")
    # greeter.print_greeting("hello, world")
    res = greeter.read_relation("Ozan", "NS")
    print(res)
    greeter.close()
