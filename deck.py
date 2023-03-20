from random import shuffle

total_card_info = [[0, "rabbit", "command_warren", 2, "rabbit"],
               [1, "rabbit", "command_warren", 2, "rabbit"],
               [2, "rabbit", "sack", 1, "mouse"],
               [3, "rabbit", "money", 2, "rabbit"],
               [4, "rabbit", "favor", 3, "rabbit"],
               [5, "rabbit", "ambush", 0, "anything"],
               [6, "rabbit", "better_burrow_bank", 2, "rabbit"],
               [7, "rabbit", "better_burrow_bank", 2, "rabbit"],
               [8, "rabbit", "dominance", 10, "point"],
               [9, "rabbit", "cobbler", 2, "rabbit"],
               [10, "rabbit", "cobbler", 2, "rabbit"],
               [11, "rabbit", "boot", 1, "rabbit"],
               [12, "rabbit", "root_tea", 1, "mouse"],
               [13, "mouse", "crossbow", 1, "fox"],
               [14, "mouse", "sword", 2, "fox"],
               [15, "mouse", "scouting_party", 2, "mouse"],
               [16, "mouse", "scouting_party", 2, "mouse"],
               [17, "mouse", "codebreakers", 1, "mouse"],
               [18, "mouse", "codebreakers", 1, "mouse"],
               [19, "mouse", "money", 2, "rabbit"],
               [20, "mouse", "dominance", 10, "point"],
               [21, "mouse", "root_tea", 1, "mouse"],
               [22, "mouse", "favor", 3, "mouse"],
               [23, "mouse", "boot", 1, "rabbit"],
               [24, "mouse", "sack", 1, "mouse"],
               [25, "mouse", "ambush", 0, "anything"],
               [26, "fox", "anvil", 1, "fox"],
               [27, "fox", "stand_and_deliver", 3, "mouse"],
               [28, "fox", "stand_and_deliver", 3, "mouse"],
               [29, "fox", "tax_collector", 3, "all"],
               [30, "fox", "tax_collector", 3, "all"],
               [31, "fox", "tax_collector", 3, "all"],
               [32, "fox", "root_tea", 1, "mouse"],
               [33, "fox", "ambush", 0, "anything"],
               [34, "fox", "sword", 2, "fox"],
               [35, "fox", "sack", 1, "mouse"],
               [36, "fox", "dominance", 10, "point"],
               [37, "fox", "favor", 3, "fox"],
               [38, "fox", "money", 2, "rabbit"],
               [39, "fox", "boot", 1, "rabbit"],
               [40, "bird", "sack", 1, "mouse"],
               [41, "bird", "sappers", 1, "mouse"],
               [42, "bird", "sappers", 1, "mouse"],
               [43, "bird", "boot", 1, "rabbit"],
               [44, "bird", "brutal_tactics", 2, "fox"],
               [45, "bird", "brutal_tactics", 2, "fox"],
               [46, "bird", "dominance", 10, "point"],
               [47, "bird", "sword", 2, "fox" ],
               [48, "bird", "ambush", 0, "anything"],
               [49, "bird", "ambush", 0, "anything"],
               [50, "bird", "armorers", 1, "fox"],
               [51, "bird", "armorers", 1, "fox"],
               [52, "bird", "crossbow", 1, "fox"],
               [53, "bird", "royal_claim", 4, "anything"]]

class Card:
    def __init__(self, ID:int, suit: str, craft:str, needed_crafts:int, what_crafts:str):
        self.ID = ID
        self.suit = suit
        self.craft = craft
        self.needed_crafts = needed_crafts
        self.what_crafts = what_crafts
    
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
            for card_info in total_card_info:
                self.cards.append(Card(*card_info))
        
        else:
            # Init discard deck
            self.cards = []

        self.shuffle_deck()

    def get_the_card(self, ID):
        try:
            self.cards.remove(Card(*total_card_info[ID]))
            return Card(*total_card_info[ID])
        except:
            return("Card not in the deck")
    
    def draw_card(self):
        if len(self.cards) == 0:
            return "Deck Empty"
        return self.cards.pop(0)
    
    def add_card(self, card: Card):
        """
        Add a card to the end, mainly used for discard deck
        """
        self.cards.append(card)
    
    def shuffle_deck(self):
        shuffle(self.cards)