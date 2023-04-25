
from deck import Deck, QuestDeck
from map import build_regular_forest
from actors import Marquise, Eyrie, Alliance, Vagabond
from actions import cat_birdsong_wood
from game import Game, random_choose, vagabond_evening, cat_daylight_actions, get_all_daylight_option_alliance, move_and_account_to_sympathy, eyrie_birdsong_actions, eyrie_daylight_actions, alliance_daylight_actions, alliance_evening_actions, get_all_evening_option_alliance
if __name__ == "__main__":
    game = Game(debug=False)
    
    winner = "No one"
    while winner == "No one":

        # CAT
        # BIRDSONG
        game.cat_birdsong_wood()
        # DAYLIGHT
        # CRAFT
        game.marquise.refresh_craft_activations(game.map)
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
                move_and_account_to_sympathy(game, move_choice)
            
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

        discard_options = True
        while discard_options:
            discard_options = game.marquise.discard_down_to_five_options()
            if discard_options:
                choice = random_choose(discard_options)
                game.discard_deck.add_card(game.marquise.deck.get_the_card(choice))
        
        # EYRIE
        eyrie_birdsong_actions(game)
        eyrie_daylight_actions(game)
        game.eyrie_get_points()
        draws = game.eyrie.count_for_card_draw()
        for _ in range(draws):
            game.eyrie.deck.add_card(game.deck.draw_card())
            if len(game.deck.cards) >= 0: # DECK ONE LINER
                game.deck = game.discard_deck
                game.deck.shuffle_deck()
                game.discard_deck = Deck(empty=True)

        discard_options = True
        while discard_options:
            discard_options = game.eyrie.discard_down_to_five_options()
            if discard_options:
                choice = random_choose(discard_options)
                game.discard_deck.add_card(game.eyrie.deck.get_the_card(choice))

        # ALLIANCE
        # BIRDSONG
        options = game.alliance.get_revolt_options(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            game.revolt(*choice)

        options = game.alliance.get_spread_sympathy_options(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            game.spread_sympathy(*choice)

        # DAYLIGHT
        game.alliance.refresh_craft_activations(game.map)
        choice = True
        while choice:
            options = get_all_daylight_option_alliance(game)
            choice = random_choose(options)
            if choice:
                alliance_daylight_actions(game, choice)

        # EVENING
        for _ in range(game.alliance.total_officers):
            options = get_all_evening_option_alliance(game)
            if choice:
                choice = random_choose(options)
                alliance_evening_actions(game, choice)
            else:
                break

        draws = game.alliance.count_for_card_draw()
        for _ in range(draws):
            game.alliance.deck.add_card(game.deck.draw_card())
            if len(game.deck.cards) >= 0: # DECK ONE LINER
                game.deck = game.discard_deck
                game.deck.shuffle_deck()
                game.discard_deck = Deck(empty=True)
        
        discard_options = True
        while discard_options:
            discard_options = game.alliance.discard_down_to_five_options()
            if discard_options:
                choice = random_choose(discard_options)
                game.discard_deck.add_card(game.alliance.deck.get_the_card(choice))
        
        discard_options = True
        while discard_options:
            discard_options = game.alliance.discard_down_to_five_supporters_options()
            if discard_options:
                choice = random_choose(discard_options)
                game.discard_deck.add_card(game.alliance.supporter_deck.get_the_card(choice))

        

        

        # VAGABOND
        # BIRDSONG

        vagabond_evening(game)