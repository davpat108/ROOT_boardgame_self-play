from deck import Deck, QuestDeck
from abc import ABC, abstractmethod

class Actor(ABC):

    def __init__(self) -> None:
        self.deck = Deck(empty=True)
        self.points = 0
        self.sappers = 0
        self.cobbler = 0
        self.tax_collector = 0

    @abstractmethod
    def get_options(self):
        pass

class Margquise(Actor):
    def __init__(self) -> None:
        super().__init__()
    
    def get_options_craft(self, map):
        # Daylight craft
        craft_suits = map.count_on_map(("building", "workshop"), per_suit=True)
                      
                      
        



class Eerie(Actor):
    def __init__(self) -> None:
        super().__init__()
    
    def get_options(self, map):
        return super().get_options()
    
class Alliance(Actor):
    def __init__(self) -> None:
        super().__init__()
        self.supporter_deck = Deck(empty = True)
    
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