from deck import Deck, QuestDeck
from dtos import Battle_DTO, CraftDTO, MoveDTO, OverworkDTO
from configs import buildings_list_marquise, Immediate_non_item_effects, persistent_effects, eyrie_leader_config
from itertools import combinations
from item import Item
import random
class Actor():

    def __init__(self, map) -> None:
        self.deck = Deck(empty=True)
        self.sappers = False
        self.cobbler = False
        self.tax_collector = False
        self.armorers = False
        self.sappers = False
        self.command_warren = False
        self.scouting_party = False
        self.codebreakers = False
        self.stand_and_deliver = False
        self.better_burrow_bank = False
        self.royal_claim = False
        self.brutal_tactics = False
        self.known_hands = {
            'cat': False,
            'bird': False,
            'alliance': False,
            'vagabond': False
        }
        self.victory_points = 0
        self.craft_activations = {
            "rabbit": 0,
            "mouse": 0,
            "fox": 0
        }
        self.win_condition = "points" #None, rabbit, mouse, fox, bird, coalition
        self.refresh_craft_activations(map)
        self.card_prios = []
    
    def __lt__(self, other):
        return self.name < other.name

    def add_item(self, item):
        self.items.append(item)

    def codebreakers_options(self, actors):
        if not self.codebreakers:
            return
        options = []
        for actor in actors:
            if actor != self:
                options.append(actor.name)
        return options

    def deactivate(self, cost):
        for suit, amount in cost.items():
            self.craft_activations[suit] -= amount

    def get_card_options(self):
        card_ids = [card.ID for card in self.deck.cards]
        return card_ids

    def stand_and_deliver_options(self, actors):
        if not self.stand_and_deliver:
            return
        options = ['No one'] # Maybe you can take from supporter deck but its not implemented
        for actor in actors:
            if actor != self and len(actor.deck.cards) > 0:
                options.append(actor)
        return options

    def bbb_options(self, actors):
        if not self.better_burrow_bank:
            return
        options = []
        for actor in actors:
            if actor != self:
                options.append(actor)
        return options

    def discard_down_to_five_options(self):
        if len(self.deck.cards) <= 5:
            return
        card_IDs = []
        retlist = []
        for card in self.deck.cards:
            card_IDs.append(card.ID)

        for combination in list(combinations(card_IDs, len(card_IDs)-5)):
            retlist.append(list(combination))
        return retlist
    
    def get_cards_by_suit_options(self, suit):
        matching_cards = []
        for card in self.deck:
            if card.suit == suit:
                matching_cards.append(card)
        return matching_cards
        
    def card_to_give_to_alliace_options(self, suit):
        options = []
        for card in self.deck.cards:
            if card.card_suit == suit or card.card_suit == "bird":
                options.append(card.ID)
        return options

    def get_sappers_options(self):
        if not self.sappers:
            return
        return [True, False]
    
    def get_ambush_options(self, place):
        options = [False]
        for card in self.deck.cards:
            if card.craft == "ambush" and card.card_suit == place.suit and "suit" not in options:
                options.append("suit")
            if card.craft == "ambush" and card.card_suit == 'bird' and "bird" not in options:
                options.append("bird")
        return options
    
    def get_royal_claim_options(self):
        if not self.royal_claim:
            return
        return [True, False]

    def get_tax_collector_options(self, map):
        # Gets all places with soldiers on the map
        if not self.tax_collector:
            return
        options = []
        for place in map.places.values():
            if place.soldiers[self.name] > 0:
                options.append(place.name)
        return options
    


