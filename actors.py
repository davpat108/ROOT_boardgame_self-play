from deck import Deck, QuestDeck

class Actor():

    def __init__(self) -> None:
        self.deck = Deck(empty=True)
        self.points = 0
        self.sappers = 0
        self.cobbler = 0
        self.tax_collector = 0
        self.ambush ={
            "rabbit": 0,
            "mouse": 0,
            "fox": 0,
            "bird": 0,
        }

    def get_options(self):
        pass

    def return_craft_options():
        #retuns a list of options
        pass
        
        
class Marquise(Actor):
    def __init__(self) -> None:
        super().__init__()
        self.items = []
    
    def get_options_craft(self, map):
        # Daylight craft
        craft_suits = map.count_on_map(("building", "workshop"), per_suit=True)
        craft_options = []
        for card in self.deck.cards:
            if card.craft_suit == "ambush":
                self.ambush[card.card_suit] += 1
            elif craft_suits[card.craft_suit] >= card.craft_cost:
                craft_options.append(card.craft)
            elif card.craft_suit == "anything":
                if sum(craft_suits.values()) > card.craft_cost:
                    craft_options.append(card.craft)
        return craft_options
                      
                      
class Eerie(Actor):
    def __init__(self) -> None:
        super().__init__()
        self.items = []
    
    def get_options(self, map):
        return super().get_options()
    
class Alliance(Actor):
    def __init__(self) -> None:
        super().__init__()
        self.supporter_deck = Deck(empty = True)
        self.items = []
    
    def get_options(self):
        return super().get_options()
    
class Vagabond(Actor):
    # First lets just make him thief
    def __init__(self, role = "Thief") -> None:
        super().__init__()
        self.quest_deck = QuestDeck(empty=True)
        if role == "Thief":
            self.satchel_fresh = ["sword", "torch", "boot"]
            self.satchel_exhausted = []
            self.satchel_damaged = []
            self.other_items_fresh = ["root_tea"]
            self.other_items_exhausted = []
            self.other_items_damaged = []
        else:
            raise NotImplementedError("Only thief yet")

    def get_options(self):
        return super().get_options()