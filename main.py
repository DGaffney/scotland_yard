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

def fill_in_graph(edgelist, nodes):
  graph = igraph.Graph()
  graph.add_vertices(nodes)
  for edge in edgelist:
    indices = [nodes.index(n) for n in edge]
    graph.add_edges([(indices[0], indices[1])])
  return graph

nodes = (np.arange(0,200)+1).tolist()
taxi_edges = read_csv("data/taxi_map.txt")
bus_edges = read_csv("data/bus_map.txt")
metro_edges = read_csv("data/metro_map.txt")
ferry_edges = read_csv("data/ferry_map.txt")
taxi_graph = fill_in_graph(taxi_edges, nodes)
bus_graph = fill_in_graph(bus_edges, nodes)
metro_graph = fill_in_graph(metro_edges, nodes)
ferry_graph = fill_in_graph(ferry_edges, nodes)
start_info = json.loads(open("data/start_data.json").read())