class Marquise(Actor):
    def __init__(self, map) -> None:
        super().__init__(map)
        self.items = []
        self.name = 'cat'
    
    def refresh_craft_activations(self, map):
        self.craft_activations = map.count_on_map(("building", "workshop"), per_suit=True)

    def pieces_to_lose_in_battle(self):
        chosen_pieces = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
        random.shuffle(chosen_pieces)
        return chosen_pieces

    def count_for_card_draw(self, map):
        draws = 1
        recruiter_count = map.count_on_map(("building", "recruiter"))
        if recruiter_count > 2:
            draws += 1
        if recruiter_count > 4:
            draws += 1
        return draws

    def get_options_craft(self, map):
        craft_options = []
        for card in self.deck.cards:
            if card.craft in Immediate_non_item_effects or card.craft in map.craftables or card.craft in persistent_effects:
                if card.craft_suit == "ambush":
                    pass
                elif card.craft_suit == "anything":
                    if sum(self.craft_activations.values()) >= card.craft_cost:
                        craft_options.append(CraftDTO(card))
                elif card.craft_suit == "all":
                    if self.craft_activations["fox"] >= 1 and self.craft_activations["rabbit"] >= 1 and self.craft_activations["mouse"] >= 1:
                        craft_options.append(CraftDTO(card))
                elif card.craft_suit == "dominance" and self.victory_points >= 10 and self.win_condition == "points":
                    craft_options.append(CraftDTO(card))
                elif self.craft_activations[card.craft_suit] >= card.craft_cost:
                    craft_options.append(CraftDTO(card))
        return craft_options
    
    def get_battles(self, map):
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
                if self.armorers:
                    if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                        battle_options.append(Battle_DTO(place.name, "bird", armorer_usage=True))
                    if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                        battle_options.append(Battle_DTO(place.name, "alliance", armorer_usage=True))
                    if place.vagabond_is_here:
                        battle_options.append(Battle_DTO(place.name, "vagabond", armorer_usage=True))
                if self.brutal_tactics:
                    if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                        battle_options.append(Battle_DTO(place.name, "bird", brutal_tactics_usage=True))
                    if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                        battle_options.append(Battle_DTO(place.name, "alliance", brutal_tactics_usage=True))
                    if place.vagabond_is_here:
                        battle_options.append(Battle_DTO(place.name, "vagabond", brutal_tactics_usage=True))
                if self.brutal_tactics and self.armorers:
                    if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                        battle_options.append(Battle_DTO(place.name, "bird", brutal_tactics_usage=True, armorer_usage=True))
                    if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                        battle_options.append(Battle_DTO(place.name, "alliance", brutal_tactics_usage=True, armorer_usage=True))
                    if place.vagabond_is_here:
                        battle_options.append(Battle_DTO(place.name, "vagabond", brutal_tactics_usage=True, armorer_usage=True))
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
                            moves.append(MoveDTO(place.name, map.places[neighbor[0]].name, who='cat', how_many=i + 1))
        return moves    
    
    def get_can_recruit(self, map):
        if sum([place.soldiers["cat"] for place in map.places.values()]) >= 25:
            return (False, 'recruit')
        return (map.count_on_map(("building", "recruiter")) > 0, 'recruit')
    
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
        building_options = []

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
                            building_options.append((place.name, building, cost))

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
                            overwork_clearings.append(OverworkDTO(place.name, card.ID))

        return overwork_clearings
    
    def get_use_bird_card_to_gain_moves(self):
        options = [False]
        for card in self.deck.cards:
            if card.card_suit == 'bird':
                options.append(card.ID)
        return options

