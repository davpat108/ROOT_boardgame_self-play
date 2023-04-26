
from deck import Deck
from game import Game
from game_helper import random_choose, marquise_daylight, marquise_evening, alliance_birsong, alliance_daylight, alliance_evening, vagabond_birdsong, vagabond_daylight, vagabond_evening, get_all_daylight_option_alliance, move_and_account_to_sympathy, eyrie_birdsong, eyrie_daylight, eyrie_eveing, alliance_daylight_actions, alliance_evening_actions, get_all_evening_option_alliance

if __name__ == "__main__":
    game = Game(debug=False)
    
    winner = "No one"
    while winner == "No one":

        # CAT
        # BIRDSONG
        game.cat_birdsong_wood()
        marquise_daylight(game)
        marquise_evening(game)
    
        # EYRIE
        eyrie_birdsong(game)
        eyrie_daylight(game)
        eyrie_eveing(game)
        # ALLIANCE
        alliance_birsong(game)
        alliance_daylight(game)
        alliance_evening(game)
        

        # VAGABOND
        vagabond_birdsong(game)
        vagabond_daylight(game)
        vagabond_evening(game)