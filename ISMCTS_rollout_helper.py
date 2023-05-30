import random
from dtos import Battle_DTO, OverworkDTO, MoveDTO, CraftDTO, Item
from deck import Deck
from copy import copy
import logging
from game_helper_random import birdsong_card_actions, random_choose, daylight_card_actions, get_all_daylight_option_cat, cat_daylight_actions, move_and_account_to_sympathy, evening_card_actions, battle_bird
from game_helper_random import get_all_daylight_option_alliance, get_all_evening_option_alliance, alliance_daylight_actions, alliance_evening_actions, move_and_account_to_sympathy, get_all_daylight_actions_vagabond, vagabond_daylight_actions
from game_helper_random import marquise_birdsong, marquise_daylight, marquise_evening, alliance_birdsong, alliance_daylight, alliance_evening, vagabond_birdsong, vagabond_daylight, vagabond_evening, eyrie_birdsong, eyrie_daylight, eyrie_evening



def player_finish_actions_old(turn_order, state, game):
    game.check_dominance(game.marquise)
    birdsong_card_actions(game, game.marquise)
    game.cat_birdsong_wood()


    options = game.marquise.swap_discarded_dominance_card_options(game.dominance_discard_deck)
    choice = random_choose(options)
    if choice:
        logging.debug(f"{game.marquise.name} swapped dominance card")
        game.swap_discarded_dominance_card(game.marquise, choice[0], choice[1])
    daylight_card_actions(game, game.marquise)
    # CRAFT
    game.marquise.refresh_craft_activations(game.map)
    craft_options = game.marquise.get_options_craft(game.map)
    choice = random_choose(craft_options)
    if choice:
        logging.debug(f"{game.marquise.name} crafted {choice.card.craft}")
        _ = game.craft(game.marquise, choice)
    # ACTIONS
    recruited_already = False
    actions = [1, 1, 1]
    for _ in actions:
        # MAIN MOVES
        options = get_all_daylight_option_cat(game, recruited_already)
        choice = random_choose(options)
        if choice:
            recruited_already, moved = cat_daylight_actions(game, choice, recruited_already)
        # IF MARCH, MOVE AGAIN
        else:
            moved = False
        if moved == True:
            move_options = game.marquise.get_moves(game.map)
            move_choice = random_choose(move_options)
            if move_choice:
                move_and_account_to_sympathy(game, move_choice)
        
        # IF BIRD CARD, 1 MORE ACTION
        more_move_options = game.marquise.get_use_bird_card_to_gain_moves()
        more_moves_choice = random_choose(more_move_options)
        if more_moves_choice:
            logging.debug(f"Cat used bird card to gain a move")
            game.cat_use_bird_card_to_gain_move(more_moves_choice)
            actions.append(1)


    evening_card_actions(game, game.marquise)
    draws = game.marquise.count_for_card_draw(game.map)
    for _ in range(draws):
        game.marquise.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) <= 0: # DECK ONE LINER
            game.deck = copy(game.discard_deck)
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)
    discard_options = True
    while discard_options:
        discard_options = game.marquise.discard_down_to_five_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.marquise.deck.get_the_card(choice))
    # TODO EXIT

    game.check_dominance(game.eyrie)
    birdsong_card_actions(game, game.eyrie)
    # DRAW IF HAND EMPTY
    if len(game.eyrie.deck.cards) == 0:
        game.eyrie.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) <= 0: # DECK ONE LINER
            game.deck = copy(game.discard_deck)
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)
    
    # ADD UP TO TWO CARDS TO DECREE
    options = game.eyrie.get_decree_options()
    choice = random_choose(options)
    if choice:
        logging.debug(f"{game.eyrie.name} added {choice[1]} to the {choice[0]} decree")
        game.add_card_to_decree(*choice)
    else:
        logging.debug(f"{game.eyrie.name} did not add a card to the decree")
    options = game.eyrie.get_decree_options()
    options.append(False)
    choice = random_choose(options)
    if choice:
        logging.debug(f"{game.eyrie.name} added {choice[1]} to the {choice[0]} decree")
        game.add_card_to_decree(*choice)
    options = game.eyrie.get_no_roosts_left_options(game.map)
    if options:
        logging.debug(f"{game.eyrie.name} Has no roosts left")
        choice = random_choose(options)
        game.place_roost_if_zero_roost(choice)


    options = game.eyrie.swap_discarded_dominance_card_options(game.dominance_discard_deck)
    choice = random_choose(options)
    if choice:
        logging.debug(f"{game.eyrie.name} swapped dominance card")
        game.swap_discarded_dominance_card(game.eyrie, choice[0], choice[1])
    daylight_card_actions(game, game.eyrie)
    choice = True
    game.eyrie.refresh_craft_activations(game.map)
    while choice:
        options = game.eyrie.get_options_craft(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{game.eyrie.name} crafted {choice.card.craft}")
            wounded_cat_soldiers = game.craft(game.eyrie, choice)
            if wounded_cat_soldiers:
                option = game.marquise.get_field_hospital_options(suit=choice.card.card_suit, map = game.map)
                choice = random_choose(option)
                if choice:
                    game.field_hospital(wounded_cat_soldiers, choice)
            

    game.eyrie.refresh_temp_decree()
    turmoil = False

    for _ in range(len(game.eyrie.decree['recruit'])):
        options = game.eyrie.get_resolve_recruit(game.map)
        if options:
            choice = random_choose(options)
            logging.debug(f"{game.eyrie.name} recruited at {choice[0]}")
            game.recruit(placename = choice[0], actor = game.eyrie, card_ID=choice[1])
        else:
            turmoil = True
            logging.debug(f"{game.eyrie.name} fell into turmoil")
            break
    if not turmoil:
        for _ in range(len(game.eyrie.decree['move'])):
            options = game.eyrie.get_resolve_move(game.map)
            if options:
                choice = random_choose(options)
                move_and_account_to_sympathy(game, choice)
            else:
                turmoil = True
                logging.debug(f"{game.eyrie.name} fell into turmoil")
                break
    if not turmoil:  
        for _ in range(len(game.eyrie.decree['battle'])):
            options = game.eyrie.get_resolve_battle(game.map)
            if options:
                choice = random_choose(options)
                battle_bird(game, choice)
            else:
                logging.debug(f"{game.eyrie.name} fell into turmoil")
                turmoil = True
                break
    if not turmoil:
        for _ in range(len(game.eyrie.decree['build'])):
            options = game.eyrie.get_resolve_building(game.map)
            if options:
                choice = random_choose(options)
                logging.debug(f"{game.eyrie.name} built at {choice[0]}")
                game.build(place=game.map.places[choice[0]], building="roost", actor=game.eyrie, card_ID = choice[1])
            else:
                logging.debug(f"{game.eyrie.name} fell into turmoil")
                turmoil = True
                break
    
    if turmoil:
        options = game.eyrie.get_turmoil_options()
        choice = random_choose(options)
        logging.debug(f"{game.eyrie.name} chose {choice} as its new leader")
        game.bird_turmoil(choice)
    

    evening_card_actions(game, game.eyrie)
    game.eyrie_get_points()
    draws = game.eyrie.count_for_card_draw(game.map)
    for _ in range(draws):
        game.eyrie.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) <= 0: # DECK ONE LINER
            game.deck = copy(game.discard_deck)
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)
    discard_options = True
    while discard_options:
        discard_options = game.eyrie.discard_down_to_five_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.eyrie.deck.get_the_card(choice))
