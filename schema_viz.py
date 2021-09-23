"""Given a schema in json format visualize it."""

import json
from graphviz import Digraph

def load_schema(filename):
    with open(filename) as sf:
        schema = json.load(sf)
    return schema

def get_digraph(nodes, edges, db_name):
    digraph = Digraph("Schema for " + db_name)
    for node in nodes:
        digraph.node(node)
    for node_a, node_b, multiplicity in edges:
        digraph.edge(node_a, node_b, label=multiplicity)
    return digraph

def disconnetted(collections, edges):
    connected_a = set([edge[0] for edge in edges])
    connected_b = set([edge[1] for edge in edges])
    connected = connected_a | connected_b
    return collections - connected

def process_schema(schema):
    nodes = []
    edges = []
    db_collections = None
    db_name = None
    loops = []
    for key in schema:
        db_name = key
        db_collections = set(schema[db_name])
        for collection in db_collections:
            collection_data = schema[db_name][collection]["object"]
            for field_key in collection_data:
                field_name = field_key
                multiplicity = ""
                if collection_data[field_key]["type"] == "ARRAY":
                    multiplicity = "N"
                    # remove plural
                    if field_key[-1] == "s":
                        field_name = field_key[:-1]
                if field_name in db_collections:
                    if collection != field_name:
                        # add only a node with edges
                        nodes.append(collection)
                        # the field is a reference to another collection
                        edges.append((collection, field_name, multiplicity))
                    else:
                        # break auto loops
                        loops.append(collection)
    return nodes, edges, db_name, disconnetted(db_collections, edges), loops

if __name__ == "__main__":
    schema = load_schema("schema.json")
    nodes, edges, db_name, disconnected_nodes, loops = process_schema(schema)
    print("These documents have a field with the same name as a collection")
    print(loops)
    print()
    print("These documents have no references to other documents")
    print(disconnected_nodes)
    digraph = get_digraph(nodes, edges, db_name)
    digraph.view()
