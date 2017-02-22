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

As the spy moves around the board, they are transiting the various stations, or in network terms, nodes. Some nodes are connected to many other nodes, which means that there are many ways to escape that particular node, but also many ways to get to that node - if any of the six adversaries land on the node the spy currently sits on, the spy loses. At every point, each player has several methods of transit