from deck import Deck, QuestDeck
from dtos import Battle_DTO, CraftDTO, MoveDTO, OverworkDTO
from configs import buildings_list_marquise, Immediate_non_item_effects, persistent_effects, eyrie_leader_config
from itertools import combinations
from item import Item
from copy import copy
import logging
import random
import numpy as np

class ExhaustbootERROR(Exception):
    pass
class Actor():

    def __init__(self, map) -> None:
        self.deck = Deck(empty=True)
        self.sappers = False
        self.cobbler = False
        self.tax_collector = False
        self.armorers = False
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
        self.persistent_effect_deck = Deck(empty=True)
    
    def encode_actor(self):
        encoded_deck, encoded_suits = self.deck.encode_deck()

        encoded_buffs = np.zeros((11, 1))
        encoded_buffs[0][0] = self.sappers
        encoded_buffs[1][0] = self.cobbler
        encoded_buffs[2][0] = self.tax_collector
        encoded_buffs[3][0] = self.armorers
        encoded_buffs[4][0] = self.command_warren
        encoded_buffs[5][0] = self.scouting_party
        encoded_buffs[6][0] = self.codebreakers
        encoded_buffs[7][0] = self.stand_and_deliver
        encoded_buffs[8][0] = self.better_burrow_bank
        encoded_buffs[9][0] = self.royal_claim
        encoded_buffs[10][0] = self.brutal_tactics

        encoded_VP = np.array([[self.victory_points]])

        encoded_win_condition = np.zeros((6, 1))
        if self.win_condition == "points":
            encoded_win_condition[0][0] = 1
        elif self.win_condition == "rabbit":
            encoded_win_condition[1][0] = 1
        elif self.win_condition == "mouse":
            encoded_win_condition[2][0] = 1
        elif self.win_condition == "fox":
            encoded_win_condition[3][0] = 1
        elif self.win_condition == "bird":
            encoded_win_condition[4][0] = 1
        elif self.win_condition == "coalition_major" or self.win_condition == "coalition_minor":
            encoded_win_condition[5][0] = 1

        return encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition


    def __lt__(self, other):
        return self.name < other.name

    def add_item(self, item):
        self.items.append(item)
        
    def deactivate(self, cost):
        for suit, amount in cost.items():
            self.craft_activations[suit] -= amount
    


