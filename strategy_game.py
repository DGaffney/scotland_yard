import pickle
import random
import operator
import igraph
import csv
import numpy as np
import json
import copy
import queue
import yen_k_shortest
from collections import Counter
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
    distances_from_me = [len(full_adversary_graph.get_shortest_paths(adversary["position"], possible_move)[0]) for possible_move in possible_moves]
    max_distance_from_me = sorted(distances_from_me)[-1]
    adversary['spy_guess'] = random.choice([pm for k,pm in enumerate(possible_moves) if distances_from_me[k] == max_distance_from_me])
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
      adversary['transits'].append(next_move)
      adversary['transit_types'].append(move_method)
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
  if [available_methods, available_count, available_moves] == [[], [], []]:
    spy['state'] = 'dead'
  else:
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
    spy['transit_types'].append(transit_type)
    spy['transits'].append(next_move)
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
spy_win_record = []
full_adversary_graph = igraph.Graph()
full_adversary_graph.add_vertices(nodes)
fa_edges = []
for edge in taxi_edges:
  if edge not in fa_edges:
    fa_edges.append(edge)

for edge in bus_edges:
  if edge not in fa_edges:
    fa_edges.append(edge)

for edge in bus_edges:
  if edge not in fa_edges:
    fa_edges.append(edge)

for edge in fa_edges:
  indices = [nodes.index(n) for n in edge]
  full_adversary_graph.add_edges([(indices[0], indices[1])])

for i in range(10000):
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
  possible_starts = list(set(np.array(start_info["start_positions"])-1)-set(adversary_starts))
  adversaries = [{"transits": [a_s], "transit_types": [], "spy_guess": random.choice(possible_starts)-1, "role": "adversary", "state": "alive", "position": a_s, "moves": copy.deepcopy(start_info["tickets"]["adversaries"])} for a_s in adversary_starts]
  spy = {"transits": [spy_start], "transit_types": [], "role": "spy", "state": "alive", "position": spy_start, "moves": copy.deepcopy(start_info["tickets"]["spy"])}
  moves = 0
  adversary_moves = []
  while spy['state'] != "dead" and moves < 23 and spy["position"] not in [a["position"] for a in adversaries] and[a["state"] for a in adversaries].count("alive") > 0:
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
    spy_win_record.append(1)
  else:
    adversary_wins += 1
    spy_win_record.append(0)
  if moves == 23 and spy["position"] not in [a["position"] for a in adversaries]:
    spy_win_hits += np.array([graph.vs["spy_transits"] for graph in graphs]).sum(0)
    adversary_lose_hits += np.array([graph.vs["adversary_transits"] for graph in graphs]).sum(0)
  else:
    spy_lose_hits += np.array([graph.vs["spy_transits"] for graph in graphs]).sum(0)
    adversary_win_hits += np.array([graph.vs["adversary_transits"] for graph in graphs]).sum(0)
  all_game_data.append({'iteration': i, 'adversaries': adversaries, 'spy': spy, 'graphs': graphs})
  print([spy_wins, adversary_wins])


