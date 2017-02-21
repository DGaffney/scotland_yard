import igraph
import csv
import numpy as np
import json
def read_csv(filename):
  dataset = []
  with open(filename, 'rb') as f:
      reader = csv.reader(f)
      for row in reader:
        dataset.append([int(el) for el in row])
  return dataset

def fill_in_graph(edgelist, graph):
  for edge in edgelist:
    indices = [nodes.index(n) for n in edge]
    graph.add_edges([(indices[0], indices[1])])
  return graph

nodes = (np.arange(0,200)+1).tolist()
taxi_edges = read_csv("data/taxi_map.txt")
bus_edges = read_csv("data/bus_map.txt")
metro_edges = read_csv("data/metro_map.txt")
ferry_edges = read_csv("data/ferry_map.txt")
graph = igraph.Graph()
graph.add_vertices(nodes)
graph = fill_in_graph(taxi_edges, graph)
graph = fill_in_graph(bus_edges, graph)
graph = fill_in_graph(metro_edges, graph)
graph = fill_in_graph(ferry_edges, graph)
for v in graph.vs():
  v['ambiguity'] = len(set([item for sublist in [[vvv['name'] for vvv in vv.neighbors()] for vv in v.neighbors()] for item in sublist]))

for v in graph.vs():
  print str.join(",", [str(v.index+1), str(v['ambiguity'])])