class Eyrie(Actor):
    def __init__(self, map, role) -> None:
        super().__init__(map)
        self.items = []
        self.leader = role
        self.avaible_leaders = ["Despot", "Commander", "Builder", "Charismatic"]
        self.check_role()
        self.name = 'bird'
        self.setup_based_on_leader()
        self.decree_deck = Deck(empty=True)
        self.temp_decree = {
            "recruit": [],
            "move": [],
            "battle": [],
            "build": [],
        } # Remove cards from this decree while resolving

    def pieces_to_lose_in_battle(self):
        return ['roost']

    def check_role(self):
        if self.leader in self.avaible_leaders:
            self.avaible_leaders.remove(self.leader)
            return
        else:
            raise ValueError("Invalid role for Eyrie")

    def change_role(self, role):
        self.leader = role
        self.check_role()


    def count_for_card_draw(self, map):
        draws = 1
        recruiter_count = map.count_on_map(("building", "roost"))
        if recruiter_count > 2:
            draws += 1
        if recruiter_count > 5:
            draws += 1
        return draws

    def setup_based_on_leader(self):
        new_loyal_viziers = eyrie_leader_config[self.leader]
        self.decree = {
            "recruit": [],
            "move": [],
            "battle": [],
            "build": [],
        }
        for action in self.decree.keys():
            if action in new_loyal_viziers:
                self.decree[action] += [(-1, "bird")]

    def get_turmoil_options(self):
        return self.avaible_leaders

    def get_decree_options(self):
        actions = ["recruit", "move", "battle", "build"]
        options = []

        for card in self.deck.cards:
            for action in actions:
                options.append((action, card.ID, card.card_suit))

        return options
    
    def remove_from_temp_decree(self, card_ID, action):
        self.temp_decree[action] = [(ID, suit) for ID, suit in self.temp_decree[action] if ID != card_ID]


    def refresh_temp_decree(self):
        self.temp_decree = self.decree

    def get_resolve_recruit(self, map):
        recruit_options = []

        for card_ID, card_suit in self.temp_decree["recruit"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]

            total_bird_soldiers = sum([place.soldiers["bird"] for place in map.places.values()])
            if self.leader != "Charismatic" and total_bird_soldiers < 20:
                for clearing in matching_clearings:
                    if True in [building[0] == 'roost' for building in clearing.building_slots]:
                        recruit_options.append((clearing, card_ID))
            if self.leader == "Charismatic" and total_bird_soldiers < 19:
                for clearing in matching_clearings:
                    if True in [building[0] == 'roost' for building in clearing.building_slots]:
                        recruit_options.append((clearing, card_ID))

        return recruit_options

    def get_resolve_move(self, map):

        move_options = []
        for card_ID, card_suit in  self.temp_decree["move"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]

            for source_clearing in matching_clearings:
                if source_clearing.soldiers["bird"] > 0:
                    for neighbor in source_clearing.neighbors:
                        if not neighbor[1]:
                            dest_clearing = map.places[neighbor[0]]
                            for soldiers in range(1, source_clearing.soldiers["bird"] + 1):
                                move_options.append(MoveDTO(source_clearing.name, dest_clearing.name, how_many=soldiers,card_ID=card_ID, who="bird"))
        return move_options

    def get_resolve_battle(self, map):
        battle_options = []

        for card_ID, card_suit in self.temp_decree["battle"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]

            for clearing in matching_clearings:
                if clearing.soldiers["bird"] > 0:
                    if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "cat", card_ID))
                    if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID))
                    if clearing.vagabond_is_here:
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID))
                    if self.armorers:
                        if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                            battle_options.append(Battle_DTO(clearing.name, "cat", card_ID, armorer_usage=True))
                        if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                            battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID, armorer_usage=True))
                        if clearing.vagabond_is_here:
                            battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID, armorer_usage=True))
                    if self.brutal_tactics:
                        if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                            battle_options.append(Battle_DTO(clearing.name, "cat", card_ID, brutal_tactics_usage=True))
                        if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                            battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID, brutal_tactics_usage=True))
                        if clearing.vagabond_is_here:
                            battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID, brutal_tactics_usage=True))
                    if self.brutal_tactics and self.armorers:
                        if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                            battle_options.append(Battle_DTO(clearing.name, "cat", card_ID, brutal_tactics_usage=True, armorer_usage=True))
                        if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                            battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID, brutal_tactics_usage=True, armorer_usage=True))
                        if clearing.vagabond_is_here:
                            battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID, brutal_tactics_usage=True, armorer_usage=True))

        return battle_options
    
    def get_resolve_building(self, map):
        building_option = []

        for card_ID, card_suit in self.temp_decree["build"]:
            matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]
            total_roosts = sum([True in [slot[0] == 'roost' for slot in place.building_slots] for place in map.places.values()])
            if total_roosts <7:
                for clearing in matching_clearings:
                    if clearing.owner == 'bird':
                        if not True in [slot[0] == 'roost' for slot in clearing.building_slots] and True in [slot[0] == 'empty' for slot in clearing.building_slots] and not True in [token == 'keep' for token in clearing.tokens]:
                            building_option.append((clearing.name, card_ID))
                    

        return building_option
    
    def get_no_roosts_left_options(self, map): 
        for place in map.places.values():
            if True in [slot[0] == 'roost' for slot in place.building_slots]:
                return []
        
        min_soldiers_clearing = []
        min_soldiers = 100
        for place in map.places.values():
            if sum(place.soldiers.values()) == min_soldiers and not 'keep' in place.tokens and not place.forest and ('empty', 'No one') in place.building_slots:
                min_soldiers = sum(place.soldiers.values())
                min_soldiers_clearing.append(place.name)
            if sum(place.soldiers.values()) < min_soldiers and not 'keep' in place.tokens and not place.forest and ('empty', 'No one') in place.building_slots:
                min_soldiers_clearing = []
                min_soldiers = sum(place.soldiers.values())
                min_soldiers_clearing.append(place.name)
            
                
        return min_soldiers_clearing

    def refresh_craft_activations(self, map):
        self.craft_activations = map.count_on_map(("building", "roost"), per_suit=True)

    def get_options_craft(self, map):
        craft_options = []
        for card in self.deck.cards:
            if card.craft in Immediate_non_item_effects or card.craft in map.craftables or card.craft in persistent_effects:
                if card.craft_suit == "ambush":
                    pass
                elif self.craft_activations[card.craft_suit] >= card.craft_cost:
                    craft_options.append(CraftDTO(card))
                elif card.craft_suit == "anything":
                    if sum(self.craft_activations.values()) >= card.craft_cost:
                        craft_options.append(CraftDTO(card))
                elif card.craft_suit == "all":
                    if self.craft_activations["fox"] >= 1 and self.craft_activations["rabbit"] >= 1 and self.craft_activations["mouse"] >= 1:
                        craft_options.append(CraftDTO(card))
                elif card.craft_suit == "dominance" and self.victory_points >= 10 and self.win_condition == "points":
                    craft_options.append(CraftDTO(card))
        return craft_options 


