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
X means done XX means tested / means partially tested

Vagabond discard items down to sack
crafting XX, move action XX, build XX, recruit XX, overwork XX, revolt XX, sympathy XX, mobilize XX, train XX, organize XX, ruin_explore XX, aid XX, steal XX, complete quest XX, strike XX
update victory points check gain-loss XX
losing stuff in general  XX
bird turmoil, leader choice, despot commander builder(and vp anyways) XX

Cards:
ambush XX
Codebreaker XX
cobbler XX should be accounted for during the game
better burrow bank XX
tax collctor XX
armorers XX
sappers XX
brutal tactics XX
stand and deliver XX
command warren XX should be accounted for during the game
scouting party XX
royal claim XX

maybe priority list for battle losses not that good and full list is necessery?
no matching card to give alliance

# TODO first gonna skip
which woods to use to build, if you can build by the rule supply lines, you might be able to build unsupported wood
which craft activations to use for royal claim
