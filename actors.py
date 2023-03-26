from deck import Deck, QuestDeck
from actions import Battle_DTO, CraftDTO#, Move, Quest
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
        craft_suits = map.count_on_map(("building", "workshop"), per_suit=True)
        craft_options = []
        for card in self.deck.cards:
            if card.craft_suit == "ambush":
                pass
            elif craft_suits[card.craft_suit] >= card.craft_cost:
                craft_options.append(CraftDTO(card.craft))
            elif card.craft_suit == "anything":
                if sum(craft_suits.values()) > card.craft_cost:
                    craft_options.append(CraftDTO(card.craft))
        return craft_options
    
    def get_ambushes(self):
        self.ambush ={
            "rabbit": 0,
            "mouse": 0,
            "fox": 0,
            "bird": 0,
        }
        for card in self.deck.cards:
            if card.craft_suit == "ambush":
                self.ambush[card.card_suit] += 1

    def get_battles(self, map, vagabond):
        battle_options = []
        for key in sorted(list(map.places.keys())):
            place = map.places[key]
            if place.soldiers['cat'] > 0:
                if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                    battle_options.append(Battle_DTO(place, "bird"))
                if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                    battle_options.append(Battle_DTO(place, "alliance"))
                if place.vagabond_is_here and vagabond.relations['cat'] == 'hostile':
                    battle_options.append(Battle_DTO(place, "vagabond"))
        return battle_options
    
    def get_moves(self, map):
        pass
                      
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
            self.relations = {
			"cat" : 'indifferent',
			"bird" : 'indifferent',
			"alliance" : 'indifferent'
		}

        else:
            raise NotImplementedError("Only thief yet")

    def get_options(self):
        return super().get_options()