class Alliance(Actor):
    def __init__(self, map) -> None:
        super().__init__(map)
        self.supporter_deck = Deck(empty = True)
        self.items = []
        self.current_officers = 0
        self.total_officers = 0
        self.name = "alliance"
    
    def pieces_to_lose_in_battle(self):
        return ['sympathy', 'base']

    def take_card_from_a_player_options(self, player):
        self.known_hands[player.name] = True
        return [card.ID for card in player.deck.cards]

    def count_for_card_draw(self, map):
        draws = map.count_on_map(("building", "base")) + 1
        return draws

    def refresh_officers(self):
        self.current_officers = self.total_officers

    def get_options(self):
        return super().get_options()
    
    def discard_down_to_five_supporters_options(self, map):
        if map.count_on_map(("building", "base")) == 0:
            if len(self.supporter_deck.cards) <= 5:
                return
            card_IDs = []
            retlist = []
            for card in self.supporter_deck.cards:
                card_IDs.append(card.ID)

            for combination in list(combinations(card_IDs, len(card_IDs)-5)):
                retlist.append(list(combination))
            return retlist
        return


    def get_revolt_options(self, map):
        revolt_options = []

        # Iterate through the map to find suitable clearings for a revolt
        for key in sorted(list(map.places.keys())):
            place = map.places[key]

            if "sympathy" in place.tokens and not "keep" in place.tokens:
                suit = place.suit
                has_base = self.base_search(map, place.suit)

                if not has_base:
                    soldiers_to_gain = map.count_on_map(("token", "sympathy"), per_suit=True)[suit]
                    matching_cards = [card for card in self.supporter_deck.cards if card.card_suit == suit or card.card_suit == "bird"]
                    card_combinations = self.get_card_combinations(matching_cards, 2)

                    for combination in card_combinations:
                        revolt_options.append((place, combination[0].ID, combination[1].ID, soldiers_to_gain))

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
    
    def refresh_craft_activations(self, map):
        self.craft_activations = map.count_on_map(("token", "sympathy"), per_suit=True)

    def get_options_craft(self, map):
        craft_options = []
        for card in self.deck.cards:
            if card.craft in Immediate_non_item_effects or card.craft in map.craftables or card.craft in persistent_effects:
                if card.craft_suit == "ambush":
                    pass
                elif card.craft_suit == "anything":
                    if sum(self.craft_activations.values()) >= card.craft_cost:
                        craft_options.append(CraftDTO(card))
                elif card.craft_suit == "all":
                    if self.craft_activations["fox"] >= 1 and self.craft_activations["rabbit"] >= 1 and self.craft_activations["mouse"] >= 1:
                        craft_options.append(CraftDTO(card))
                elif card.craft_suit == "dominance" and self.victory_points >= 10 and self.win_condition == "points":
                    craft_options.append(CraftDTO(card))
                elif self.craft_activations[card.craft_suit] >= card.craft_cost:
                   craft_options.append(CraftDTO(card))
        return craft_options
    
    def get_mobilize_options(self):
        return [card.ID for card in self.deck.cards]
    
    def get_train_options(self, map):
        base_suits = set()
        train_options = []
        if sum([place.soldiers["alliance"] for place in map.places.values()]) + self.total_officers >= 10:
            return train_options
        for place in map.places.values():
            if ("base", "alliance") in place.building_slots:
                base_suits.add(place.suit)

        for card in self.deck.cards:
            if card.card_suit in base_suits or card.card_suit == "bird":
                train_options.append((card.ID, "train"))

        return list(set(train_options))
    
    def get_battles(self, map):
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
                if self.armorers:
                    if place.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in place.building_slots]or 'keep' in place.tokens or 'wood' in place.tokens:
                        battle_options.append(Battle_DTO(place.name, "cat", armorer_usage=True))
                    if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                        battle_options.append(Battle_DTO(place.name, "bird", armorer_usage=True))
                    if place.vagabond_is_here:
                        battle_options.append(Battle_DTO(place.name, "vagabond", armorer_usage=True))
                if self.brutal_tactics:
                    if place.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in place.building_slots]or 'keep' in place.tokens or 'wood' in place.tokens:
                        battle_options.append(Battle_DTO(place.name, "cat", brutal_tactics_usage=True))
                    if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                        battle_options.append(Battle_DTO(place.name, "bird", brutal_tactics_usage=True))
                    if place.vagabond_is_here:
                        battle_options.append(Battle_DTO(place.name, "vagabond", brutal_tactics_usage=True))
                if self.armorers and self.brutal_tactics:
                    if place.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in place.building_slots]or 'keep' in place.tokens or 'wood' in place.tokens:
                        battle_options.append(Battle_DTO(place.name, "cat", armorer_usage=True, brutal_tactics_usage=True))
                    if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                        battle_options.append(Battle_DTO(place.name, "bird", armorer_usage=True, brutal_tactics_usage=True))
                    if place.vagabond_is_here:
                        battle_options.append(Battle_DTO(place.name, "vagabond", armorer_usage=True, brutal_tactics_usage=True))
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
                            moves.append(MoveDTO(place.name, map.places[neighbor[0]].name, how_many=i + 1, who='alliance'))
        return moves

    def get_recruits(self, map):
        if self.current_officers == 0:
            return []
        recruit_options = []
        if sum([place.soldiers["alliance"] for place in map.places.values()]) + self.total_officers >= 10:
            return []
        for place in map.places.values():
            if True in [slot[0]=='base' for slot in place.building_slots]:
                recruit_options.append((place.name, "recruit"))
        return recruit_options   

    def get_organize_options(self, map):
        organize_options = []
        if self.current_officers == 0:
            return organize_options
        
        for place in map.places.values():
            if place.soldiers['alliance']>0 and not 'sympathy' in place.tokens:
                organize_options.append((place.name, "organize"))

        return organize_options
    

