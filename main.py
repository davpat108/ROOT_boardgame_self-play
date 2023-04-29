
from deck import Deck
from game import Game
from game_helper import marquise_birdsong, marquise_daylight, marquise_evening, alliance_birsong, alliance_daylight, alliance_evening, vagabond_birdsong, vagabond_daylight, vagabond_evening, get_all_daylight_option_alliance, move_and_account_to_sympathy, eyrie_birdsong, eyrie_daylight, eyrie_eveing, alliance_daylight_actions, alliance_evening_actions, get_all_evening_option_alliance
import random
import logging

def play(player):

    if player == "cat":
        marquise_birdsong(game)
        marquise_daylight(game)
        marquise_evening(game)

    elif player == "bird":
        if not game.eyrie_dead:
            eyrie_birdsong(game)
            eyrie_daylight(game)
            eyrie_eveing(game)

    elif player == "alliance":
        alliance_birsong(game)
        alliance_daylight(game)
        alliance_evening(game)

    elif player == "vagabond":
        vagabond_birdsong(game)
        vagabond_daylight(game)
        vagabond_evening(game)

if __name__ == "__main__":
    game = Game(debug=False)
    turn_order = ['cat', 'bird', 'alliance', 'vagabond']
    #random.shuffle(turn_order)
    winner = "No one"
    game_num = 0
    while 1:
        logging.basicConfig(filename=f'{game_num}thgame.log', encoding='utf-8', level=logging.DEBUG)
        play(turn_order[0])
        play(turn_order[1])
        play(turn_order[2])
        play(turn_order[3])

        if game.winner:
            game_num += 1
            logging.debug(f"Game {game_num} winner is {game.winner[0]}, they won with a {game.winner[1]} victory")
            break