# TODO EXIT

    game.check_dominance(game.alliance)
    birdsong_card_actions(game, game.alliance)
    options = game.alliance.get_revolt_options(game.map)
    options.append(False)
    choice = random_choose(options)
    if choice:
        logging.debug(f"{game.alliance.name} revolted at {choice[0].name}")
        wounded_cat_soldiers = game.revolt(*choice)
        if wounded_cat_soldiers:
            option = game.marquise.get_field_hospital_options(placename=choice[0].name, map=game.map)
            choice = random_choose(option)
            if choice:
                game.field_hospital(wounded_cat_soldiers, choice)
    choice = True
    while choice:
        options = game.alliance.get_spread_sympathy_options(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{game.alliance.name} spread sympathy to {choice[0]}")
            game.spread_sympathy(*choice)

    options = game.alliance.swap_discarded_dominance_card_options(game.dominance_discard_deck)
    choice = random_choose(options)
    if choice:
        game.swap_discarded_dominance_card(game.alliance, choice[0], choice[1])
    daylight_card_actions(game, game.alliance)
    game.alliance.refresh_craft_activations(game.map)
    choice = True
    while choice:
        options = get_all_daylight_option_alliance(game)
        choice = random_choose(options)
        if choice:
            alliance_daylight_actions(game, choice)


    evening_card_actions(game, game.alliance)
    for _ in range(game.alliance.total_officers):
        options = get_all_evening_option_alliance(game)
        choice = random_choose(options) 
        if choice:
            alliance_evening_actions(game, choice)
        else:
            break
    draws = game.alliance.count_for_card_draw(game.map)
    for _ in range(draws):
        game.alliance.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) <= 0: # DECK ONE LINER
            game.deck = copy(game.discard_deck)
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
        discard_options = game.alliance.discard_down_to_five_supporters_options(game.map)
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.alliance.supporter_deck.get_the_card(choice))

    # TODO EXIT    

    birdsong_card_actions(game, game.vagabond)
    for _ in range(game.vagabond.other_items.count(Item("root_tea"))*2 + 3):
        options = game.vagabond.get_refresh_options()
        if options:
            choice = random_choose(options)
            logging.debug(f"{game.vagabond.name} refreshed {choice}")
            game.vagabond.refresh_item(choice)
        else:
            break
    options = game.vagabond.get_slip_options(game.map)
    choice = random_choose(options)
    card_to_give_if_sympathy = game.vagabond.card_to_give_to_alliace_options(game.map.places[choice.end].suit)
    card = random_choose(card_to_give_if_sympathy)
    logging.debug(f"{game.vagabond.name} slipped to {choice.end}")
    game.slip(choice.end, card_to_give_if_sympathy=card)


    options = game.vagabond.swap_discarded_dominance_card_options(game.dominance_discard_deck)
    choice = random_choose(options)
    if choice:
        game.swap_discarded_dominance_card(game.vagabond, choice[0], choice[1])
    daylight_card_actions(game, game.vagabond)
    choice = True
    consequitive_aids = 0
    while choice:
        options = get_all_daylight_actions_vagabond(game)
        choice = random_choose(options)
        if choice:
            consequitive_aids = vagabond_daylight_actions(game, choice, consequitive_aids)


    evening_card_actions(game, game.vagabond)
    if ord(game.map.vagabond_position) > ord('L'):
        game.vagabond.repair_and_refresh_all()
    draws = game.vagabond.count_for_card_draw()
    for _ in range(draws):
        game.vagabond.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) <= 0: # DECK ONE LINER
            game.deck = copy(game.discard_deck)
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)

    discard_options = True
    while discard_options:
        discard_options = game.vagabond.discard_down_to_five_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.vagabond.deck.get_the_card(choice))
    
    discard_options = True
    while discard_options:
        discard_options = game.vagabond.get_discard_items_down_to_sack_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.vagabond.satchel.remove(choice)

def play(player, game):

    if player == "cat":
        marquise_birdsong(game)
        marquise_daylight(game)
        marquise_evening(game)

    elif player == "bird":
        eyrie_birdsong(game)
        eyrie_daylight(game)
        eyrie_evening(game)
            
    elif player == "alliance":
        alliance_birdsong(game)
        alliance_daylight(game)
        alliance_evening(game)

    elif player == "vagabond":
        vagabond_birdsong(game)
        vagabond_daylight(game)
        vagabond_evening(game)

