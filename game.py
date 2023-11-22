from actors import Marquise, Eyrie, Alliance, Vagabond
from item import Item
from dtos import CraftDTO
from map import build_regular_forest
from deck import Deck, QuestDeck
from configs import sympathy_VPs, eyrie_roost_VPs, persistent_effects, Immediate_non_item_effects, eyrie_leader_config, buildings_list_marquise, vagabond_quest_card_info, total_common_card_info
from game_helper_random import alliance_choose_card, choose_card_prios
from copy import copy
import random
import logging
import torch
import numpy as np


class Game():
    def __init__(self, debug = True) -> None:
        self.encoded_adjacencies_forest = np.array(([0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                                                    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                    [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
                                                    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                                                    [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
                                                    [0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0],
                                                    [0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0],
                                                    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1],
                                                    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
                                                    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
                                                    [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
                                                    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0]))
        if debug:
            self.map = build_regular_forest()
            self.marquise = Marquise(map=self.map)
            self.eyrie = Eyrie(map=self.map, role='Despot')
            self.alliance = Alliance(map=self.map)
            self.vagabond = Vagabond(map=self.map, role="Thief")
            self.deck = Deck()
            self.discard_deck = Deck(empty=True)
            self.dominance_discard_deck = Deck(empty=True)
            self.quest_deck = QuestDeck()
            self.discard_quest_deck = QuestDeck(empty=True)
            self.winner = None

            self.marquise.deck.add_card(self.deck.get_the_card(5))
            self.marquise.deck.add_card(self.deck.get_the_card(11))
            self.marquise.deck.add_card(self.deck.get_the_card(12))

            # everyone gets 1 rabbit 2 fox 1 bird
            self.eyrie.deck.add_card(self.deck.get_the_card(0))
            self.eyrie.deck.add_card(self.deck.get_the_card(27))
            self.eyrie.deck.add_card(self.deck.get_the_card(28))
            self.eyrie.deck.add_card(self.deck.get_the_card(53))

            self.alliance.deck.add_card(self.deck.get_the_card(1))
            self.alliance.deck.add_card(self.deck.get_the_card(29))
            self.alliance.deck.add_card(self.deck.get_the_card(30))
            self.alliance.deck.add_card(self.deck.get_the_card(52))

            self.alliance.supporter_deck.add_card(self.deck.get_the_card(2))
            self.alliance.supporter_deck.add_card(self.deck.get_the_card(31))
            self.alliance.supporter_deck.add_card(self.deck.get_the_card(32))
            self.alliance.supporter_deck.add_card(self.deck.get_the_card(51))

            self.vagabond.deck.add_card(self.deck.get_the_card(3))
            self.vagabond.deck.add_card(self.deck.get_the_card(33))
            self.vagabond.deck.add_card(self.deck.get_the_card(34))
            self.vagabond.deck.add_card(self.deck.get_the_card(50))

            self.vagabond.quest_deck.add_card(self.quest_deck.get_the_card(10)) # 2 mouse 1 fox
            self.vagabond.quest_deck.add_card(self.quest_deck.get_the_card(11))
            self.vagabond.quest_deck.add_card(self.quest_deck.get_the_card(0))


        else:
            vagabond_roles = ["Thief"] # ["Thief", "Ranger", "Tinkerer"]
            eyrie_leaders = ["Despot", "Commander", "Charismatic", "Builder"]
            self.map = build_regular_forest()

            self.marquise = Marquise(map=self.map)
            self.eyrie = Eyrie(map=self.map, role=random.choice(eyrie_leaders))
            self.alliance = Alliance(map=self.map)
            self.vagabond = Vagabond(map=self.map, role=random.choice(vagabond_roles))
            self.winner = None

            self.deck = Deck()
            self.discard_deck = Deck(empty=True)
            self.quest_deck = QuestDeck()
            self.discard_quest_deck = QuestDeck(empty=True)
            self.dominance_discard_deck = Deck(empty=True)

            self.marquise.deck.add_card(self.deck.draw_card())
            self.marquise.deck.add_card(self.deck.draw_card())
            self.marquise.deck.add_card(self.deck.draw_card())

            self.eyrie.deck.add_card(self.deck.draw_card())
            self.eyrie.deck.add_card(self.deck.draw_card())
            self.eyrie.deck.add_card(self.deck.draw_card())

            self.alliance.deck.add_card(self.deck.draw_card())
            self.alliance.deck.add_card(self.deck.draw_card())
            self.alliance.deck.add_card(self.deck.draw_card())

            self.alliance.supporter_deck.add_card(self.deck.draw_card())
            self.alliance.supporter_deck.add_card(self.deck.draw_card())
            self.alliance.supporter_deck.add_card(self.deck.draw_card())

            self.vagabond.deck.add_card(self.deck.draw_card())
            self.vagabond.deck.add_card(self.deck.draw_card())
            self.vagabond.deck.add_card(self.deck.draw_card())

            self.vagabond.quest_deck.add_card(self.quest_deck.draw_card())
            self.vagabond.quest_deck.add_card(self.quest_deck.draw_card())
            self.vagabond.quest_deck.add_card(self.quest_deck.draw_card())


    def encode(self, gamestate, player_id = 0):
        map_encoded = np.zeros((12,16))
        map_adjacency_encoded = self.encoded_adjacencies_forest # Hard coded until we only use forest
        for i, place in enumerate(self.map.places.values()):
            if i < 12:
                for slot in place.building_slots:
                    map_encoded[i][0] += 1 if slot[0] == "sawmill" else 0
                    map_encoded[i][1] += 1 if slot[0] == "workshop" else 0
                    map_encoded[i][2] += 1 if slot[0] == "recruiter" else 0
                    map_encoded[i][3] += 1 if slot[0] == "roost" else 0
                    map_encoded[i][4] += 1 if slot[0] == "base" else 0
                    map_encoded[i][5] += 1 if slot[0] == "ruin" else 0
                for token in place.tokens:
                    map_encoded[i][6] += 1 if token == "sympathy" else 0
                    map_encoded[i][7] += 1 if token == "keep" else 0
                    map_encoded[i][8] += 1 if token == "wood" else 0
                map_encoded[i][9] = place.soldiers['cat']
                map_encoded[i][10] = place.soldiers['bird']
                map_encoded[i][11] = place.soldiers['alliance']
                map_encoded[i][12] = len(place.building_slots)
                map_encoded[i][13] = 1 if place.vagabond_is_here else 0
                map_encoded[i][14] = 0 if place.suit == "fox" else 1 if place.suit == "mouse" else 2
                neighbouring_vagabonds = 0
                for neighbor in place.neighbors:
                    neighbouring_vagabonds += 1 if self.map.places[neighbor[0]].vagabond_is_here else 0
                map_encoded[i][15] = min(neighbouring_vagabonds, 1)

        craftables = np.zeros((7,1))
        craftables[0][0] = self.map.craftables.count(Item("sack"))
        craftables[1][0] = self.map.craftables.count(Item("root_tea"))
        craftables[2][0] = self.map.craftables.count(Item("money"))
        craftables[3][0] = self.map.craftables.count(Item("boot"))
        craftables[4][0] = self.map.craftables.count(Item("sword"))
        craftables[5][0] = Item("crossbow") in self.map.craftables
        craftables[6][0] = Item("hammer") in self.map.craftables

        gamestate_encoded = np.zeros((15, 1))
        gamestate_encoded[gamestate][0] = 1

        player_id_encoded = np.zeros((4, 1))
        player_id_encoded[player_id][0] = 1

        encoded_discard_deck, encoded_discard_suits = self.discard_deck.encode_deck()
        _, encoded_domimance_discard_suits = self.dominance_discard_deck.encode_deck()

        # ACTORS, ENCODED SUPPORTER DECK MIGHT NOT BE USEFUL
        cat_encoded_deck, cat_encoded_suits, cat_encoded_buffs, cat_encoded_VP, cat_encoded_win_condition, cat_encoded_items = self.marquise.encode_actor()
        bird_encoded_deck, bird_encoded_suits, bird_encoded_buffs, bird_encoded_VP, bird_encoded_win_condition, bird_encoded_items, encoded_role, encoded_avaible_leaders, encoded_decree, encoded_decree_deck = self.eyrie.encode_actor()
        alliance_encoded_deck, alliance_encoded_suits, alliance_encoded_buffs, alliance_encoded_VP, alliance_encoded_win_condition, alliance_encoded_items, encoded_supporter_deck, encoded_supporter_suits, encoded_total_officers = self.alliance.encode_actor()
        vagabond_encoded_deck, vagabond_encoded_suits, vagabond_encoded_buffs, vagabond_encoded_VP, vagabond_encoded_win_condition, vagabond_encoded_items = self.vagabond.encode_actor()

        # ALL NON MAP INFO TO A VECTOR
        encoded_decks = np.concatenate((encoded_discard_deck, cat_encoded_deck, bird_encoded_deck, alliance_encoded_deck, encoded_supporter_deck, vagabond_encoded_deck), axis=0)
        encoded_suits = np.concatenate((encoded_discard_suits, encoded_domimance_discard_suits, cat_encoded_suits, bird_encoded_suits, alliance_encoded_suits, encoded_supporter_suits, vagabond_encoded_suits), axis=0)
        encoded_buffs = np.concatenate((cat_encoded_buffs, bird_encoded_buffs, alliance_encoded_buffs, vagabond_encoded_buffs), axis=0)
        encoded_items = np.concatenate((craftables, cat_encoded_items, bird_encoded_items, alliance_encoded_items, vagabond_encoded_items.reshape((-1,1))), axis=0)
        encoded_VPs = np.concatenate((cat_encoded_VP, bird_encoded_VP, alliance_encoded_VP, vagabond_encoded_VP), axis=0)
        encoded_win_conditions = np.concatenate((cat_encoded_win_condition, bird_encoded_win_condition, alliance_encoded_win_condition, vagabond_encoded_win_condition), axis=0)
        encoded_other_actor_info = np.concatenate((encoded_role, encoded_avaible_leaders, encoded_decree.reshape((-1,1)), encoded_decree_deck, encoded_total_officers), axis=0)

        total_other_info = np.concatenate((encoded_decks, encoded_suits, encoded_buffs, encoded_items, encoded_VPs, encoded_win_conditions, encoded_other_actor_info, gamestate_encoded, player_id_encoded), axis=0)
        encoding = np.concatenate((map_encoded.reshape((-1,1)), map_adjacency_encoded.reshape((-1,1)), total_other_info), axis=0)

        return  torch.tensor(encoding.T, dtype = torch.float)


    def check_victory_points(self):
        if self.marquise.victory_points >= 30 and not self.winner:
            if self.marquise.win_condition == "points":
                self.winner = ("cat", "points")
            elif self.marquise.win_condition == "coalition_major":
                self.winner = ("cat", "coalition")
        if self.eyrie.victory_points >= 30 and not self.winner:
            if self.eyrie.win_condition == "points":
                self.winner = ("bird", "points")
            elif self.eyrie.win_condition == "coalition_major":
                self.winner = ("bird", "coalition")
        if self.alliance.victory_points >= 30 and not self.winner:
            if self.alliance.win_condition == "points":
                self.winner = ("alliance", "points")
            elif self.alliance.win_condition == "coalition_major":
                self.winner = ("alliance", "coalition")
        if self.vagabond.victory_points >= 30 and not self.winner:
            if self.vagabond.win_condition == "points":
                self.winner = ("vagabond", "points")

    def check_dominance(self, actor):
        if not self.winner:
            if actor.win_condition == "bird":
                if self.map.places['F'].owner == actor.name and self.map.places['C'].owner == actor.name:
                    self.winner = (actor.name, "bird dominance")
                elif self.map.places['A'].owner == actor.name and self.map.places['L'].owner == actor.name:
                    self.winner = (actor.name, "bird dominance")
            if actor.win_condition == "fox":
                if [True if place.owner == actor.name and place.suit == "fox" else False for place in self.map.places.values()].count(True) >= 3:
                    self.winner = (actor.name, "fox dominance")
            if actor.win_condition == "mouse":
                if [True if place.owner == actor.name and place.suit == "mouse" else False for place in self.map.places.values()].count(True) >= 3:
                    self.winner = (actor.name, "mouse dominance")
            if actor.win_condition == "rabbit":
                if [True if place.owner == actor.name and place.suit == "rabbit" else False for place in self.map.places.values()].count(True) >= 3:
                    self.winner = (actor.name, "rabbit dominance")
                    
    def remove_soldiers_from_vagabond_items(self, items, defender):
        new_items = []
        for item in items:
            if not item == defender:
                new_items.append(item)
        return new_items
    
   def priority_to_list(self, priorities, placename, owner):
       """
       :param priority: str
       :return: list
       """
       chosen_pieces = []
       for piece in priorities:
           for token in self.map.places[placename].tokens:
               if token == piece:
                   chosen_pieces.append((token, 'token'))
           for building_slot in self.map.places[placename].building_slots:
               if building_slot[0] == piece and building_slot[1] == owner:
                   chosen_pieces.append((building_slot[0], 'building'))
       return chosen_pieces