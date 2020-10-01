import json
import networkx as nx
from networkx.readwrite import json_graph

with open('./data/graph_data.json') as f:
    j_graph = json.load(f)

dg = json_graph.node_link_graph(j_graph)
ag = nx.nx_agraph.to_agraph(dg)
ag.write('./data/test_from_json.dot')
ag.draw('./data/test_from_json.pdf', prog='dot')