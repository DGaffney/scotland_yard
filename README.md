#Scotland Yard Network Analysis

![Map Of Scotland Yard](https://raw.githubusercontent.com/DGaffney/scotland_yard/master/results/successful_transits.png)

This is a repository that explores the network analysis attributes of the game [Scotland Yard](https://en.wikipedia.org/wiki/Scotland_Yard_(board_game)).


##Ambiguity leaderboard
If you're a spy, you want to try to get to these positions - in two turns, this is how many possible places you could be at:

* 67: 51 second-degree spaces
* 111: 50 second-degree spaces
* 89: 49 second-degree spaces
* 153: 46 second-degree spaces
* 159: 41 second-degree spaces
* 13: 40 second-degree spaces
* 46: 39 second-degree spaces
* 140: 38 second-degree spaces
* 79: 37 second-degree spaces
* 52: 36 second-degree spaces
* 185: 35 second-degree spaces
* 163: 31 second-degree spaces
* 124: 30 second-degree spaces

##Simulating Scotland Yard

As the spy moves around the board, they are transiting the various stations, or in network terms, nodes. Some nodes are connected to many other nodes, which means that there are many ways to escape that particular node, but also many ways to get to that node - if any of the six adversaries land on the node the spy currently sits on, the spy loses. At every point, each player has several methods of transit - taxi, bus, metro, or in the case of the spy, a black ticket that can stand in for any of those three OR an additional ferry route. The code in random\_game.py simulates as close to non-decision making as possible for the players - they simply move to an available position proportional to the tickets left for each type as they are available for the position. The code in strategy\_game.py is a bit more involved:

In the beginning of the game, Adversaries have no priors on the location of the spy, so they move around randomly on the board (of course, they could work together to increase maximal coverage, but right now these agents act independent of one another). Once they know the location of the spy, they use an implementation of [Yen's algorithm](https://en.wikipedia.org/wiki/Yen's_algorithm) to contemplate several potential shortest paths towards the spy's known location, and then select the shortest one available that satisfies their current ticket alotment. On their next turn, they create a hypothesis as to the direction of the spy, and assume the spy has randomly walked to another node (future feature update here is to have them hypothesize that the spy has moved to a node furthest away from this agent). They keep updating their guess at the path the spy is randomly walking, and keep using Yen's algorithm to approach their current hypothesis. When the spy is revealed in a later round, this guess is replaced with the reality, and the process continues.

The spy moves accordingly: the spy measures all of the distances from all of the agents, but doesn't account for the ticket alotments - it simply calculates how "far" an agent is from the spy in terms of shortest path distance for the union of the taxi, bus, and metro network. It then measures the average shortest path length for every node it could move to, and then moves to a node that is maximally distant by this metric. It continuously moves using this rule until the spy is either caught or the adversaries have lost due to round exhaustion or their inability to move any more.

##Upcoming
Currently, the code records metadata for each game in terms of the transits agents take and the ultimate outcome of the match. This will then be used to analyze the general dynamics of the game for agents playing under the terms described above.