class Vagabond(Actor):
    def __init__(self, map, role = "Thief") -> None:
        super().__init__(map)
        self.quest_deck = QuestDeck(empty=True)
        self.role = role
        self.name = "vagabond"
        self.allied_soldiers = [] # list of playernames
        if self.role == "Thief":
            self.satchel = [Item("sword"), Item("torch"), Item("boot")]
            self.other_items = [Item("root_tea")]
            self.relations = {
			"cat" : 'indifferent',
			"bird" : 'indifferent',
			"alliance" : 'indifferent'
		}
            self.refresh_items_to_damage()
        else:
            raise NotImplementedError("Only thief yet")

    def refresh_craft_activations(self, map):
        pass

    def refresh_items_to_damage(self): # TODO NEEDS to be written properly after debug
        self.items_to_damage = [Item('root_tea'), Item('torch'), Item('boot'), Item('sword')]

    def chack_relation_status_correct(self):
        for status in self.relations.values():
            if not status in ['indifferent', 'hostile', 'good', 'very good', 'friendly']:
                return True

    def get_options(self):
        return super().get_options()

    def get_options_craft(self, map):
        craft_options = []
        activations = 0
        for item in self.satchel + self.other_items:
            if item.name == "hammer" and not item.exhausted and not item.damaged:
                activations += 1
        for card in self.deck.cards:
            if card.craft in Immediate_non_item_effects or card.craft in map.craftables or card.craft in persistent_effects: 
                if card.craft_suit == "ambush":
                    pass
                elif activations >= card.craft_cost:
                    craft_options.append(CraftDTO(card))
                elif card.craft_suit == "anything":
                    pass
                elif card.craft_suit == "all" and activations >= 3:
                    craft_options.append(CraftDTO(card))
                elif card.craft_suit == "dominance" and self.victory_points >= 10 and self.win_condition == "points":
                    craft_options.append(CraftDTO(card))
        return craft_options        

    def get_slip_options(self, map):
        slip_options = []
        for neighbor in map.places[map.vagabond_position].neighbors:
            slip_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, 0, who='vagabond'))
        return slip_options
    
    def get_moves(self, map):
        move_options = []
        for neighbor in map.places[map.vagabond_position].neighbors:
            if not neighbor[1]:
                if self.relations[map.places[neighbor[0]].owner] == 'hostile':
                    boot_cost = 2
                else:
                    boot_cost = 1
                if [item for item in self.satchel if item.exhausted == False and item.damaged == False].count(Item("boot")) >= boot_cost:
                    move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=0, who='vagabond'))
                    if self.relations['cat'] == 'friendly' and map.places[map.vagabond_position].soldiers['cat'] > 0:
                        for i in range(map.places[map.vagabond_position].soldiers['cat']):
                            move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=1, who='vagabond', vagabond_allies=(i+1, 'cat')))
                    if self.relations['bird'] == 'friendly' and map.places[map.vagabond_position].soldiers['bird'] > 0:
                        for i in range(map.places[map.vagabond_position].soldiers['bird']):
                            move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=1,  who='vagabond', vagabond_allies=(i+1, 'bird')))
                    if self.relations['alliance'] == 'friendly' and map.places[map.vagabond_position].soldiers['alliance'] > 0:
                        for i in range(map.places[map.vagabond_position].soldiers['alliance']):
                            move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=1,  who='vagabond', vagabond_allies=(i+1, 'alliance')))
        return move_options
    
    def get_refresh_options(self):
        item_num = self.other_items.count(Item("root_tea"))*2 + 3
        all_items = self.satchel + self.other_items
        exhausted_items = [item for item in all_items if item.exhausted]
        return list(combinations(exhausted_items, min(item_num, len(exhausted_items))))
    
    #def get_damage_options(self, num_dmged):
    #    all_items = self.satchel + self.other_items
    #    non_damaged_items = [item for item in all_items if not item.damaged]
    #    non_damaged_items += self.allied_soldiers
    #    return list(combinations(non_damaged_items, min(num_dmged, len(non_damaged_items))))

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
                    if self.brutal_tactics:
                        battle_options.append(Battle_DTO(map.vagabond_position, army, brutal_tactics_usage=True))
                    if self.armorers:
                        battle_options.append(Battle_DTO(map.vagabond_position, army, armorer_usage=True))
                    if self.armorers and self.brutal_tactics:
                        battle_options.append(Battle_DTO(map.vagabond_position, army, brutal_tactics_usage=True, armorer_usage=True))

            for building_slots in map.places[map.vagabond_position].building_slots:
                if building_slots[1] != "No one":
                    battle_options.append(Battle_DTO(map.vagabond_position, building_slots[1]))
                    if self.brutal_tactics:
                        battle_options.append(Battle_DTO(map.vagabond_position, building_slots[1], brutal_tactics_usage=True))
                    if self.armorers:
                        battle_options.append(Battle_DTO(map.vagabond_position, building_slots[1], armorer_usage=True))
                    if self.armorers and self.brutal_tactics:
                        battle_options.append(Battle_DTO(map.vagabond_position, building_slots[1], brutal_tactics_usage=True, armorer_usage=True))
            
            if "sympathy" in map.places[map.vagabond_position].tokens:
                    battle_options.append(Battle_DTO(map.vagabond_position, 'alliance'))
                    if self.brutal_tactics:
                        battle_options.append(Battle_DTO(map.vagabond_position, 'alliance', brutal_tactics_usage=True))
                    if self.armorers:
                        battle_options.append(Battle_DTO(map.vagabond_position, 'alliance', armorer_usage=True))
                    if self.armorers and self.brutal_tactics:
                        battle_options.append(Battle_DTO(map.vagabond_position, 'alliance', brutal_tactics_usage=True, armorer_usage=True))

            if "wood" in map.places[map.vagabond_position].tokens or "keep" in map.places[map.vagabond_position].tokens:
                battle_options.append(Battle_DTO(map.vagabond_position, 'cat'))
                if self.brutal_tactics:
                    battle_options.append(Battle_DTO(map.vagabond_position, 'cat', brutal_tactics_usage=True))
                if self.armorers:
                    battle_options.append(Battle_DTO(map.vagabond_position, 'cat', armorer_usage=True))
                if self.armorers and self.brutal_tactics:
                    battle_options.append(Battle_DTO(map.vagabond_position, 'cat', brutal_tactics_usage=True, armorer_usage=True))
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
                    self.has_items(quest_card.item1, quest_card.item2)):
                quest_options.append((quest_card.ID, 'draw'))
                quest_options.append((quest_card.ID, 'VP'))

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

        if current_clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in current_clearing.building_slots]or 'keep' in current_clearing.tokens or 'wood' in current_clearing.tokens:
            thief_ability_options.append('cat')
        if current_clearing.soldiers['bird'] > 0 or True in [slot[0] == 'roost' for slot in current_clearing.building_slots]:
            thief_ability_options.append('bird')
        if current_clearing.soldiers['alliance'] > 0 or True in [slot[0] == 'base' for slot in current_clearing.building_slots] or "sympathy" in current_clearing.tokens:
            thief_ability_options.append('alliance')

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
                continue
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

    def get_aid_options(self, map, opponents):
        aid_options = []
        current_clearing = map.places[map.vagabond_position]
        # Iterates through name
        i = 0
        for opponent in opponents:
            if current_clearing.has_opponent_pieces(opponent.name):
                relation = self.relations[opponent.name]
                if relation == 'hostile':
                    continue

                item_choices = []  # Get items from the opponent
                for item in opponents[i].items: #Iterates through opponent objects from arquments
                    item_choices.append(Item(item.name))
                item_choices = set(item_choices)

                for card in self.deck.cards:
                    if card.card_suit == current_clearing.suit or card.card_suit == 'bird':
                        if item_choices:
                            for item in item_choices:
                                aid_options.append((opponent, card.ID, item))
                        else:
                            aid_options.append((opponent, card.ID, None))
            i += 1

        return aid_options

    def refresh_allied_soldiers(self, map):
        current_clearing = map.places[map.vagabond_position]
        for opponent in ['cat', 'bird', 'alliance']:
            if self.relations[opponent] == 'friendly':
                for _ in range(current_clearing.soldiers[opponent]):
                    self.allied_soldiers += opponent

    def get_item_dmg_options(self):
        """Returns a list of items that can be damaged"""
        item_dmg_options = []
        for item in self.satchel + self.other_items:
            if not item.damaged:
                item_dmg_options.append(item)
        self.refresh_allied_soldiers()
        for soldier in self.allied_soldiers:
            item_dmg_options.append(soldier)

        random.shuffle(item_dmg_options)
        self.items_to_damage = item_dmg_options

    def damage_item(self, other_item, place = None):
        # Place: when the vagabond is allied to a faction, the factions soldiers are considered items, vagabond doesn't care
        if isinstance(other_item, Item):
            for item in self.satchel:
                if item.name == other_item.name and not item.damaged:
                    item.damaged = True
                    return True
            for item in self.other_items:
                if item.name == other_item.name and not item.damaged:
                    item.damaged = True
                    return True
        if place and not isinstance(other_item, Item):
            place.soldiers[self.allied_soldiers[0]] -= 1
            self.allied_soldiers.remove(self.allied_soldiers[0])
        return False

    def add_item(self, item):
        if item.name in ['sword', 'crossbow', 'hammer', 'boot', 'torch']:
            self.satchel.append(item)
        else:
            self.other_items.append(item)

    def exhaust_item(self, other_item):
        for item in self.satchel:
            if item.name == other_item.name and not item.exhausted:
                item.exhausted = True
                return
        for item in self.other_items:
            if item.name == other_item.name and not item.exhausted:
                item.exhausted = True
                return
        raise ValueError("Item not found or exhausted")

    def repair_item(self, other_item):
        for item in self.satchel:
            if item.name == other_item.name and item.damaged:
                item.damaged = False
                return
        for item in self.other_items:
            if item.name == other_item and item.damaged:
                item.damaged = False
                return
        raise ValueError("Item not found or not damaged")
    
    def refresh_item(self, other_item):
        for item in self.satchel:
            if item.name == other_item.name and item.exhausted:
                item.exhausted = False
                return
        for item in self.other_items:
            if item.name == other_item.name and item.exhausted:
                item.exhausted = False
                return
        raise ValueError("Item not found or not exhausted")
    
    def repair_and_refresh_all(self):
        for item in self.satchel:
            item.damaged = False
            item.exhausted = False
        for item in self.other_items:
            item.damaged = False
            item.exhausted = False
    
    def deactivate(self, cost):
        total = 0
        for amount in cost.values():
            total += amount
        for _ in range(total):
            self.exhaust_item(Item("hammer"))

    def get_discard_items_down_to_sack_options(self):
        pass