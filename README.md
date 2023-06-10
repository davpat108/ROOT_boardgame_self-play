# Status:
Taking a little bit of rest from this project, will carry on shortly

# ROOT_boardgame_self-play
Implementation of the popular boardgame ROOT, and training a self play AI on it. The game backbone is made out of 3 parts. The first part contains all the info that represents the gamestate (map.py, actors.py), the secound all the possible actions in that gamestate (actors.py), the third carries out the options and changes the gamestate (game.py).

# Progess
Game backbone is mostly done, currently trying a information set monte carlo tree search. 
After ISMCTS is done, I'll use the models and encodings that are already written in model.py and test_model.py to implement more advanced solutions.
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
## Errors I couldn't figure out yet
Vagabond around once every 4000 fully random games tries to exhaust 2 boots while going to a hostile clearing, while only having one. Get_moves shouldn't return this move possibility. I can't figure out why it does.

# TODO first gonna skip
which woods to use when building, if you can build by the rule supply lines, you might be able to build unsupported wood
which craft activations to use for royal claim
tax collection throughout daylight instead of only at the start
