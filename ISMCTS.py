#

from game import Game
import random
from copy import copy
from deck import Deck, QuestDeck
import logging


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
            options = game_sample.marquise.bbb_options((game_sample.marquise, game_sample.eyrie, game_sample.alliance, game_sample.vagabond))
            if options is None:
                self.state = 1
                return 
            choice = random_choose(options)
            if choice:
                logging.debug(f"Cats used Better burrow bank with {choice.name}")
                game_sample.better_burrow_bank(game_sample.marquise, choice)