class Marquise(Actor):
    def __init__(self, map) -> None:
        super().__init__(map)
        self.items = []
        self.name = 'cat'
    
    def encode_actor(self):
        encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition = super().encode_actor()

        encoded_items = np.zeros((7, 1))
        encoded_items[0][0] = self.items.count(Item("sack"))
        encoded_items[1][0] = self.items.count(Item("root_tea"))
        encoded_items[2][0] = self.items.count(Item("money"))
        encoded_items[3][0] = self.items.count(Item("boot"))
        encoded_items[4][0] = self.items.count(Item("sword"))
        encoded_items[5][0] = self.items.count(Item("crossbow"))
        encoded_items[6][0] = self.items.count(Item("hammer"))

        return encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition, encoded_items

    def refresh_craft_activations(self, map):
        self.craft_activations = map.count_on_map(("building", "workshop"), per_suit=True)


    def count_for_card_draw(self, map):
        draws = 1
        recruiter_count = map.count_on_map(("building", "recruiter"))
        if recruiter_count > 2:
            draws += 1
        if recruiter_count > 4:
            draws += 1
        return draws


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

    def encode_actor(self):

        encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition = super().encode_actor()

        encoded_items = np.zeros((7, 1))
        encoded_items[0][0] = self.items.count(Item("sack"))
        encoded_items[1][0] = self.items.count(Item("root_tea"))
        encoded_items[2][0] = self.items.count(Item("money"))
        encoded_items[3][0] = self.items.count(Item("boot"))
        encoded_items[4][0] = self.items.count(Item("sword"))
        encoded_items[5][0] = self.items.count(Item("crossbow"))
        encoded_items[6][0] = self.items.count(Item("hammer"))

        encoded_role = np.zeros((4, 1))
        if self.leader == "Despot":
            encoded_role[0][0] = 1
        elif self.leader == "Commander":
            encoded_role[1][0] = 1
        elif self.leader == "Builder":
            encoded_role[2][0] = 1
        elif self.leader == "Charismatic":
            encoded_role[3][0] = 1
        
        encoded_avaible_leaders = np.ones((4, 1))
        if "Despot" not in self.avaible_leaders:
            encoded_avaible_leaders[0][0] = 0
        if "Commander" not in self.avaible_leaders:
            encoded_avaible_leaders[1][0] = 0
        if "Builder" not in self.avaible_leaders:
            encoded_avaible_leaders[2][0] = 0
        if "Charismatic" not in self.avaible_leaders:
            encoded_avaible_leaders[3][0] = 0
        
        encoded_decree = np.zeros((4, 4))
        for i, decree in enumerate(self.decree.values()): 
            encoded_decree[i][0] = [card[1] for card in decree].count("fox")
            encoded_decree[i][1] = [card[1] for card in decree].count("mouse")
            encoded_decree[i][2] = [card[1] for card in decree].count("rabbit")
            encoded_decree[i][3] = [card[1] for card in decree].count("bird")

        encoded_decree_deck, _ = self.decree_deck.encode_deck()

        return encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition, encoded_items, encoded_role, encoded_avaible_leaders, encoded_decree, encoded_decree_deck

    def check_role(self):
        if self.leader in self.avaible_leaders:
            self.avaible_leaders.remove(self.leader)
            return
        else:
            raise ValueError("Invalid role for Eyrie")

    def change_role(self, role):
        self.leader = role
        self.setup_based_on_leader()
        
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
    
    def remove_from_temp_decree(self, card_ID, action):
        self.temp_decree[action] = [(ID, suit) for ID, suit in self.temp_decree[action] if ID != card_ID]

    
    def pieces_to_lose_in_battle(self):
        return ['roost']

    def refresh_temp_decree(self):
        self.temp_decree = copy(self.decree)
        
    def refresh_craft_activations(self, map):
        self.craft_activations = map.count_on_map(("building", "roost"), per_suit=True)
    


