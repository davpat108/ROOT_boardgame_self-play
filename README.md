# ROOT_boardgame_self-play
Implementation of the popular boardgame ROOT, and training a self play AI on it

## The map
The map is stored as a graph, where each node is a place (meaning a clearing or a forest).

## Decks
The common deck and the vagabonds quest deck is implemented here.

## Actors
The 4 actors and the actions they can take from the state of the map, their board and their hand.

## Utils
Stuff that doesn't fit into the map nor the actors

## Actions
Action data transfer objects and the functions that change the gamestate can be found here.

## Tests
I wrote pytests to ensure ther game and its elements work strictly according to the rules.

## Configs
The bigger constats are located here.

## TODO
Vagabond discard items down to sack
crafting, move action, build,recruit, overwork tests
in get options: all the immidiet and persistent effect cards
dominance cards,
favor cards,

# TODO first gonna skip
which woods to use to build, if you can build by the rule supply lines, you might be able to build unsupported wood
which craft activations to use for royal claim