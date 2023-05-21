#

from game import Game
import random
from copy import copy
from deck import Deck, QuestDeck
import logging
from game_helper_random import get_all_daylight_option_cat, cat_daylight_actions, get_loss_prios, get_ambush_usage, get_sappers_usage, get_armorers_usage, roll_dice, move_and_account_to_sympathy


def random_choose(options):
    if options is None:
        return None
    if len(options) == 0:
        return None
    return random.choice(options)

class Set:
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

    def expand(self, position, player_gave_card_to_another=None, player_drew_card=None, card_count=None):
        # FIRST EXPAND 
        if position == "start":
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
                #TODO BATTLE
                pass
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