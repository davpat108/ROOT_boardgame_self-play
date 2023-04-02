from deck import Deck, QuestDeck
from actions import Battle_DTO, CraftDTO, MoveDTO, OverworkDTO
from configs import buildings_list_marquise
from itertools import combinations
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
                if place.vagabond_is_here:
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
                    if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "cat", card_ID))
                    if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID))
                    if clearing.vagabond_is_here:
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID))

        return battle_options
    
    def get_resolve_building(self, map):
        building_option = []

        for card_ID, card_suit in self.decree["battle"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]
            total_roosts = sum([True in [slot[0] == 'roost' for slot in place.building_slots] for place in map.places.values()])
            if total_roosts <7:
                for clearing in matching_clearings:
                    if clearing.owner == 'bird':
                        if not True in [slot[0] == 'roost' for slot in clearing.building_slots] and True in [slot[0] == 'empty' for slot in clearing.building_slots] and not True in [token == 'keep' for token in clearing.tokens]:
                            building_option.append((clearing.name, card_ID))
                    

        return building_option
    
    def get_no_roosts_left_options(self, map):
        building_option = []
        for place in map.places.values():
            if not True in [slot[0] == 'roost' for slot in place.building_slots]:
                if not True in [slot[0] == 'roost' for slot in place.building_slots] and True in [slot[0] == 'empty' for slot in place.building_slots] and not True in [token == 'keep' for token in place.tokens]:
                    building_option.append((place.name, 0))

        return building_option

    def get_options_craft(self, map):
        roost_counts = map.count_on_map(("building", "roost"), per_suit=True)
        craft_options = []
        for card in self.deck.cards:
            if card.craft_suit == "ambush":
                pass
            elif roost_counts[card.craft_suit] >= card.craft_cost:
                craft_options.append(CraftDTO(card.craft))
            elif card.craft_suit == "anything":
                if sum(roost_counts.values()) > card.craft_cost:
                    craft_options.append(CraftDTO(card.craft))
        return craft_options 


