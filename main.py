
from deck import Deck, QuestDeck
from map import build_regular_forest
from actors import Marquise, Eyrie, Alliance, Vagabond
from actions import cat_birdsong_wood
from game import Game, random_choose
if __name__ == "__main__":
    game = Game(debug=False)
    
    winner = "No one"
    while winner == "No one":
        # CAT
        #BIRDSONG
        game.cat_birdsong_wood()
        # DAYLIGHT
        # CRAFT
        craft_options = game.marquise.get_options_craft()
        choice = random_choose(craft_options)
        game.marquise.craft(choice)
        # BULK OF OPTIONS
        
        