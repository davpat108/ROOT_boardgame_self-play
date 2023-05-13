#

from game import Game
import random
from copy import copy
from deck import Deck, QuestDeck
class Set:
    # NODE is and information set
    def __init__(self, state, parent, previous_random_samples, player, game_copy):
        self.parent = parent
        self.player = player
        self.number_of_visits = 0
        self.value = 0
        self.children = []
        self.previous_random_samples = previous_random_samples
        self.state = state
        self.game_copy = game_copy

    def generate_samples_base(self):
        """
        Generate samples at the start of a search
        """

        # Card I'm not seeing = deck+hands together
        avalible_quest_deck = copy(self.game_copy.deck.cards)
        for player in [self.game_copy.marquise, self.game_copy.eyrie, self.game.alliance, self.game.vagabond]:
            if player.name != self.player:
                avalible_quest_deck.cards += player.deck.cards
        
        if self.player != "Alliance":
            avalible_quest_deck.cards += self.game_copy.alliance.supporter_deck.cards

        avalible_quest_deck.random.shuffle()

        for player in [self.game_copy.marquise, self.game_copy.eyrie, self.game.alliance, self.game.vagabond]:
            if player.name != self.player:
                prev_hand_size = len(player.deck.cards)
                player.deck = Deck(empty=True)
                for _ in range(prev_hand_size):
                    player.deck.add_card(avalible_quest_deck.draw_card())
        
        if self.player != "Alliance":
            prev_supporter_size = len(self.game_copy.alliance.supporter_deck.cards)
            self.game_copy.alliance.supporter_deck = Deck(empty=True)
            for _ in range(prev_supporter_size):
                self.game_copy.alliance.supporter_deck.add_card(avalible_quest_deck.draw_card())
        

        if self.player != "Vagabond":
            avalible_quest_deck = copy(self.game_copy.quest_deck.cards)
            avalible_quest_deck.random.shuffle()
            vagabond_quest_deck_size = len(self.game_copy.vagabond.quest_deck.cards)
            self.game_copy.vagabond.quest_deck = QuestDeck(empty=True)
            for _ in range(vagabond_quest_deck_size):
                self.game_copy.vagabond.quest_deck.add_card(avalible_quest_deck.draw_card())

    
    def generate_samples_with_prior_samples(self):
        """
        Generate samples knowing the previous random samples
        """
        pass