def analyze_game(all_game_data, spy_win_record):
  station_data = [str.split(el, ",") for el in str.split(open("data/nodelist.csv").read(), "\r\n")]
  station_dict = {}
  for name,st_type in station_data:
    station_dict[name] = st_type
  win_heatmap = {}
  loss_heatmap = {}
  adversary_starting_spot_wins = {}
  adversary_starting_spot_losses = {}
  spy_starting_spot_wins = {}
  spy_starting_spot_losses = {}
  adversary_heatmap_wins = {}
  adversary_heatmap_losses = {}
  spy_heatmap_wins = {}
  spy_heatmap_losses = {}
  adversary_timeline_positions_wins = {}
  adversary_timeline_positions_losses = {}
  spy_timeline_positions_wins = {}
  spy_timeline_positions_losses = {}
  adversary_timeline_positions_wins_generalized = {}
  adversary_timeline_positions_losses_generalized = {}
  spy_timeline_positions_wins_generalized = {}
  spy_timeline_positions_losses_generalized = {}
  spy_total_transits_heatmap_win = {}
  spy_total_transits_heatmap_loss = {}
  adversary_total_transits_heatmap_win = {}
  adversary_total_transits_heatmap_loss = {}
  for heatmap in [adversary_total_transits_heatmap_loss, adversary_total_transits_heatmap_win, spy_total_transits_heatmap_win, spy_total_transits_heatmap_loss, adversary_heatmap_wins, adversary_heatmap_losses, spy_heatmap_wins, spy_heatmap_losses, adversary_starting_spot_wins, adversary_starting_spot_losses, spy_starting_spot_wins, spy_starting_spot_losses]:
    for val in list(set(np.array(np.arange(200)+1).tolist())-set([108])):
      heatmap[str(val)] = 0
      win_heatmap[str(val)] = 0
      loss_heatmap[str(val)] = 0
  for heatmap in [adversary_timeline_positions_wins, adversary_timeline_positions_losses, spy_timeline_positions_wins, spy_timeline_positions_losses]:
    for val in list(set(np.array(np.arange(200)+1).tolist())-set([108])):
      heatmap[str(val)] = {}
      for i in np.arange(24):
        heatmap[str(val)][str(i)] = 0
  for heatmap in [adversary_timeline_positions_wins_generalized, adversary_timeline_positions_losses_generalized, spy_timeline_positions_wins_generalized, spy_timeline_positions_losses_generalized]:
    for i in np.arange(24):
      heatmap[str(i)] = {"metro": 0, "bus": 0, "taxi": 0, "ferry": 0}
  win_games = []
  loss_games = []
  for i,game in enumerate(all_game_data):
    if spy_win_record[i] == 0:
      loss_games.append(game)
    else:
      win_games.append(game)
  for win_game in win_games:
    spy_heatmap_wins[str(win_game["spy"]["position"]+1)] += 1
    spy_starting_spot_wins[str(win_game["spy"]["transits"][0]+1)] += 1
    for p in [a["position"] for a in win_game["adversaries"]]:
      adversary_heatmap_wins[str(p+1)] += 1
    for p in [a["transits"][0] for a in win_game["adversaries"]]:
      adversary_starting_spot_wins[str(p+1)] += 1
    for transit in [a["transits"] for a in win_game["adversaries"]]:
      for s,step in enumerate(transit):
        adversary_timeline_positions_wins[str(step+1)][str(s)] += 1
        adversary_total_transits_heatmap_win[str(step+1)] += 1
        adversary_timeline_positions_wins_generalized[str(s)][station_dict[str(step+1)]] += 1
    for s,step in enumerate(win_game["spy"]["transits"]):
      spy_timeline_positions_wins[str(step+1)][str(s)] += 1
      spy_total_transits_heatmap_win[str(step+1)] += 1
      spy_timeline_positions_wins_generalized[str(s)][station_dict[str(step+1)]] += 1
  for loss_game in loss_games:
    spy_heatmap_losses[str(loss_game["spy"]["position"]+1)] += 1
    spy_starting_spot_losses[str(loss_game["spy"]["transits"][0]+1)] += 1
    for p in [a["position"] for a in loss_game["adversaries"]]:
      adversary_heatmap_losses[str(p+1)] += 1
    for p in [a["transits"][0] for a in loss_game["adversaries"]]:
      adversary_starting_spot_losses[str(p+1)] += 1
    for transit in [a["transits"] for a in loss_game["adversaries"]]:
      for s,step in enumerate(transit):
        adversary_timeline_positions_losses[str(step+1)][str(s)] += 1
        adversary_total_transits_heatmap_loss[str(step+1)] += 1
        adversary_timeline_positions_losses_generalized[str(s)][station_dict[str(step+1)]] += 1
    for s,step in enumerate(loss_game["spy"]["transits"]):
      spy_timeline_positions_losses[str(step+1)][str(s)] += 1
      spy_total_transits_heatmap_loss[str(step+1)] += 1
      spy_timeline_positions_losses_generalized[str(s)][station_dict[str(step+1)]] += 1
  visualization_dataset = [["node_id", "spy_win_density", "spy_loss_density", "adversary_win_density", "adversary_loss_density", "spy_win_adversary_start_density", "spy_lose_adversary_start_density", "spy_win_spy_start_density", "spy_lose_spy_start_density","spy_total_transits_heatmap_win","spy_total_transits_heatmap_lose","adversary_total_transits_heatmap_win","adversary_total_transits_heatmap_lose"]]
  ml_dataset = [["spy_wins", "spy_start", "adversary_start_1", "adversary_start_2", "adversary_start_3", "adversary_start_4", "adversary_start_5", "adversary_start_6"]]
  generalized_transit_type_dataset = [["turn", "spy_win_avg_metro_count_spy", "spy_win_avg_bus_count_spy", "spy_win_avg_taxi_count_spy", "adversary_win_avg_metro_count_spy", "adversary_win_avg_bus_count_spy", "adversary_win_avg_taxi_count_spy", "spy_loss_avg_metro_count_spy", "spy_loss_avg_bus_count_spy", "spy_loss_avg_taxi_count_spy", "adversary_loss_avg_metro_count_spy", "adversary_loss_avg_bus_count_spy", "adversary_loss_avg_taxi_count_spy"]]
  for turn in np.arange(24):
    stw = [spy_timeline_positions_wins_generalized[str(turn)]["metro"], spy_timeline_positions_wins_generalized[str(turn)]["bus"], spy_timeline_positions_wins_generalized[str(turn)]["taxi"]]
    atw = [adversary_timeline_positions_wins_generalized[str(turn)]["metro"], adversary_timeline_positions_wins_generalized[str(turn)]["bus"], adversary_timeline_positions_wins_generalized[str(turn)]["taxi"]]
    stl = [spy_timeline_positions_losses_generalized[str(turn)]["metro"], spy_timeline_positions_losses_generalized[str(turn)]["bus"], spy_timeline_positions_losses_generalized[str(turn)]["taxi"]]
    atl = [adversary_timeline_positions_losses_generalized[str(turn)]["metro"], adversary_timeline_positions_losses_generalized[str(turn)]["bus"], adversary_timeline_positions_losses_generalized[str(turn)]["taxi"]]
    if sum(stw) != 0:
      stw = [s/float(sum(stw)) for s in stw]
    if sum(atw) != 0:
      atw = [s/float(sum(atw)) for s in atw]
    if sum(stl) != 0:
      stl = [s/float(sum(stl)) for s in stl]
    if sum(atl) != 0:
      atl = [s/float(sum(atl)) for s in atl]
    generalized_transit_type_dataset.append([turn,stw[0],stw[1],stw[2],atw[0],atw[1],atw[2],stl[0],stl[1],stl[2],atl[0],atl[1],atl[2]])
  for node_id in list(set(np.array(np.arange(200)+1).tolist())-set([108])):
    visualization_dataset.append([node_id, spy_heatmap_wins[str(node_id)], spy_heatmap_losses[str(node_id)], adversary_heatmap_wins[str(node_id)], adversary_heatmap_losses[str(node_id)],spy_starting_spot_wins[str(node_id)],spy_starting_spot_losses[str(node_id)],adversary_starting_spot_wins[str(node_id)],adversary_starting_spot_losses[str(node_id)],spy_total_transits_heatmap_win[str(node_id)],spy_total_transits_heatmap_loss[str(node_id)],adversary_total_transits_heatmap_win[str(node_id)],adversary_total_transits_heatmap_loss[str(node_id)]])
  for game in win_games:
    a_s = [a["transits"][0] for a in game["adversaries"]]
    a_s1 = [a["transits"][1] for a in game["adversaries"]]
    a_s2 = [a["transits"][2] for a in game["adversaries"]]
    ml_dataset.append([1, game["spy"]["transits"][0], game["spy"]["transits"][1], game["spy"]["transits"][2], a_s[0], a_s[1], a_s[2], a_s[3], a_s[4], a_s[5], a_s1[0], a_s1[1], a_s1[2], a_s1[3], a_s1[4], a_s1[5], a_s2[0], a_s2[1], a_s2[2], a_s2[3], a_s2[4], a_s2[5]])
  for game in loss_games:
    a_s = [a["transits"][0] for a in game["adversaries"]]
    a_s1 = [a["transits"][1] for a in game["adversaries"]]
    a_s2 = [a["transits"][2] for a in game["adversaries"]]
    ml_dataset.append([0, game["spy"]["transits"][0], game["spy"]["transits"][1], game["spy"]["transits"][2], a_s[0], a_s[1], a_s[2], a_s[3], a_s[4], a_s[5], a_s1[0], a_s1[1], a_s1[2], a_s1[3], a_s1[4], a_s1[5], a_s2[0], a_s2[1], a_s2[2], a_s2[3], a_s2[4], a_s2[5]])
  with open('games.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(ml_dataset)
