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
graphs = [taxi_graph, bus_graph, metro_graph, ferry_graph]
graph_types = ["taxi", "bus", "metro", "ferry"]
def moves_for_player(player, graphs):
  available_methods = [m for m in player['moves'].keys()]
  available_count = [player['moves'][m] for m in available_methods if player['moves'][m]]
  available_moves = [graph.neighbors(player["position"]) for graph in graphs]
  return [available_methods, available_count, available_moves]

def decide_adversary_move(adversary, spy, graphs, adversary_type="50_50"):
  
def decide_spy_move(spy, graphs, spy_type="increase_distance"):
  available_methods, available_count, available_moves = moves_for_player(player, graphs)

def play_game():

np.random.shuffle(start_info["start_positions"])
spy_start = start_info["start_positions"][0]
adversary_starts = start_info["start_positions"][1:7]
adversaries = [{"position": a_s, "moves": start_info["tickets"]["adversaries"]} for a_s in adversary_starts]
spy = {"position": spy_start, "moves": start_info["tickets"]["spy"]}
moves = 0
while moves < 23 and spy["position"] not in [a["position"] for a in adversaries]:
  spy = decide_spy_move(spy, graphs, spy_type)
  
  moves += 1
  