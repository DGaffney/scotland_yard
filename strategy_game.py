import operator
import igraph
import csv
import numpy as np
import json
import copy
import queue
import yen_k_shortest
def read_csv(filename):
  return [[int(i) for i in str.split(el, ",")] for el in str.split(str(open(filename, 'r').read()), "\n")]

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
graph_types = ["taxi", "bus", "metro", "ferry"]
def moves_for_player(player, adversaries, graphs):
  adversary_positions = [a["position"] for a in adversaries]
  possible_methods = [g for g in graph_types if player['moves'][g] != 0]
  possible_count = [player['moves'][m] for m in possible_methods]
  possible_moves = [list(set(graphs[graph_types.index(m)].neighbors(player["position"]))-set(adversary_positions)) for m in possible_methods]
  available_methods = [am for i,am in enumerate(possible_methods) if len(possible_moves[i]) != 0]
  available_count = [ac for i,ac in enumerate(possible_count) if len(possible_moves[i]) != 0]
  available_moves = [am for i,am in enumerate(possible_moves) if len(possible_moves[i]) != 0]
  return [available_methods, available_count, available_moves]

def calculate_shortest_ticket_path_next_move(adversary, adversaries, spy, graphs, moves):
  tmp_graph = igraph.Graph()
  tmp_graph.add_vertices(nodes)
  valid_transit_types = [k for k in adversary['moves'].keys() if adversary['moves'][k]]
  edges = []
  for valid_transit_type in valid_transit_types:
    if valid_transit_type == "taxi":
      for edge in taxi_edges:
        if edge not in edges:
          edges.append(edge)
    elif valid_transit_type == "bus":
      for edge in bus_edges:
        if edge not in edges:
          edges.append(edge)
    elif valid_transit_type == "metro":
      for edge in bus_edges:
        if edge not in edges:
          edges.append(edge)
  for edge in edges:
    indices = [nodes.index(n) for n in edge]
    tmp_graph.add_edges([(indices[0], indices[1])])
  budget = copy.deepcopy(adversary['moves'])
  winning_strategy = None
  winning_transits = None
  solved = False
  strategies = []
  if moves in start_info['reveal_points']:
    adversary['spy_guess'] = spy['position']
  else:
    possible_moves = list(set(graphs[graph_types.index(spy["last_transit_type"])].neighbors(spy['position']))-set([adversary["position"]]))
    np.random.shuffle(possible_moves)
    adversary['spy_guess'] = possible_moves[0]
  strategies = yen_k_shortest.yen_igraph(tmp_graph, adversary["position"], adversary['spy_guess'], 10, None)[0]
  gz = [strategies.append(strat) for strat in yen_k_shortest.yen_igraph(taxi_graph, adversary["position"], adversary['spy_guess'], 3, None)[0]]
  transit_methods = []
  if tmp_graph.neighbors(adversary['position']) == [] or strategies[0] == []:
    return [-1, "dead"]
  for strategy in strategies:
    print(strategy)
    if len(strategy) == 1:
      preferences = [list(el) for el in list(reversed(sorted(budget.items(), key=operator.itemgetter(1))))]
      transition = sorted([adversary['position'], strategy[0]])
      transit_method = None
      if [el+1 for el in transition] in taxi_edges:
        transit_method = "taxi"
      elif [el+1 for el in transition] in bus_edges:
        transit_method = "bus"
      elif [el+1 for el in transition] in metro_edges:
        transit_method = "metro"
      return [strategy[0], transit_method]
    elif strategy[1] not in list(set([a["position"] for a in adversaries])-set([adversary["position"]])):
      transit_methods = []
      preferences = [list(el) for el in list(reversed(sorted(budget.items(), key=operator.itemgetter(1))))]
      length_in = 0
      impossible = False
      while length_in < len(strategy)-1 and not impossible:
        solved_step = False
        transition = sorted([strategy[length_in], strategy[length_in+1]])
        prev_length_in = length_in
        for p,preference in enumerate(preferences):
          if solved_step == False and preference[0] == "taxi" and preference[1] > 0 and [el+1 for el in transition] in taxi_edges:
            preferences[p][1] -= 1
            length_in += 1
            solved_step = True
            transit_methods.append("taxi")
          elif solved_step == False and preference[0] == "bus" and preference[1] > 0 and [el+1 for el in transition] in bus_edges:
            preferences[p][1] -= 1
            length_in += 1
            solved_step = True
            transit_methods.append("bus")
          elif solved_step == False and preference[0] == "metro" and preference[1] > 0 and [el+1 for el in transition] in metro_edges:
            preferences[p][1] -= 1
            length_in += 1
            solved_step = True
            transit_methods.append("metro")
        if prev_length_in == length_in:
          impossible = True
      if impossible == False:
        solved = True
        winning_transits = transit_methods
        winning_strategy = strategy
  if moves-1 in start_info['reveal_points']:
    adversary['spy_guess'] = None
  if winning_strategy != None:
    return [winning_strategy[1], winning_transits[0]]
  else:
    return adversary_random_next(adversary, adversaries, graphs, spy)

def adversary_random_next(adversary, adversaries, graphs, spy):
  available_methods, available_count, available_moves = moves_for_player(adversary, adversaries, graphs)
  if sum(available_count) != 0:
    action_type = np.random.multinomial(1, np.array(available_count)/float(sum(available_count))).tolist().index(1)
    np.random.shuffle(available_moves[action_type])
    movement = available_moves[action_type][0]
    return [movement, available_methods[action_type]]
  else:
    return [-1, "dead"]

