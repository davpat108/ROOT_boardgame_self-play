#

from game import Game
import random
from copy import copy
from deck import Deck, QuestDeck
import logging
from game_helper_random import get_all_daylight_option_cat, cat_daylight_actions, move_and_account_to_sympathy, get_all_daylight_option_alliance, alliance_daylight_actions, get_all_evening_option_alliance, alliance_evening_actions, battle_vagabond, battle_cat, battle_bird, battle_alliance
from game_helper_random import marquise_birdsong, marquise_daylight, marquise_evening, alliance_birdsong, alliance_daylight, alliance_evening, vagabond_birdsong, vagabond_daylight, vagabond_evening, eyrie_birdsong, eyrie_daylight, eyrie_evening, get_all_daylight_actions_vagabond, vagabond_daylight_actions
from ISMCTS_rollout_helper import play
from item import Item
from actors import ExhaustbootERROR
import math


def random_choose(options):
    if options is None:
        return None
    if len(options) == 0:
        return None
    return random.choice(options)

class Node:
    # NODE is and information set
    def __init__(self, state, parent, previous_random_samples, player, game):
        self.parent = parent
        self.player = player

        self.number_of_visits = 0
        self.value = 0

        self.children = []
        self.previous_random_samples = previous_random_samples
        
        self.state = state
        self.game = game

    def calc_UCB_score(self, c_param=1.4):
        if self.number_of_visits == 0:
            return float("inf")
        return self.value/self.number_of_visits + c_param * (math.sqrt(math.log(self.parent.number_of_visits)/self.number_of_visits))
    
    def rollout_placeholder(self, player, turn_order):
        # Returns if the player won or not
        return False

    def generate_samples_base(self):
        """
        Generate samples at the start of a search
        """
        new_game = copy(self.game)
        # Card I'm not seeing = deck+hands together
        avalible_deck = new_game.deck.cards
        for player in [new_game.marquise, new_game.eyrie, new_game.alliance, new_game.vagabond]:
            if player.name != self.player:
                avalible_deck.cards += player.deck.cards
        
        if self.player != "Alliance":
            avalible_deck.cards += new_game.alliance.supporter_deck.cards

        avalible_deck.random.shuffle()

        for player in [new_game.marquise, new_game.eyrie, new_game.alliance, new_game.vagabond]:
            if player.name != self.player:
                prev_hand_size = len(player.deck.cards)
                player.deck = Deck(empty=True)
                for _ in range(prev_hand_size):
                    player.deck.add_card(avalible_deck.draw_card())
        
        if self.player != "Alliance":
            prev_supporter_size = len(new_game.alliance.supporter_deck.cards)
            new_game.alliance.supporter_deck = Deck(empty=True)
            for _ in range(prev_supporter_size):
                new_game.alliance.supporter_deck.add_card(avalible_deck.draw_card())
        

        if self.player != "Vagabond":
            avalible_quest_deck = new_game.quest_deck.cards
            avalible_quest_deck.random.shuffle()
            vagabond_quest_deck_size = len(new_game.vagabond.quest_deck.cards)
            new_game.vagabond.quest_deck = QuestDeck(empty=True)
            for _ in range(vagabond_quest_deck_size):
                new_game.vagabond.quest_deck.add_card(avalible_quest_deck.draw_card())
        
        return new_game
    
    def generate_samples_someone_draws_a_cards(self, drawing_player, card_count):
        """
        Generate samples knowing the previous random samples, and someone draws a card
        """
        new_game = copy(self.game)
        avalible_deck = new_game.deck.cards
        avalible_deck.random.shuffle()
        for player in [new_game.marquise, new_game.eyrie, new_game.alliance, new_game.vagabond]: 
            if player.name == drawing_player:
                player.deck.add_card(avalible_deck.draw_card())
        
        return new_game

    def generate_samples_one_player_gives_a_card_to_another(self, player1, player2, to_supporter_deck=False):
        """
        Generate samples knowing the previous random samples and a player gives a card to another player
        """
        new_game = copy(self.game)
        if not to_supporter_deck:
            avalible_deck = new_game.deck.cards
            for player in [new_game.marquise, new_game.eyrie, self.game.alliance, self.game.vagabond]:
                if player.name == player1 or player.name == player2:
                    avalible_deck.cards += player.deck.cards
            avalible_deck.random.shuffle()
            for player in [new_game.marquise, new_game.eyrie, self.game.alliance, self.game.vagabond]:
                if player.name == player1 or player.name == player2:
                    prev_hand_size = len(player.deck.cards)
                    player.deck = Deck(empty=True)
                    for _ in range(prev_hand_size):
                        player.deck.add_card(avalible_deck.draw_card())
        
        else:
            if not player2 == "Alliance":
                raise Exception("Can't give to supporter deck if not alliance")
            avalible_deck = new_game.deck.cards

            for player in [new_game.marquise, new_game.eyrie, self.game.vagabond]:
                if player.name == player1:
                    avalible_deck.cards += player.deck.cards
            avalible_deck.cards += new_game.alliance.supporter_deck.cards
            avalible_deck.random.shuffle()
            for player in [new_game.marquise, new_game.eyrie, self.game.vagabond]:
                if player.name == player1:
                    prev_hand_size = len(player.deck.cards)
                    player.deck = Deck(empty=True)
                    for _ in range(prev_hand_size):
                        player.deck.add_card(avalible_deck.draw_card())
            prev_supporter_size = len(new_game.alliance.supporter_deck.cards)
            new_game.alliance.supporter_deck = Deck(empty=True)
            for _ in range(prev_supporter_size):
                new_game.alliance.supporter_deck.add_card(avalible_deck.draw_card())

    def expand_simplified(self, player_gave_card_to_another=None, player_drew_card=None, card_count=None, expand_count=5, player_orders=['cat', 'bird', 'alliance', 'vagabond']):
        for _ in range(expand_count):
            if self.previous_random_samples is None:
                game_sample = self.generate_samples_base()
            if player_gave_card_to_another is not None:
                game_sample = self.generate_samples_one_player_gives_a_card_to_another(player1=player_gave_card_to_another[0], player2=player_gave_card_to_another[1], to_supporter_deck=len(player_gave_card_to_another)==3)
            if player_drew_card is not None:
                game_sample = self.generate_samples_someone_draws_a_cards(drawing_player=player_drew_card, card_count=card_count)
            
            if self.state == 0:
                marquise_birdsong(game_sample)
                marquise_daylight(game_sample)
                marquise_evening(game_sample)
            
            if self.state == 1:
                eyrie_birdsong(game_sample)
                eyrie_daylight(game_sample)
                eyrie_evening(game_sample)
            
            if self.state == 2:
                alliance_birdsong(game_sample)
                alliance_daylight(game_sample)
                alliance_evening(game_sample)
            
            if self.state == 3:
                vagabond_birdsong(game_sample)
                vagabond_daylight(game_sample)
                vagabond_evening(game_sample)

            if self.state == 4:
                # CAT FIELD HOSPITAL
                pass
            
            if self.state == 5:
                # CAT AMBUSH
                pass

            if self.state == 6:
                # BIRD AMBUSH
                pass
                
            if self.state == 7:
                # ALLIANCE AMBUSH
                pass

            if self.state == 8:
                # VAGABOND AMBUSH
                pass
            
            if self.state == 9:
                # CAT ARMOERERS_SAPPERS_BRUTAL_TACTICS
                pass

            if self.state == 9:
                # BIRD ARMOERERS_SAPPERS_BRUTAL_TACTICS
                pass

            if self.state == 9:
                # ALLIANCE ARMOERERS_SAPPERS_BRUTAL_TACTICS
                pass

            if self.state == 9:
                # VAGABOND ARMOERERS_SAPPERS_BRUTAL_TACTICS
                pass
            
            self.children.append(game_sample)

    def rollout_simplified(self, player_orders=['cat', 'bird', 'alliance', 'vagabond']):
        # Returns if the player won or not with random choices till game end, the result is used to backpropagate
        next_player = player_orders[player_orders.index(self.game.current_player.name)+1]
        start = True

        while 1:
            try:
                game = Game(debug=False)
                print(game_num)
                while 1:
                    logging.basicConfig(filename=f'{game_num}thgame.log', encoding='utf-8', level=logging.DEBUG)
                    if not start or player_orders[0] == next_player:
                        play(player_orders[0])
                        start = False
                    if not start or player_orders[1] == next_player:
                        play(player_orders[1])
                        start = False
                    if not start or player_orders[2] == next_player:
                        play(player_orders[2])
                        start = False
                    if not start or player_orders[3] == next_player:
                        play(player_orders[3])
                        start = False

                    if game.winner:
                        game_num += 1
                        logging.debug(f"Game {game_num} winner is {game.winner[0]}, they won with a {game.winner[1]} victory")
                        if game.winner[0] == self.player:
                            return True
                        else:
                            return False
                        break
            except Exception as e:
                if isinstance(e, ExhaustbootERROR):
                    #There's an elusive 1 in 4000 game error when the vagabond runs out of boots to exhaust
                    print("Boot error")
                else:
                    raise e

    def expand_old(self, player_gave_card_to_another=None, player_drew_card=None, card_count=None, expand_count=3):
        # FIRST EXPAND 
        for _ in range(expand_count):
            if self.previous_random_samples is None:
                game_sample = self.generate_samples_base()
            if player_gave_card_to_another is not None:
                game_sample = self.generate_samples_one_player_gives_a_card_to_another(player1=player_gave_card_to_another[0], player2=player_gave_card_to_another[1], to_supporter_deck=len(player_gave_card_to_another)==3)
            if player_drew_card is not None:
                game_sample = self.generate_samples_someone_draws_a_cards(drawing_player=player_drew_card, card_count=card_count)

            if self.state == 0:
                ### BBB CAT
                options = game_sample.marquise.bbb_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                if options is None:
                    self.state = 1
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"Cats used Better burrow bank with {choice.name}")
                    game_sample.better_burrow_bank(game_sample.marquise, choice)

            if self.state == 1:
                # STAND AND DELIVER CAT
                options = game_sample.marquise.stand_and_deliver_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                if options is None:
                    self.state = 2
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.marquise.name} used stand and deliver with {choice.name}")
                    game_sample.stand_and_deliver(game_sample.marquise, choice)

            if self.state == 2:
                # ROYAL CLAIM CAT
                options = game_sample.marquise.get_royal_claim_options()
                if options is None:
                    self.state = 3
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.marquise.name} used royal heir")
                    game_sample.activate_royal_claim(game_sample.marquise)

            if self.state == 3:
                # SWAP DOMINANCE CARD CAT
                options = game_sample.marquise.swap_discarded_dominance_card_options(game_sample.dominance_discard_deck)
                if options is None:
                    self.state = 4
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.marquise.name} swapped dominance card")
                    game_sample.swap_discarded_dominance_card(game_sample.marquise, choice[0], choice[1])

            if self.state == 4:
                if game_sample.marquise.command_warren:
                    options = game_sample.marquise.get_battles(game_sample.map)
                    options.append(False)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.marquise.name} used command warren")
                        battle_cat(game_sample, choice)
                else:
                    self.state = 5
                    return

            if self.state == 5:
                # CODEBREAKERS
                if game_sample.marquise.codebreakers:
                    options = game_sample.marquise.codebreakers_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.marquise.name} used Codebreakers")
                        game_sample.marquise.known_hands[choice] = True
                else:
                    self.state = 6
                    return

            if self.state == 6:
                # TAX COLLECTOR
                if game_sample.marquise.tax_collector:
                    options = game_sample.marquise.get_tax_collector_options(game_sample.map)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.marquise.name} used tax collector")
                        game_sample.tax_collection(game_sample.marquise, choice)
                else:
                    self.state = 7
                    return

            if self.state == 7:
                # CRAFT
                game_sample.marquise.refresh_craft_activations(game_sample.map)
                craft_options = game_sample.marquise.get_options_craft(game_sample.map)
                choice = random_choose(craft_options)
                if choice:
                    logging.debug(f"{game_sample.marquise.name} crafted {choice.card.craft}")
                    _ = game_sample.craft(game_sample.marquise, choice)
                else:
                    self.state = 8
                    return

            if self.state == 8:
                # DAYLIGHT
                recruited_already = False
                actions = [1, 1, 1]
                for _ in actions:
                    # MAIN MOVES
                    options = get_all_daylight_option_cat(game_sample, recruited_already)
                    choice = random_choose(options)
                    if choice:
                        recruited_already, moved = cat_daylight_actions(game_sample, choice, recruited_already)
                    # IF MARCH, MOVE AGAIN
                    else:
                        moved = False
                    if moved == True:
                        move_options = game_sample.marquise.get_moves(game_sample.map)
                        move_choice = random_choose(move_options)
                        if move_choice:
                            move_and_account_to_sympathy(game_sample, move_choice)

                    # IF BIRD CARD, 1 MORE ACTION
                    more_move_options = game_sample.marquise.get_use_bird_card_to_gain_moves()
                    more_moves_choice = random_choose(more_move_options)
                    if more_moves_choice:
                        logging.debug(f"Cat used bird card to gain a move")
                        game_sample.cat_use_bird_card_to_gain_move(more_moves_choice)
                        actions.append(1)

            if self.state == 9:
                # COBBLER
                if game_sample.marquise.cobbler:
                    options = game_sample.marquise.get_moves(game_sample.map)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.marquise.name} used cobbler")
                        move_and_account_to_sympathy(game_sample, choice)
                else:
                    self.state = 10
                    return

            if self.state == 10:
                draws = game_sample.marquise.count_for_card_draw(game_sample.map)
                for _ in range(draws):
                    game_sample.marquise.deck.add_card(game_sample.deck.draw_card())
                    if len(game_sample.deck.cards) <= 0: # DECK ONE LINER
                        game_sample.deck = copy(game_sample.discard_deck)
                        game_sample.deck.shuffle_deck()
                        game_sample.discard_deck = Deck(empty=True)
                discard_options = True
                while discard_options:
                    discard_options = game_sample.marquise.discard_down_to_five_options()
                    if discard_options:
                        choice = random_choose(discard_options)
                        game_sample.discard_deck.add_card(game_sample.marquise.deck.get_the_card(choice))

            if self.state == 11:
                ### BBB BIRD
                options = game_sample.eyrie.bbb_options((game_sample.eyrie, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                if options is None:
                    self.state = 12
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"Cats used Better burrow bank with {choice.name}")
                    game_sample.better_burrow_bank(game_sample.eyrie, choice)

            if self.state == 12:
                # STAND AND DELIVER BIRD
                options = game_sample.eyrie.stand_and_deliver_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                if options is None:
                    self.state = 13
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.eyrie.name} used stand and deliver with {choice.name}")
                    game_sample.stand_and_deliver(game_sample.eyrie, choice)

            if self.state == 13:
                # ROYAL CLAIM BIRD
                options = game_sample.eyrie.get_royal_claim_options()
                if options is None:
                    self.state = 14
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.eyrie.name} used royal heir")
                    game_sample.activate_royal_claim(game_sample.eyrie)

            if self.state == 14:
                options = game_sample.eyrie.get_decree_options()
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.eyrie.name} added {choice[1]} to the {choice[0]} decree")
                    game_sample.add_card_to_decree(*choice)
                else:
                    logging.debug(f"{game_sample.eyrie.name} did not add a card to the decree")
                options = game_sample.eyrie.get_decree_options()
                options.append(False)
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.eyrie.name} added {choice[1]} to the {choice[0]} decree")
                    game_sample.add_card_to_decree(*choice)
                options = game_sample.eyrie.get_no_roosts_left_options(game_sample.map)
                if options:
                    logging.debug(f"{game_sample.eyrie.name} Has no roosts left")
                    choice = random_choose(options)
                    game_sample.place_roost_if_zero_roost(choice)

            if self.state == 15:
                # SWAP DOMINANCE CARD BIRD
                options = game_sample.eyrie.swap_discarded_dominance_card_options(game_sample.dominance_discard_deck)
                if options is None:
                    self.state = 16
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.eyrie.name} swapped dominance card")
                    game_sample.swap_discarded_dominance_card(game_sample.eyrie, choice[0], choice[1])

            if self.state == 16:
                if game_sample.eyrie.command_warren:
                    options = game_sample.eyrie.get_command_warren_battle(game_sample.map)
                    options.append(False)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.eyrie.name} used command warren")
                        battle_bird(game_sample, choice)
                else:
                    self.state = 17
                    return

            if self.state == 17:
                # CODEBREAKERS
                if game_sample.eyrie.codebreakers:
                    options = game_sample.eyrie.codebreakers_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.eyrie.name} used Codebreakers")
                        game_sample.eyrie.known_hands[choice] = True
                else:
                    self.state = 18
                    return

            if self.state == 18:
                # TAX COLLECTOR
                if game_sample.eyrie.tax_collector:
                    options = game_sample.eyrie.get_tax_collector_options(game_sample.map)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.eyrie.name} used tax collector")
                        game_sample.tax_collection(game_sample.eyrie, choice)
                else:
                    self.state = 19
                    return

            if self.state == 19:
                # CRAFT
                choice = True
                game_sample.eyrie.refresh_craft_activations(game_sample.map)
                while choice:
                    options = game_sample.eyrie.get_options_craft(game_sample.map)
                    options.append(False)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.eyrie.name} crafted {choice.card.craft}")
                        wounded_cat_soldiers = game_sample.craft(game_sample.eyrie, choice)
                        if wounded_cat_soldiers:
                            option = game_sample.marquise.get_field_hospital_options(suit=choice.card.card_suit, map = game_sample.map)
                            choice = random_choose(option)
                            if choice:
                                game_sample.field_hospital(wounded_cat_soldiers, choice)

            if self.state == 20:
                game_sample.eyrie.refresh_temp_decree()
                turmoil = False

                if not turmoil:
                    for _ in range(len(game_sample.eyrie.decree['recruit'])):
                        options = game_sample.eyrie.get_resolve_recruit(game_sample.map)
                        if options:
                            choice = random_choose(options)
                            logging.debug(f"{game_sample.eyrie.name} recruited at {choice[0]}")
                            game_sample.recruit(placename = choice[0], actor = game_sample.eyrie, card_ID=choice[1])
                        else:
                            turmoil = True
                            logging.debug(f"{game_sample.eyrie.name} fell into turmoil")
                            break
                if not turmoil:
                    for _ in range(len(game_sample.eyrie.decree['move'])):
                        options = game_sample.eyrie.get_resolve_move(game_sample.map)
                        if options:
                            choice = random_choose(options)
                            move_and_account_to_sympathy(game_sample, choice)
                        else:
                            turmoil = True
                            logging.debug(f"{game_sample.eyrie.name} fell into turmoil")
                            break
                if not turmoil:      
                    for _ in range(len(game_sample.eyrie.decree['battle'])):
                        options = game_sample.eyrie.get_resolve_battle(game_sample.map)
                        if options:
                            choice = random_choose(options)
                            battle_bird(game_sample, choice)
                        else:
                            logging.debug(f"{game_sample.eyrie.name} fell into turmoil")
                            turmoil = True
                            break

                if not turmoil:
                    for _ in range(len(game_sample.eyrie.decree['build'])):
                        options = game_sample.eyrie.get_resolve_building(game_sample.map)
                        if options:
                            choice = random_choose(options)
                            logging.debug(f"{game_sample.eyrie.name} built at {choice[0]}")
                            game_sample.build(place=game_sample.map.places[choice[0]], building="roost", actor=game_sample.eyrie, card_ID = choice[1])
                        else:
                            logging.debug(f"{game_sample.eyrie.name} fell into turmoil")
                            turmoil = True
                            break
                        
            if self.state == 21:
                if turmoil:
                    options = game_sample.eyrie.get_turmoil_options()
                    choice = random_choose(options)
                    logging.debug(f"{game_sample.eyrie.name} chose {choice} as its new leader")
                    game_sample.bird_turmoil(choice)
                else:
                    self.state = 22
                    return

            if self.state == 22:
                # COBBLER
                if game_sample.eyrie.cobbler:
                    options = game_sample.eyrie.get_cobbler_move_options(game_sample.map)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.eyrie.name} used cobbler")
                        move_and_account_to_sympathy(game_sample, choice)
                else:
                    self.state = 23
                    return

            if self.state == 23:
                game_sample.eyrie_get_points()
                draws = game_sample.eyrie.count_for_card_draw(game_sample.map)
                for _ in range(draws):
                    game_sample.eyrie.deck.add_card(game_sample.deck.draw_card())
                    if len(game_sample.deck.cards) <= 0: # DECK ONE LINER
                        game_sample.deck = copy(game_sample.discard_deck)
                        game_sample.deck.shuffle_deck()
                        game_sample.discard_deck = Deck(empty=True)
                discard_options = True
                while discard_options:
                    discard_options = game_sample.eyrie.discard_down_to_five_options()
                    if discard_options:
                        choice = random_choose(discard_options)
                        game_sample.discard_deck.add_card(game_sample.eyrie.deck.get_the_card(choice))

            if self.state == 24:
                ### BBB ALLIANCE
                options = game_sample.alliance.bbb_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                if options is None:
                    self.state = 25
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"Alliance used Better burrow bank with {choice.name}")
                    game_sample.better_burrow_bank(game_sample.alliance, choice)

            if self.state == 25:
                # STAND AND DELIVER ALLIANCE
                options = game_sample.alliance.stand_and_deliver_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                if options is None:
                    self.state = 26
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.alliance.name} used stand and deliver with {choice.name}")
                    game_sample.stand_and_deliver(game_sample.alliance, choice)

            if self.state == 26:
                # ROYAL CLAIM ALLIANCE
                options = game_sample.alliance.get_royal_claim_options()
                if options is None:
                    self.state = 27
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.alliance.name} used royal heir")
                    game_sample.activate_royal_claim(game_sample.alliance)

            if self.state == 27:
                options = game_sample.alliance.get_revolt_options(game_sample.map)
                options.append(False)
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.alliance.name} revolted at {choice[0].name}")
                    wounded_cat_soldiers = game_sample.revolt(*choice)
                    if wounded_cat_soldiers:
                        option = game_sample.marquise.get_field_hospital_options(placename=choice[0].name, map=game_sample.map)
                        choice = random_choose(option)
                        if choice:
                            game_sample.field_hospital(wounded_cat_soldiers, choice)
                else:
                    self.state = 28
                    return

            if self.state == 28:
                choice = True
                while choice:
                    options = game_sample.alliance.get_spread_sympathy_options(game_sample.map)
                    options.append(False)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.alliance.name} spread sympathy to {choice[0]}")
                        game_sample.spread_sympathy(*choice)

            if self.state == 29:
                # SWAP DOMINANCE CARD BIRD
                options = game_sample.alliance.swap_discarded_dominance_card_options(game_sample.dominance_discard_deck)
                if options is None:
                    self.state = 30
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.alliance.name} swapped dominance card")
                    game_sample.swap_discarded_dominance_card(game_sample.alliance, choice[0], choice[1])

            if self.state == 30:
                if game_sample.alliance.command_warren:
                    options = game_sample.alliance.get_battles(game_sample.map)
                    options.append(False)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.alliance.name} used command warren")
                        battle_alliance(game_sample, choice)
                else:
                    self.state = 31
                    return

            if self.state == 31:
                # CODEBREAKERS
                if game_sample.alliance.codebreakers:
                    options = game_sample.alliance.codebreakers_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.alliance.name} used Codebreakers")
                        game_sample.alliance.known_hands[choice] = True
                else:
                    self.state = 32
                    return

            if self.state == 32:
                # TAX COLLECTOR
                if game_sample.alliance.tax_collector:
                    options = game_sample.alliance.get_tax_collector_options(game_sample.map)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.alliance.name} used tax collector")
                        game_sample.tax_collection(game_sample.alliance, choice)
                else:
                    self.state = 33
                    return

            if self.state == 33:
                # ACTIONS
                game_sample.alliance.refresh_craft_activations(game_sample.map)
                choice = True
                while choice:
                    options = get_all_daylight_option_alliance(game_sample)
                    choice = random_choose(options)
                    if choice:
                        alliance_daylight_actions(game_sample, choice)

            if self.state == 34:
                # COBBLER
                if game_sample.alliance.cobbler:
                    options = game_sample.alliance.get_cobbler_move_options(game_sample.map)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.alliance.name} used cobbler")
                        move_and_account_to_sympathy(game_sample, choice)
                else:
                    self.state = 35
                    return

            if self.state == 35:
                for _ in range(game_sample.alliance.total_officers):
                    options = get_all_evening_option_alliance(game_sample)
                    choice = random_choose(options) 
                    if choice:
                        alliance_evening_actions(game_sample, choice)
                    else:
                        break

            if self.state == 36:
                draws = game_sample.alliance.count_for_card_draw(game_sample.map)
                for _ in range(draws):
                    game_sample.alliance.deck.add_card(game_sample.deck.draw_card())
                    if len(game_sample.deck.cards) <= 0: # DECK ONE LINER
                        game_sample.deck = copy(game_sample.discard_deck)
                        game_sample.deck.shuffle_deck()
                        game_sample.discard_deck = Deck(empty=True)

                discard_options = True
                while discard_options:
                    discard_options = game_sample.alliance.discard_down_to_five_options()
                    if discard_options:
                        choice = random_choose(discard_options)
                        game_sample.discard_deck.add_card(game_sample.alliance.deck.get_the_card(choice))

                discard_options = True
                while discard_options:
                    discard_options = game_sample.alliance.discard_down_to_five_supporters_options(game_sample.map)
                    if discard_options:
                        choice = random_choose(discard_options)
                        game_sample.discard_deck.add_card(game_sample.alliance.supporter_deck.get_the_card(choice))

            if self.state == 37:
                ### BBB VAGABOND
                options = game_sample.vagabond.bbb_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                if options is None:
                    self.state = 38
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"Vagabond used Better burrow bank with {choice.name}")
                    game_sample.better_burrow_bank(game_sample.vagabond, choice)  

            if self.state == 38:
                # STAND AND DELIVER Vagabond
                options = game_sample.vagabond.stand_and_deliver_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                if options is None:
                    self.state = 39
                    return 
                choice = random_choose(options)
                if choice:
                    logging.debug(f"{game_sample.vagabond.name} used stand and deliver with {choice.name}")
                    game_sample.stand_and_deliver(game_sample.vagabond, choice)

            if self.state == 39:
                for _ in range(game_sample.vagabond.other_items.count(Item("root_tea"))*2 + 3):
                    options = game_sample.vagabond.get_refresh_options()
                    if options:
                        choice = random_choose(options)
                        logging.debug(f"{game_sample.vagabond.name} refreshed {choice}")
                        game_sample.vagabond.refresh_item(choice)
                    else:
                        break

            if self.state == 40:
                options = game_sample.vagabond.get_slip_options(game_sample.map)
                choice = random_choose(options)
                card_to_give_if_sympathy = game_sample.vagabond.card_to_give_to_alliace_options(game_sample.map.places[choice.end].suit)
                card = random_choose(card_to_give_if_sympathy)
                logging.debug(f"{game_sample.vagabond.name} slipped to {choice.end}")
                game_sample.slip(choice.end, card_to_give_if_sympathy=card)

            if self.state == 41:
                options = game_sample.vagabond.swap_discarded_dominance_card_options(game_sample.dominance_discard_deck)
                choice = random_choose(options)
                if choice:
                    game_sample.swap_discarded_dominance_card(game_sample.vagabond, choice[0], choice[1])

            if self.state == 42:
                if game_sample.vagabond.command_warren:
                    options = game_sample.vagabond.get_battle_options(game_sample.map)
                    options.append(False)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.vagabond.name} used command warren")
                        battle_vagabond(game_sample, choice)
                else:
                    self.state = 43
                    return

            if self.state == 43:
                if game_sample.codebreakers:
                    options = game_sample.vagabond.codebreakers_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.vagabond.name} used Codebreakers")
                        game_sample.vagabond.known_hands[choice] = True
                else:
                    self.state = 44
                    return

            if self.state == 44:
                choice = True
                consequitive_aids = 0
                while choice:
                    options = get_all_daylight_actions_vagabond(game_sample)
                    choice = random_choose(options)
                    if choice:
                        consequitive_aids = vagabond_daylight_actions(game_sample, choice, consequitive_aids)

            if self.state == 45:
                if game_sample.vagabond.cobbler:
                    options = game_sample.vagabond.get_cobbler_move_options(game_sample.vagabond.map)
                    choice = random_choose(options)
                    if choice:
                        logging.debug(f"{game_sample.vagabond.name} used cobbler")
                        move_and_account_to_sympathy(game_sample, choice)


            if self.state == 46:
                if ord(game_sample.map.vagabond_position) > ord('L'):
                    game_sample.vagabond.repair_and_refresh_all()
                draws = game_sample.vagabond.count_for_card_draw()
                for _ in range(draws):
                    game_sample.vagabond.deck.add_card(game_sample.deck.draw_card())
                    if len(game_sample.deck.cards) <= 0: # DECK ONE LINER
                        game_sample.deck = copy(game_sample.discard_deck)
                        game_sample.deck.shuffle_deck()
                        game_sample.discard_deck = Deck(empty=True)
                discard_options = True
                while discard_options:
                    discard_options = game_sample.vagabond.discard_down_to_five_options()
                    if discard_options:
                        choice = random_choose(discard_options)
                        game_sample.discard_deck.add_card(game_sample.vagabond.deck.get_the_card(choice))

            if self.state == 47:
                discard_options = True
                while discard_options:
                    discard_options = game_sample.vagabond.get_discard_items_down_to_sack_options()
                    if discard_options:
                        choice = random_choose(discard_options)
                        game_sample.vagabond.satchel.remove(choice)
            
            self.children.append(game_sample)

    def selection(self):
        """Select a child node from children that has the maximum UCB score."""
        if len(self.children) == 0:
            return self
        return max(self.children, key=lambda c: c.calc_UCB_score())

    def backpropagate(self, reward):
        """Backpropagate the reward (result of the game) back up to the root node."""
        self.number_of_visits += 1
        self.value += reward
        if self.parent:
            self.parent.backpropagate(reward)

    def player_finish_round(self, turn_order, state):
        pass


def ISMCTS_decide(state, game, itermax, player):
    rootnode = Node(state=state, parent=None, game=game, previous_random_samples=None, player=player)
    rootnode.expand_old()
    for _ in range(itermax):
        current_node = rootnode

        # Selection
        current_node = current_node.selection()

        # Expansion
        current_node.expand_old()

        # Simulation
        reward = current_node.rollout(player)

        # Backpropagation
        current_node.backpropagate(reward)

    decision = rootnode.selection()
    return decision