class Alliance(Actor):
    def __init__(self, map) -> None:
        super().__init__(map)
        self.supporter_deck = Deck(empty = True)
        self.items = []
        self.total_officers = 0
        self.name = "alliance"

    def encode_actor(self):
        encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition = super().encode_actor()

        encoded_items = np.zeros((7, 1))
        encoded_items[0][0] = self.items.count(Item("sack"))
        encoded_items[1][0] = self.items.count(Item("root_tea"))
        encoded_items[2][0] = self.items.count(Item("money"))
        encoded_items[3][0] = self.items.count(Item("boot"))
        encoded_items[4][0] = self.items.count(Item("sword"))
        encoded_items[5][0] = self.items.count(Item("crossbow"))
        encoded_items[6][0] = self.items.count(Item("hammer"))

        encoded_supporter_deck, encoded_supporter_suits = self.supporter_deck.encode_deck()
        encoded_total_officers = np.array([[self.total_officers]])

        return encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition, encoded_items, encoded_supporter_deck, encoded_supporter_suits, encoded_total_officers

    def count_for_card_draw(self, map):
        draws = map.count_on_map(("building", "base")) + 1
        return draws

    def pieces_to_lose_in_battle(self):
        return ['sympathy', 'base']

    def losing_a_base(self, place_suit, discard_deck):
        card_ids_to_remove = []
        for card in self.supporter_deck.cards:
            if card.card_suit == place_suit or card.card_suit == "bird":
                card_ids_to_remove.append(card.ID)
    
        logging.debug(f"Removing {card_ids_to_remove} from the Alliance's supporter deck because of a base loss")
        for card_id in card_ids_to_remove:
            discard_deck.add_card(self.supporter_deck.get_the_card(card_id))

    def base_search(self, map, suit):
        for place in map.places.values():
            if place.suit == suit:
                for slot in place.building_slots:
                    if slot[0] == 'base':
                        return True
        return False
    
    def refresh_craft_activations(self, map):
        self.craft_activations = map.count_on_map(("token", "sympathy"), per_suit=True)
            
    def take_card_from_a_player_options(self, player):
        self.known_hands[player.name] = True
        return [card.ID for card in player.deck.cards]

    


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
			"alliance" : 'indifferent',
            "No one": 'indifferent',
		}
            self.refresh_items_to_damage()
        else:
            raise NotImplementedError("Only thief yet")

    def encode_actor(self):
        encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition = super().encode_actor()

        encoded_items = np.zeros((8,3)) # first three other items, satchel last 5
        encoded_items[0][0] = self.other_items.count(Item("sack"))
        encoded_items[0][1] = sum([1 if item.name == "sack" and item.exhausted else 0 for item in self.other_items])
        encoded_items[0][2] = sum([1 if item.name == "sack" and item.damaged else 0 for item in self.other_items])

        encoded_items[1][0] = self.other_items.count(Item("root_tea"))
        encoded_items[1][1] = sum([1 if item.name == "root_tea" and item.exhausted else 0 for item in self.other_items])
        encoded_items[1][2] = sum([1 if item.name == "root_tea" and item.damaged else 0 for item in self.other_items])

        encoded_items[2][0] = self.other_items.count(Item("money"))
        encoded_items[2][1] = sum([1 if item.name == "money" and item.exhausted else 0 for item in self.other_items])
        encoded_items[2][2] = sum([1 if item.name == "money" and item.damaged else 0 for item in self.other_items])

        encoded_items[3][0] = self.other_items.count(Item("boot"))
        encoded_items[3][1] = sum([1 if item.name == "boot" and item.exhausted else 0 for item in self.satchel])
        encoded_items[3][2] = sum([1 if item.name == "boot" and item.damaged else 0 for item in self.satchel])

        encoded_items[4][0] = self.other_items.count(Item("sword"))
        encoded_items[4][1] = sum([1 if item.name == "sword" and item.exhausted else 0 for item in self.satchel])
        encoded_items[4][2] = sum([1 if item.name == "sword" and item.damaged else 0 for item in self.satchel])

        encoded_items[5][0] = self.other_items.count(Item("crossbow"))
        encoded_items[5][1] = sum([1 if item.name == "crossbow" and item.exhausted else 0 for item in self.satchel])
        encoded_items[5][2] = sum([1 if item.name == "crossbow" and item.damaged else 0 for item in self.satchel])

        encoded_items[5][0] = self.other_items.count(Item("hammer"))
        encoded_items[5][1] = sum([1 if item.name == "hammer" and item.exhausted else 0 for item in self.satchel])
        encoded_items[5][2] = sum([1 if item.name == "hammer" and item.damaged else 0 for item in self.satchel])


        return encoded_deck, encoded_suits, encoded_buffs, encoded_VP, encoded_win_condition, encoded_items

    def refresh_craft_activations(self, map):
        pass

    def refresh_items_to_damage(self): # TODO NEEDS to be written properly after debug
        self.items_to_damage = [Item('root_tea'), Item('torch'), Item('boot'), Item('sword')]

    def chack_relation_status_correct(self):
        for status in self.relations.values():
            if not status in ['indifferent', 'hostile', 'good', 'very good', 'friendly']:
                return True

    def count_for_card_draw(self):
        return self.satchel.count(Item('money')) + 1
    
        def has_non_exhausted_item(self, searched_item):
        for item in self.satchel + self.other_items:
            if item.name == searched_item.name and not item.exhausted and not item.damaged:
                return True
        return False



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

    def refresh_allied_soldiers(self, map):
        current_clearing = map.places[map.vagabond_position]
        self.allied_soldiers = []
        for opponent in ['cat', 'bird', 'alliance']:
            if self.relations[opponent] == 'friendly':
                for _ in range(current_clearing.soldiers[opponent]):
                    self.allied_soldiers.append(opponent)

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
        raise ExhaustbootERROR(f"Item:{other_item.name} not found or exhausted")

    def repair_item(self, other_item):
        for item in self.satchel:
            if item.name == other_item.name and item.damaged:
                item.damaged = False
                return
        for item in self.other_items:
            if item.name == other_item.name and item.damaged:
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

    def get_options(self):
        return super().get_options()