def decide_adversary_move(adversary, graphs, adversaries, moves, reveal_points, spy, adversary_type="random"):
  next_move = None
  move_method = None
  if adversary['state'] != "dead":
    if moves in reveal_points or adversary['spy_guess'] != None:
      next_move, move_method = calculate_shortest_ticket_path_next_move(adversary, adversaries, spy, graphs, moves)
    else:
      next_move, move_method = adversary_random_next(adversary, adversaries, graphs, spy)
    if move_method != "dead":
      adversary['moves'][move_method] -= 1
      spy['moves'][move_method] += 1
      adversary['position'] = next_move
      graphs[graph_types.index(move_method)].vs[spy["position"]]['adversary_transits'] += 1
    else:
      adversary["state"] = "dead"
  return adversary 

def decide_spy_move(spy, graphs, adversaries, spy_type="random"):
  tmp_graph = igraph.Graph()
  tmp_graph.add_vertices(nodes)
  edges = []
  for edge in taxi_edges:
    if edge not in edges:
      edges.append(edge)
  for edge in bus_edges:
    if edge not in edges:
      edges.append(edge)
  for edge in metro_edges:
    if edge not in edges:
      edges.append(edge)
  for edge in edges:
    indices = [nodes.index(n) for n in edge]
    tmp_graph.add_edges([(indices[0], indices[1])])
  available_methods, available_count, available_moves = moves_for_player(spy, adversaries, graphs)
  adversary_positions = [a["position"] for a in adversaries if a['state'] != "dead"]
  cur_distance = np.mean([len(tmp_graph.get_shortest_paths(spy["position"], a["position"])[0]) for a in adversaries])
  distance_sets = []
  for available_move_group in available_moves:
    distance_set = []
    for available_move in available_move_group:
      adversary_distances = [len(tmp_graph.get_shortest_paths(available_move, a["position"])[0]) for a in adversaries]
      distance_set.append(np.mean(adversary_distances))
    distance_sets.append(distance_set)
  print(distance_sets)
  min_dists = [sorted(ds)[-1] for ds in distance_sets]
  max_min_dist = sorted(min_dists)[-1]
  transit_type = available_methods[min_dists.index(max_min_dist)]
  next_move = available_moves[min_dists.index(max_min_dist)][distance_sets[min_dists.index(max_min_dist)].index(max_min_dist)]
  spy["last_transit_type"] = transit_type
  spy['moves'][transit_type] -= 1
  spy['position'] = next_move
  graphs[graph_types.index(transit_type)].vs[next_move]['spy_transits'] += 1
  return spy 

spy_win_hits = np.array([0]*200)
adversary_lose_hits = np.array([0]*200)
spy_lose_hits = np.array([0]*200)
adversary_win_hits = np.array([0]*200)
taxi_graph = fill_in_graph(taxi_edges, nodes)
bus_graph = fill_in_graph(bus_edges, nodes)
metro_graph = fill_in_graph(metro_edges, nodes)
ferry_graph = fill_in_graph(ferry_edges, nodes)
spy_wins = 0
adversary_wins = 0
all_game_data = []
for i in range(1000):
  #IDEA - every adversary has an internal current guess for where spy is, and spy has a flag on the obj which shows previous transit type
  taxi_graph = fill_in_graph(taxi_edges, nodes)
  bus_graph = fill_in_graph(bus_edges, nodes)
  metro_graph = fill_in_graph(metro_edges, nodes)
  ferry_graph = fill_in_graph(ferry_edges, nodes)
  graphs = [taxi_graph, bus_graph, metro_graph, ferry_graph]
  print(i)
  np.random.shuffle(start_info["start_positions"])
  spy_start = start_info["start_positions"][0]-1
  adversary_starts = list(np.array(start_info["start_positions"][1:7])-1)
  adversaries = [{"transits": [a_s], "transit_types": [], "spy_guess": None, "role": "adversary", "state": "alive", "position": a_s, "moves": copy.deepcopy(start_info["tickets"]["adversaries"])} for a_s in adversary_starts]
  spy = {"transits": [spy_start], "transit_types": [], "role": "spy", "state": "alive", "position": spy_start, "moves": copy.deepcopy(start_info["tickets"]["spy"])}
  moves = 0
  adversary_moves = []
  while moves < 23 and spy["position"] not in [a["position"] for a in adversaries] and[a["state"] for a in adversaries].count("alive") > 0:
    print(moves)
    spy = decide_spy_move(spy, graphs, adversaries)
    new_adversaries = []
    for adversary in adversaries:
      new_adversaries.append(decide_adversary_move(adversary, graphs, adversaries, moves, start_info['reveal_points'], spy))
    adversary_moves.append([a["position"] for a in adversaries])
    adversaries = new_adversaries
    moves += 1
  if spy["position"] not in [a["position"] for a in adversaries]:
    spy_wins += 1
  else:
    adversary_wins += 1
  if moves == 23 and spy["position"] not in [a["position"] for a in adversaries]:
    spy_win_hits += np.array([graph.vs["spy_transits"] for graph in graphs]).sum(0)
    adversary_lose_hits += np.array([graph.vs["adversary_transits"] for graph in graphs]).sum(0)
  else:
    spy_lose_hits += np.array([graph.vs["spy_transits"] for graph in graphs]).sum(0)
    adversary_win_hits += np.array([graph.vs["adversary_transits"] for graph in graphs]).sum(0)
  all_game_data.append({'iteration': i, 'adversaries': adversaries, 'spy': spy, 'graphs': graphs})

[spy_wins, adversary_wins]

