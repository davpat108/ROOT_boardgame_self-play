
from deck import Deck, QuestDeck
from map import build_regular_forest
from actors import Marquise, Eyrie, Alliance, Vagabond
from actions import cat_birdsong_wood
from game import Game, random_choose, cat_daylight_actions, get_all_daylight_option_cat, cat_move
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
        # DAY ACTIONS
        recruited_already = False
        actions = 3
        for i in range(actions):
            # MAIN MOVES
            options = game.get_all_daylight_option_cat(game, recruited_already)
            choice = random_choose(options)
            recruited_already, moved = cat_daylight_actions(game, choice, recruited_already)

            # IF MARCH, MOVE AGAIN
            if moved == True:
                move_options = game.marquise.get_moves(game.map)
                move_choice = random_choose(move_options)
                cat_move(game, move_choice)
            
            # IF BIRD CARD, 1 MORE ACTION
            more_move_options = game.marquise.get_use_bird_card_to_gain_moves()
            more_moves_choice = random_choose(more_move_options)
            if more_moves_choice:
                game.marquise.cat_use_bird_card_to_gain_move(more_moves_choice)
                actions += 1
        # EVENING
        draws = game.marquise.count_for_card_draw()
        for _ in range(draws):
            game.marquise.deck.add_card(game.deck.draw_card())
            if len(game.deck.cards) >= 0: # DECK ONE LINER
                game.deck = game.discard_deck
                game.deck.shuffle_deck()
                game.discard_deck = Deck(empty=True)
        
        # EYRIE


        # ALLIANCE


        # VAGABOND