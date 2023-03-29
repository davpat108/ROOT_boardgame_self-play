from deck import Deck, QuestDeck
from actions import Battle_DTO, CraftDTO, MoveDTO, OverworkDTO
from configs import buildings_list_marquise
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
                    battle_options.append(Battle_DTO(place.name, "bird"))
                if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                    battle_options.append(Battle_DTO(place.name, "alliance"))
                if place.vagabond_is_here and vagabond.relations['cat'] == 'hostile':
                    battle_options.append(Battle_DTO(place.name, "vagabond"))
        return battle_options
    
    def get_moves(self, map):
        "Returns a list of MoveDTO objects"
        moves = []
        for key in sorted(list(map.places.keys())): # sort places by key
            place = map.places[key]
            for i in range(place.soldiers['cat']):
                for neighbor in place.neighbors:
                    if place.owner == 'cat' or map.places[neighbor[0]].owner == 'cat':
                        if place.forest == False and map.places[neighbor[0]].forest == False:
                            moves.append(MoveDTO(place.name, map.places[neighbor[0]].name, how_many=i + 1))
        return moves    
    
    def get_can_recruit():
        return map.count_on_map(("building", "recruiter")) > 0
    
    def get_wood_tokens_to_build(self, map, place):
        """
        Finds all 'wood' tokens that are connected to a Place object on the map through multiple cat-owned Places.
        """
        if place.owner != 'cat':
            return 0
        
        connected_places = map.get_connected_places(place, 'cat')

        # Find all wood tokens on the connected places
        woods = 0
        for p in connected_places:
            for token in p.tokens:
                if token == 'wood':
                    woods += 1

        return woods
    
    def get_build_options(self, map):
        """
        Returns a dict of building options for the Marquise.
        """
        bulding_costs = [0, 1, 2, 3, 3, 4]
        building_options = {"sawmill": {"where" : [], "cost" : 9}, "workshop": {"where" : [], "cost" : 9}, "recruiter": {"where" : [], "cost" : 9}} # 9 is a placeholder for infinity

        for building in ["sawmill", "workshop", "recruiter"]:
            count = map.count_on_map(("building", building))
            if count == 6:
                continue
            cost = bulding_costs[count]
            for key in sorted(list(map.places.keys())):
                place = map.places[key]
                woods = self.get_wood_tokens_to_build(map, place)
                if place.owner == 'cat' and True in [slot[0] == "empty" for slot in place.building_slots]:
                    if not place.forest:
                        if woods >= cost:
                            building_options[building]["where"].append(place.name)
                            building_options[building]["cost"] = cost

        return building_options
    
    def get_overwork(self, map):
        """
        Returns a list of OverworkDTO objects.
        """
        overwork_clearings = []
        for key in sorted(list(map.places.keys())):
            place = map.places[key]
            for card in self.deck.cards:
                if place.owner == 'cat':
                    for slot in place.building_slots:
                        if slot[0] == 'sawmill' and (place.suit == card.card_suit or card.card_suit == 'bird'):
                            overwork_clearings.append(OverworkDTO(place.name, card.ID, card.card_suit))

        return overwork_clearings
    

class Eyrie(Actor):
    def __init__(self) -> None:
        super().__init__()
        self.items = []
        self.decree = {
            "recruit": [],
            "move": [],
            "battle": [],
            "build": [],
        }

    def get_options(self, map):
        return super().get_options()

    def get_decree_options(self):
        decree_options = {
            "recruit": [],
            "move": [],
            "battle": [],
            "build": [],
        }

        for card in self.deck.cards:
            for action in decree_options.keys():
                decree_options[action].append((card.ID, card.card_suit))

        return decree_options
    
    def get_resolve_recruit(self, map):
        recruit_options = []

        for card_ID, card_suit in  self.decree["recruit"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]

            total_bird_soldiers = sum([place.soldiers["bird"] for place in map.places.values()])
            if total_bird_soldiers < 20:
                for clearing in matching_clearings:
                    if True in [building[0] == 'roost' for building in clearing.building_slots]:
                        recruit_options.append((clearing.name, card_ID))

        return recruit_options

    def get_resolve_move(self, map):

        move_options = []
        for card_ID, card_suit in  self.decree["move"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]

            for source_clearing in matching_clearings:
                if source_clearing.soldiers["bird"] > 0:
                    for neighbor in source_clearing.neighbors:
                        if not neighbor[1]:
                            dest_clearing = map.places[neighbor[0]]
                            for soldiers in range(1, source_clearing.soldiers["bird"] + 1):
                                move_options.append(MoveDTO(source_clearing.name, dest_clearing.name, soldiers, card_ID))
        return move_options

    def get_resolve_battle(self, map, vagabond):
        battle_options = []

        for card_ID, card_suit in self.decree["battle"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]

            for clearing in matching_clearings:
                if clearing.soldiers["bird"] > 0:
                    if clearing.soldiers["cat"] > 0:
                        battle_options.append(Battle_DTO(clearing.name, "cat", card_ID))
                    if clearing.soldiers["alliance"] > 0:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID))
                    if clearing.vagabond_is_here and vagabond.relations['bird'] == 'hostile':
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID))

        return battle_options
    
    def get_resolve_building(self, map):
        building_option = []

        for card_ID, card_suit in self.decree["battle"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]

            for clearing in matching_clearings:
                if clearing.owner == 'bird':
                    if not True in [slot[0] == 'roost' for slot in clearing.building_slots] and True in [slot[0] == 'empty' for slot in clearing.building_slots] and not True in [token == 'keep' for token in clearing.tokens]:
                        building_option.append((clearing.name, card_ID))
                    

        return building_option

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