class Alliance(Actor):
    def __init__(self) -> None:
        super().__init__()
        self.supporter_deck = Deck(empty = True)
        self.items = []
        self.current_officers = 0
        self.total_officers = 0
    
    def refresh_officers(self):
        self.current_officers = self.total_officers

    def get_options(self):
        return super().get_options()
    
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

    def get_revolt_options(self, map):
        revolt_options = []

        # Iterate through the map to find suitable clearings for a revolt
        for key in sorted(list(map.places.keys())):
            place = map.places[key]

            if "sympathy" in place.tokens and not "keep" in place.tokens:
                suit = place.suit
                has_base = self.base_search(map, place.suit)

                if not has_base:
                    matching_cards = [card for card in self.supporter_deck.cards if card.card_suit == suit or card.card_suit == "bird"]
                    card_combinations = self.get_card_combinations(matching_cards, 2)

                    for combination in card_combinations:
                        revolt_options.append((place.name, combination[0].ID, combination[1].ID))

        return revolt_options

    def base_search(self, map, suit):
        for place in map.places.values():
            if place.suit == suit:
                for slot in place.building_slots:
                    if slot[0] == 'base':
                        return True
        return False

    def get_card_combinations(self, cards, num_cards):
        if num_cards == 0:
            return [[]]

        if not cards:
            return []

        card = cards[0]
        remaining_cards = cards[1:]

        with_card = [[card] + combination for combination in self.get_card_combinations(remaining_cards, num_cards - 1)]
        without_card = self.get_card_combinations(remaining_cards, num_cards)

        return with_card + without_card
    

    def get_spread_sympathy_options(self, map):
        spread_sympathy_options = []
        sympathies_on_map = sum(place.tokens.count("sympathy") for place in map.places.values())
        if sympathies_on_map > 9:
            return spread_sympathy_options
        
        if sympathies_on_map == 0:
            cost = 0
            for key in sorted(list(map.places.keys())):
                place = map.places[key]
                if "keep" not in place.tokens and place.forest == False:
                    matching_cards = [card for card in self.supporter_deck.cards if card.card_suit == place.suit or card.card_suit == "bird"]
                    other_faction_soldiers = sum(soldiers for faction, soldiers in place.soldiers.items() if faction != "alliance")
                    if other_faction_soldiers >= 3:
                        cost += 1
                    card_combinations = self.get_card_combinations(matching_cards, cost)
                    for combination in card_combinations:
                        card_ids = [card.ID for card in combination]
                        spread_sympathy_options.append((place.name, card_ids))

        else:
            sympathy_clearings = [place for place in map.places.values() if "sympathy" in place.tokens]
            adjacent_clearings = set()

            for clearing in sympathy_clearings:
                for neighbor in clearing.neighbors:
                    adjacent_clearings.update(neighbor[0])

            for clearing_name in adjacent_clearings:
                target_clearing = map.places[clearing_name]
                if "sympathy" not in target_clearing.tokens and "keep" not in target_clearing.tokens and target_clearing.forest == False:
                    clearing_suit = target_clearing.suit
                    matching_cards = [card for card in self.supporter_deck.cards if card.card_suit == clearing_suit or card.card_suit == "bird"]

                    if sympathies_on_map <= 2:
                        cost = 1
                    elif sympathies_on_map <= 5:
                        cost = 2
                    else:
                        cost = 3

                    other_faction_soldiers = sum(soldiers for faction, soldiers in target_clearing.soldiers.items() if faction != "alliance")
                    if other_faction_soldiers >= 3:
                        cost += 1

                    card_combinations = self.get_card_combinations(matching_cards, cost)
                    for combination in card_combinations:
                        card_ids = [card.ID for card in combination]
                        spread_sympathy_options.append((target_clearing.name, card_ids))

        return spread_sympathy_options
    
    def get_options_craft(self, map):
        sympathy_counts = map.count_on_map(("token", "sympathy"), per_suit=True)
        craft_options = []
        for card in self.deck.cards:
            if card.craft_suit == "ambush":
                pass
            elif sympathy_counts[card.craft_suit] >= card.craft_cost:
                craft_options.append(CraftDTO(card.craft))
            elif card.craft_suit == "anything":
                if sum(sympathy_counts.values()) > card.craft_cost:
                    craft_options.append(CraftDTO(card.craft))
        return craft_options
    
    def get_mobilize_options(self):
        return [card.ID for card in self.deck.cards]
    
    def get_train_options(self, map):
        base_suits = set()
        train_options = []

        for place in map.places.values():
            if ("base", "alliance") in place.building_slots:
                base_suits.add(place.suit)

        for card in self.deck.cards:
            if card.card_suit in base_suits or card.card_suit == "bird":
                train_options.append(card.ID)

        return list(set(train_options))
    
    def get_battles(self, map, vagabond):
        battle_options = []
        if self.current_officers == 0:
            return battle_options
        for key in sorted(list(map.places.keys())):
            place = map.places[key]
            if place.soldiers['alliance'] > 0:
                if place.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in place.building_slots]or 'keep' in place.tokens or 'wood' in place.tokens:
                    battle_options.append(Battle_DTO(place.name, "cat"))
                if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                    battle_options.append(Battle_DTO(place.name, "bird"))
                if place.vagabond_is_here:
                    battle_options.append(Battle_DTO(place.name, "vagabond"))
        return battle_options
    
    def get_moves(self, map):
        "Returns a list of MoveDTO objects"
        moves = []
        if self.current_officers == 0:
            return moves
        for key in sorted(list(map.places.keys())): # sort places by key
            place = map.places[key]
            for i in range(place.soldiers['alliance']):
                for neighbor in place.neighbors:
                    if place.owner == 'alliance' or map.places[neighbor[0]].owner == 'alliance':
                        if place.forest == False and map.places[neighbor[0]].forest == False:
                            moves.append(MoveDTO(place.name, map.places[neighbor[0]].name, how_many=i + 1))
        return moves

    def get_recruits(self, map):
        if self.current_officers == 0:
            return []
        recruit_options = []
        for place in map.places.values():
            if True in [slot[0]=='base' for slot in place.building_slots]:
                recruit_options.append(place.name)
        return recruit_options   

    def get_organize_options(self, map):
        organize_options = []
        if self.current_officers == 0:
            return organize_options
        
        for place in map.places.values():
            if place.soldiers['alliance']>0 and not 'sympathy' in place.tokens:
                organize_options.append(place.name)

        return organize_options
    

