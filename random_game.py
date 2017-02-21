import igraph
import csv
import numpy as np
import json
import copy
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
  graph.vs()['spy_transits'] = 0
  graph.vs()['adversary_transits'] = 0
  for edge in edgelist:
    indices = [nodes.index(n) for n in edge]
    graph.add_edges([(indices[0], indices[1])])
  return graph

#to be implemented: adversary adversary_type="50_50" spy spy_type="increase_distance"
nodes = (np.arange(0,200)+1).tolist()
taxi_edges = read_csv("data/taxi_map.txt")
bus_edges = read_csv("data/bus_map.txt")
metro_edges = read_csv("data/metro_map.txt")
ferry_edges = read_csv("data/ferry_map.txt")
start_info = json.loads(open("data/start_data.json").read())
graphs = [taxi_graph, bus_graph, metro_graph, ferry_graph]
graph_types = ["taxi", "bus", "metro"]
def moves_for_player(player, adversaries, graphs):
  adversary_positions = [a["position"] for a in adversaries]
  available_graphs = [g for g in graph_types if player['moves'][g] != 0]
  available_methods = [m for m in available_graphs]
  available_count = [player['moves'][m] for m in available_methods]
  available_moves = [graph.neighbors(player["position"]) for graph in graphs]
  available_methods = [am for i,am in enumerate(available_methods) if len(available_moves[i]) != 0]
  available_count = [ac for i,ac in enumerate(available_count) if len(available_moves[i]) != 0]
  available_moves = [am for i,am in enumerate(available_moves) if len(available_moves[i]) != 0]
  if player["role"] == "adversary":
    available_graphs = [g for g in graph_types if player['moves'][g] != 0]
    available_methods = [m for m in available_graphs]
    available_count = [player['moves'][m] for m in available_methods]
    available_moves = [list(set(graph.neighbors(player["position"]))-set(adversary_positions)) for graph in graphs]
    available_methods = [am for i,am in enumerate(available_methods) if len(available_moves[i]) != 0]
    available_count = [ac for i,ac in enumerate(available_count) if len(available_moves[i]) != 0]
    available_moves = [am for i,am in enumerate(available_moves) if len(available_moves[i]) != 0]
  return [available_methods, available_count, available_moves]

def decide_adversary_move(adversary, graphs, adversaries, adversary_type="random"):
  available_methods, available_count, available_moves = moves_for_player(adversary, adversaries, graphs)
  if adversary_type == "random":
    if sum(available_count) != 0:
      action_type = np.random.multinomial(1, np.array(available_count)/float(sum(available_count))).tolist().index(1)
      np.random.shuffle(available_moves[action_type])
      movement = available_moves[action_type][0]
      adversary['moves'][available_methods[action_type]] -= 1
      spy['moves'][available_methods[action_type]] += 1
      adversary['position'] = movement
      graphs[action_type].vs[spy["position"]]['adversary_transits'] += 1
    else:
      adversary["state"] = "dead"
  return adversary 

def decide_spy_move(spy, graphs, adversaries, spy_type="random"):
  available_methods, available_count, available_moves = moves_for_player(spy, adversaries, graphs)
  if spy_type == "random":
    if sum(available_count) != 0:
      action_type = np.random.multinomial(1, np.array(available_count)/float(sum(available_count))).tolist().index(1)
      np.random.shuffle(available_moves[action_type])
      movement = available_moves[action_type][0]
      spy['moves'][available_methods[action_type]] -= 1
      spy['position'] = movement
      graphs[action_type].vs[spy["position"]]['spy_transits'] += 1
    else:
      spy["state"] = "dead"
  return spy 

spy_win_hits = np.array([0]*200)
adversary_lose_hits = np.array([0]*200)
spy_lose_hits = np.array([0]*200)
adversary_win_hits = np.array([0]*200)
for i in range(10000):
  taxi_graph = fill_in_graph(taxi_edges, nodes)
  bus_graph = fill_in_graph(bus_edges, nodes)
  metro_graph = fill_in_graph(metro_edges, nodes)
  ferry_graph = fill_in_graph(ferry_edges, nodes)
  graphs = [taxi_graph, bus_graph, metro_graph, ferry_graph]
  print i
  np.random.shuffle(start_info["start_positions"])
  spy_start = start_info["start_positions"][0]
  adversary_starts = start_info["start_positions"][1:7]
  adversaries = [{"role": "adversary", "state": "alive", "position": a_s, "moves": copy.deepcopy(start_info["tickets"]["adversaries"])} for a_s in adversary_starts]
  spy = {"role": "spy", "state": "alive", "position": spy_start, "moves": start_info["tickets"]["spy"]}
  moves = 0
  while moves < 23 and spy["position"] not in [a["position"] for a in adversaries] and[a["state"] for a in adversaries].count("alive") > 0:
    spy = decide_spy_move(spy, graphs, adversaries)
    new_adversaries = []
    for adversary in adversaries:
      new_adversaries.append(decide_adversary_move(adversary, graphs, adversaries))
    adversaries = new_adversaries
    moves += 1
  if moves == 23 and spy["position"] not in [a["position"] for a in adversaries]:
    spy_win_hits += np.array([graph.vs["spy_transits"] for graph in graphs]).sum(0)
    adversary_lose_hits += np.array([graph.vs["adversary_transits"] for graph in graphs]).sum(0)
  else:
    spy_lose_hits += np.array([graph.vs["spy_transits"] for graph in graphs]).sum(0)
    adversary_win_hits += np.array([graph.vs["adversary_transits"] for graph in graphs]).sum(0)

[spy_win_hits/float(i), adversary_lose_hits/float(i), spy_lose_hits/float(i), adversary_win_hits/float(i)]