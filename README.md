#Scotland Yard Network Analysis
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

In the beginning of the game, Adversaries have no priors on the location of the spy, so they move around randomly on the board (of course, they could work together to increase maximal coverage, but right now these agents act independent of one another). Once they know the location of the spy, they use an implementation of [Yen's algorithm](https://en.wikipedia.org/wiki/Yen's_algorithm) to contemplate several potential shortest paths towards the spy's known location, and then select the shortest one available that satisfies their current ticket alotment. On their next turn, they create a hypothesis as to the direction of the spy, and assume the spy has randomly walked to another node - each agent hypothesizes that the spy has moved to a node furthest away from this agent. They keep updating their guess at the path the spy is randomly walking, and keep using Yen's algorithm to approach their current hypothesis. When the spy is revealed in a later round, this guess is replaced with the reality, and the process continues.

The spy moves accordingly: the spy measures all of the distances from all of the agents, but doesn't account for the ticket alotments - it simply calculates how "far" an agent is from the spy in terms of shortest path distance for the union of the taxi, bus, and metro network. It then measures the average shortest path length for every node it could move to, and then moves to a node that is maximally distant by this metric. It continuously moves using this rule until the spy is either caught or the adversaries have lost due to round exhaustion or their inability to move any more.

##Results
5,960 games were simulated using the above rules, resulting in 3,738 Spy wins and 2,222 Adversary wins. From the recordings of the matches, a few statistical descriptions were generated. First, a map of the game:

![Map Of Scotland Yard](https://raw.githubusercontent.com/DGaffney/scotland_yard/master/results/visualization.png)

The nodes are colored by their community according to a modularity maximization algorithm, the edges are colored by the type of transit that connects the nodes.

![Winning ratio per start position](https://raw.githubusercontent.com/DGaffney/scotland_yard/master/results/spy_start_odds.png)

Surprisingly, the starting position for the Spy appears to matter - starting on Node 34 greatly increases the odds of winning versus Node 26, where more often than not the Spy will lose. The first three transitions were sorted into a machine learning program, but the algorithm could only correctly predict 65% of the matches, so these results aren't reported here (though the code for that is in predictor.py). 

Spy's that win tend towards the Metro stations and then towards the extremities, but don't linger in the outer core of the network (darker red indicates that the Spy transits through this area more - this is a composite graph of all transits for all Spy's that won their round):


![Winning Spy Transitions](https://raw.githubusercontent.com/DGaffney/scotland_yard/master/results/spy_win_transit_density.png)

Adversaries stick more around central high transit nodes, as they are more likely to be hypothesized during turns of Spy ambiguity: 

![Winning Adversaries Transitions](https://raw.githubusercontent.com/DGaffney/scotland_yard/master/results/spy_win_transit_density.png)

Transits per node are highly linear when plotted by total Adversary vs Spy transits:

![Transit Covariance](https://raw.githubusercontent.com/DGaffney/scotland_yard/master/results/transit_relationship.png)

There's likely more here to unpack, but for now, it's well past the weekend, and this is a weekend joke project... So feel free to modify and adapt the code to find any more interesting patterns (DISCLAIMER: This is weekend project code, there are probably bugs here and there). To get a copy of around 9,000 games, please download the pickle file on my site [here](http://devingaffney.com/files/9k_games.pkl).