class Item():
    def __init__(self, name, exhausted=False, damaged=False) -> None:
        self.name = name
        self.check_names()
        self.exhausted = False
        self.damaged = False

    def __eq__(self, other) -> bool:
        if self.name == other.name:
            return True
        return False

    def __repr__(self):
        return self.name


    def check_names(self):
        if not self.name in ["sack", "money", "boot", "sword", "crossbow", "torch", "root_tea", "hammer"]:
            raise ValueError("Item name not valid")

class Vagabond(Actor):
    # First lets just make him thief
    def __init__(self, role = "Thief") -> None:
        super().__init__()
        self.quest_deck = QuestDeck(empty=True)
        self.role = role
        if self.role == "Thief":
            self.satchel = [Item("sword"), Item("torch"), Item("boot")]
            self.other_items = [Item("root_tea")]
            self.relations = {
			"cat" : 'indifferent',
			"bird" : 'indifferent',
			"alliance" : 'indifferent'
		}

        else:
            raise NotImplementedError("Only thief yet")

    def chack_relation_status(self):
        for status in self.relations.values():
            if not status in ['indifferent', 'hostile', 'good', 'very good', 'friendly']:
                return True

    def get_options(self):
        return super().get_options()
    
    def get_slip_options(self, map):
        slip_options = []
        for neighbor in map.places[map.vagabond_position].neighbors:
            slip_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, 0))
        return slip_options
    
    def get_moves(self, map):
        move_options = []
        for neighbor in map.places[map.vagabond_position].neighbors:
            if not neighbor[1]:
                if self.relations[ map.places[neighbor[0]].owner ] == 'hostile':
                    boot_cost = 2
                else:
                    boot_cost = 1
                if [item for item in self.satchel if item.exhausted == False and item.damaged == False].count(Item("boot")) >= boot_cost:
                    move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=0))
        return move_options
    

    def get_refresh_options(self):
        item_num = self.other_items.count(Item("root_tea"))*2 + 3
        all_items = self.satchel + self.other_items
        exhausted_items = [item for item in all_items if item.exhausted]
        return list(combinations(exhausted_items, min(item_num, len(exhausted_items))))

    def get_repair_options(self):
        hammer_avaible = any(item for item in self.satchel if item.name == "hammer" and not item.damaged and not item.exhausted)
        all_items = self.satchel + self.other_items
        damaged_items = [item for item in all_items if item.damaged]
        if hammer_avaible:
            return damaged_items
        else:
            return []
    
    def get_battle_options(self, map):
        battle_options = []
        if any(item for item in self.satchel if item.name == "sword" and not item.damaged and not item.exhausted):
            for army in map.places[map.vagabond_position].soldiers:
                if map.places[map.vagabond_position].soldiers[army] > 0:
                    battle_options.append(Battle_DTO(map.vagabond_position, army))
        return battle_options

    def has_items(self, item1, item2):
        all_items = self.satchel + self.other_items
        if item1 == item2:
            count = sum(1 for item in all_items if item.name == item1.name and not item.damaged and not item.exhausted)
            return count >= 2
        else:
            found_item1 = False
            found_item2 = False
            for item in self.satchel:
                if not item.damaged and not item.exhausted:
                    if item.name == item1.name:
                        found_item1 = True
                    elif item.name == item2.name:
                        found_item2 = True
                if found_item1 and found_item2:
                    return True
        return False
    

    def get_quest_options(self, map):
        quest_options = []
        current_clearing = map.places[map.vagabond_position]

        for quest_card in self.quest_deck.cards:
            if (quest_card.suit == current_clearing.suit and
                    self.has_items(Item(quest_card.item1), Item(quest_card.item2))):
                quest_options.append(quest_card.ID)

        return quest_options

    def has_non_exhausted_item(self, searched_item):
        for item in self.satchel + self.other_items:
            if item.name == searched_item.name and not item.exhausted and not item.damaged:
                return True
        return False

    def get_thief_ability(self, map):
        if not self.has_non_exhausted_item(Item('torch')):
            return []

        thief_ability_options = []
        current_clearing = map.places[map.vagabond_position]

        if current_clearing.soldiers['bird'] > 0 or True in [slot[0] == 'roost' for slot in current_clearing.building_slots]:
            thief_ability_options.append((current_clearing.name, 'bird'))
        if current_clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in current_clearing.building_slots]or 'keep' in current_clearing.tokens or 'wood' in current_clearing.tokens:
            thief_ability_options.append((current_clearing.name, 'cat'))
        if current_clearing.soldiers['alliance'] > 0 or True in [slot[0] == 'base' for slot in current_clearing.building_slots] or "sympathy" in current_clearing.tokens:
            thief_ability_options.append((current_clearing.name, 'alliance'))

        return thief_ability_options
        
    def get_ruin_explore_options(self, map):
        if not self.has_non_exhausted_item(Item('torch')):
            return False

        current_clearing = map.places[map.vagabond_position]
        has_ruin = any(slot[0] == 'ruin' for slot in current_clearing.building_slots)

        return has_ruin

    def get_strike_options(self, map):
        if not self.has_non_exhausted_item(Item("crossbow")):
            return []

        strike_options = []
        current_clearing = map.places[map.vagabond_position]

        for opponent in ['cat', 'bird', 'alliance']:
            if current_clearing.soldiers[opponent] > 0:
                strike_options.append((current_clearing.name, opponent, 'soldier'))
            if opponent=="alliance" and 'sympathy' in current_clearing.tokens:
                strike_options.append((current_clearing.name, opponent, 'sympathy'))
            if opponent=="cat" and 'keep' in current_clearing.tokens:
                strike_options.append((current_clearing.name, opponent, 'keep'))
            if opponent=="cat" and 'wood' in current_clearing.tokens:
                strike_options.append((current_clearing.name, opponent, 'wood'))
            for slot in current_clearing.building_slots:
                if slot[1]==opponent:
                    strike_options.append((current_clearing.name, opponent, slot[0]))
            
        return strike_options

    def get_aid_options(self, map, *opponents):
        aid_options = []
        current_clearing = map.places[map.vagabond_position]
        # Iterates through name
        for opponent in ['cat', 'bird', 'alliance']:
            if current_clearing.has_opponent_pieces(opponent):
                relation = self.relations[opponent]
                if relation == 'hostile':
                    continue

                if relation == 'indifferent':
                    cost = 1
                elif relation == 'good':
                    cost = 2
                else:  # friendly or very good
                    cost = 3

                item_choices = []  # Get items from the opponent
                for item in opponents.items: #Iterates through opponent objects from arquments
                    if not item.exhausted and not item.damaged:
                        item_choices.append(Item(item.name))

                if item_choices:
                    for item in item_choices:
                        aid_options.append((current_clearing.name, opponent, cost, item))
                else:
                    aid_options.append((current_clearing.name, opponent, cost, None))

        return aid_options

    def damage_item(self, other_item):
        for item in self.satchel:
            if item.name == other_item.name:
                item.damaged = True
                return
        for item in self.other_items:
            if item.name == other_item.name:
                item.damaged = True
                return
        raise ValueError("Item not found")

    def add_item(self, item):
        if item.name in ['sword', 'crossbow', 'hammer', 'boot', 'torch']:
            self.satchel.append(item)
        else:
            self.other_items.append(item)

    def exhaust_item(self, other_item):
        for item in self.satchel:
            if item.name == other_item.name:
                item.exhausted = True
                return
        for item in self.other_items:
            if item.name == other_item.name:
                item.exhausted = True
                return
        raise ValueError("Item not found")

    def repair_item(self, other_item):
        for item in self.satchel:
            if item.name == other_item.name:
                item.damaged = False
                return
        for item in self.other_items:
            if item.name == other_item:
                item.damaged = False
                return
        raise ValueError("Item not found")
    
    def refresh_item(self, other_item):
        for item in self.satchel:
            if item.name == other_item.name:
                item.exhausted = False
                return
        for item in self.other_items:
            if item.name == other_item.name:
                item.exhausted = False
                return
        raise ValueError("Item not found")
    
    def repair_and_refresh_all(self):
        for item in self.satchel:
            item.damaged = False
            item.exhausted = False
        for item in self.other_items:
            item.damaged = False
            item.exhausted = False