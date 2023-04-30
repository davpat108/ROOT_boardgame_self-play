# ROOT_boardgame_self-play
Implementation of the popular boardgame ROOT, and training a self play AI on it

## The map
The map is stored as a graph, where each node is a place (meaning a clearing or a forest).

## Decks
The common deck and the vagabonds quest deck is implemented here.

## Actors
The 4 actors and the actions they can take from the state of the map, their board and their hand.


## Game
Functions that carry out the options from actors are located here

## Tests
Pytests to ensure ther game and its elements work strictly according to the rules.

## Configs
The bigger constants are located here.

## DTOS
Data transfer objects between options in the game state and functions that carry out the options.
## TODO

tax collection
something with alliance soldiers


# TODO first gonna skip
which woods to use when building, if you can build by the rule supply lines, you might be able to build unsupported wood
which craft activations to use for royal claim
