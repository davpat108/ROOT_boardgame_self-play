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
        avalible_deck = self.game_copy.deck.cards
        for player in [self.game_copy.marquise, self.game_copy.eyrie, self.game.alliance, self.game.vagabond]:
            if player.name != self.player:
                avalible_deck.cards += player.deck.cards
        
        if self.player != "Alliance":
            avalible_deck.cards += self.game_copy.alliance.supporter_deck.cards

        avalible_deck.random.shuffle()

        for player in [self.game_copy.marquise, self.game_copy.eyrie, self.game.alliance, self.game.vagabond]:
            if player.name != self.player:
                prev_hand_size = len(player.deck.cards)
                player.deck = Deck(empty=True)
                for _ in range(prev_hand_size):
                    player.deck.add_card(avalible_deck.draw_card())
        
        if self.player != "Alliance":
            prev_supporter_size = len(self.game_copy.alliance.supporter_deck.cards)
            self.game_copy.alliance.supporter_deck = Deck(empty=True)
            for _ in range(prev_supporter_size):
                self.game_copy.alliance.supporter_deck.add_card(avalible_deck.draw_card())
        

        if self.player != "Vagabond":
            avalible_quest_deck = self.game_copy.quest_deck.cards
            avalible_quest_deck.random.shuffle()
            vagabond_quest_deck_size = len(self.game_copy.vagabond.quest_deck.cards)
            self.game_copy.vagabond.quest_deck = QuestDeck(empty=True)
            for _ in range(vagabond_quest_deck_size):
                self.game_copy.vagabond.quest_deck.add_card(avalible_quest_deck.draw_card())

    
    def generate_samples_someone_draws_a_card(self, player):
        """
        Generate samples knowing the previous random samples, and someone draws a card
        """
        pass


    def generate_samples_one_player_gives_a_card_to_another(self, player1, player2, to_supporter_deck=False):
        """
        Generate samples knowing the previous random samples and a player gives a card to another player
        """
        if not to_supporter_deck:
            avalible_deck = self.game_copy.deck.cards
            for player in [self.game_copy.marquise, self.game_copy.eyrie, self.game.alliance, self.game.vagabond]:
                if player.name == player1 or player.name == player2:
                    avalible_deck.cards += player.deck.cards
            avalible_deck.random.shuffle()
            for player in [self.game_copy.marquise, self.game_copy.eyrie, self.game.alliance, self.game.vagabond]:
                if player.name == player1 or player.name == player2:
                    prev_hand_size = len(player.deck.cards)
                    player.deck = Deck(empty=True)
                    for _ in range(prev_hand_size):
                        player.deck.add_card(avalible_deck.draw_card())
        
        else:
            if not player2 == "Alliance":
                raise Exception("Can't give to supporter deck if not alliance")
            avalible_deck = self.game_copy.deck.cards

            for player in [self.game_copy.marquise, self.game_copy.eyrie, self.game.vagabond]:
                if player.name == player1:
                    avalible_deck.cards += player.deck.cards
            avalible_deck.cards += self.game_copy.alliance.supporter_deck.cards
            avalible_deck.random.shuffle()
            for player in [self.game_copy.marquise, self.game_copy.eyrie, self.game.vagabond]:
                if player.name == player1:
                    prev_hand_size = len(player.deck.cards)
                    player.deck = Deck(empty=True)
                    for _ in range(prev_hand_size):
                        player.deck.add_card(avalible_deck.draw_card())
            prev_supporter_size = len(self.game_copy.alliance.supporter_deck.cards)
            self.game_copy.alliance.supporter_deck = Deck(empty=True)
            for _ in range(prev_supporter_size):
                self.game_copy.alliance.supporter_deck.add_card(avalible_deck.draw_card())
    
    def generate_samples_I_gave_a_card_to_another_payer(self, player):
        """
        Propably unncessary as I know their whole hand at this point
        """
        pass