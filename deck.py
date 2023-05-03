from random import shuffle
from configs import total_common_card_info, vagabond_quest_card_info
import numpy as np

class Card:
    def __init__(self, ID:int, card_suit: str, craft, craft_cost:int, craft_suit:str):
        self.ID = ID
        self.card_suit = card_suit
        self.craft = craft
        self.craft_cost = craft_cost
        self.craft_suit = craft_suit
    
    def get_options(self, points: int, crafts: list):
        pass

    def __eq__(self, other:int) -> bool:
        if isinstance(other, Card):
            return self.ID == other.ID
        return False

class Deck:
    def __init__(self, empty = False):
        if not empty:
            # Init game
            self.cards = []
            for card_info in total_common_card_info:
                self.cards.append(Card(*card_info))
        
        else:
            # Init discard deck
            self.cards = []

        self.shuffle_deck()

    def get_the_card(self, ID):
        try:
            self.cards.remove(Card(*total_common_card_info[ID]))
            return Card(*total_common_card_info[ID])
        except:
            return "Card not in the deck"
    
    def get_a_card_like_it(self, card_craft):
        for card in self.cards:
            if card.craft == card_craft:
                self.cards.remove(card)
                return card
        raise Exception("No card like that in the deck")

    def draw_card(self):
        if len(self.cards) == 0:
            return "Deck Empty"
        return self.cards.pop(0)
    
    def add_card(self, card: Card):
        """
        Add a card to the end, mainly used for discard deck
        """
        if isinstance(card, Card):
            self.cards.append(card)
        else:
            return "Deck Empty"
    
    def shuffle_deck(self):
        shuffle(self.cards)

    def encode_deck(self):
        encoded_suits= np.zeros((4, 1))
        encoded_deck = np.zeros((54, 1))
        for card in self.cards:
            if card.card_suit == "fox":
                encoded_suits[0][0] += 1
            elif card.card_suit == "mouse":
                encoded_suits[1][0] += 1
            elif card.card_suit == "rabbit":
                encoded_suits[2][0] += 1
            elif card.card_suit == "bird":
                encoded_suits[3][0] += 1
            
            encoded_deck[card.ID][0] = 1

        return encoded_deck, encoded_suits
            

class QuestCard:
    def __init__(self, ID:int, item1, item2, suit: str):
        self.ID = ID
        self.suit = suit
        self.item1 = item1
        self.item2 = item2
    
    def get_options(self, points: int, crafts: list):
        pass

    def __eq__(self, other:int) -> bool:
        if isinstance(other, QuestCard):
            return self.ID == other.ID
        return False
    
class QuestDeck:
    def __init__(self, empty = False):
        if not empty:
            # Init game
            self.cards = []
            for card_info in vagabond_quest_card_info:
                self.cards.append(QuestCard(*card_info))
        
        else:
            # Init discard deck
            self.cards = []

        self.shuffle_deck()

    def get_the_card(self, ID):
        try:
            self.cards.remove(QuestCard(*vagabond_quest_card_info[ID]))
            return QuestCard(*vagabond_quest_card_info[ID])
        except:
            return("Card not in the deck")
    
    def draw_card(self):
        if len(self.cards) == 0:
            return "Deck Empty"
        return self.cards.pop(0)
    
    def add_card(self, card: QuestCard):
        """
        Add a card to the end, mainly used for discard deck
        """
        self.cards.append(card)
    
    def shuffle_deck(self):
        shuffle(self.cards)
    
    def encode_quest_deck(self):
        encoded_suits= np.zeros((3, 1))
        encoded_deck = np.zeros((15, 1))
        for card in self.cards:
            if card.suit == "fox":
                encoded_suits[0][0] += 1
            elif card.suit == "mouse":
                encoded_suits[1][0] += 1
            elif card.suit == "rabbit":
                encoded_suits[2][0] += 1

            
            encoded_deck[card.ID][0] = 1
            
        return encoded_deck, encoded_suits
            