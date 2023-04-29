from actors import Marquise, Eyrie, Alliance, Vagabond
from item import Item
from dtos import CraftDTO
from map import build_regular_forest
from deck import Deck, QuestDeck
from configs import sympathy_VPs, eyrie_roost_VPs, persistent_effects, Immediate_non_item_effects, eyrie_leader_config, buildings_list_marquise, vagabond_quest_card_info, total_common_card_info
from game_helper import alliance_choose_card, choose_card_prios
import random
import logging


class Game():
    def __init__(self, debug = True) -> None:
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

    def stand_and_deliver(self, taker, victim):
        if not victim:
            return
        victim.deck.shuffle_deck()
        taker.deck.add_card(victim.deck.draw_card())
        victim.victory_points += 1
        self.check_victory_points()

    def check_victory_points(self):
        if self.marquise.victory_points >= 30 and not self.winner:
            if self.marquise.win_condition == "points":
                self.winner = "marquise"
            elif self.marquise.win_condition == "coalition_major":
                self.winner = "marquise and vagabond"
        elif self.eyrie.victory_points >= 30 and not self.winner:
            if self.eyrie.win_condition == "points":
                self.winner = "eyrie"
            elif self.eyrie.win_condition == "coalition_major":
                self.winner = "eyrie and vagabond"
        elif self.alliance.victory_points >= 30 and not self.winner:
            if self.alliance.win_condition == "points":
                self.winner = "alliance"
            elif self.alliance.win_condition == "coalition_major":
                self.winner = "alliance and vagabond"
        elif self.vagabond.victory_points >= 30 and not self.winner:
            if self.vagabond.win_condition == "points":
                self.winner = "vagabond"

    def swap_discarded_dominance_card(self, actor, card_id1, card_id2):
        actor.deck.add_card(self.dominance_discard_deck.get_the_card(card_id1))
        self.discard_deck.add_card(actor.deck.get_the_card(card_id2))

    def check_dominance(self, actor):
        if not self.winner:
            if actor.win_condition == "bird":
                if self.map.places['F'].owner == actor.name and self.map.places['C'].owner == actor.name:
                    self.winner = actor.name
                elif self.map.places['A'].owner == actor.name and self.map.places['L'].owner == actor.name:
                    self.winner = actor.name
            if actor.win_condition == "fox":
                if [True if place.owner == actor.name and place.suit == "fox" else False for place in self.map.places.values()].count(True) >= 3:
                    self.winner = actor.name
            if actor.win_condition == "mouse":
                if [True if place.owner == actor.name and place.suit == "mouse" else False for place in self.map.places.values()].count(True) >= 3:
                    self.winner = actor.name
            if actor.win_condition == "rabbit":
                if [True if place.owner == actor.name and place.suit == "rabbit" else False for place in self.map.places.values()].count(True) >= 3:
                    self.winner = actor.name

    def field_hospital(self, dead_soldiers, card_ID):
        keep_position = [place.name if 'keep' in place.tokens else None for place in self.map.places.values()]
        self.map.places[keep_position].soldiers['cat'] += dead_soldiers
        if total_common_card_info[card_ID][2] == "dominance":
            self.dominance_discard_deck.add_card(self.marquise.deck.get_the_card(card_ID))
        else:
            self.discard_deck.add_card(self.marquise.deck.get_the_card(card_ID))


    def better_burrow_bank(self, actor, other):
        actor.deck.add_card(self.deck.draw_card())
        if len(self.deck.cards) >= 0: # DECK ONE LINER
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)
        other.deck.add_card(self.deck.draw_card())

    def tax_collection(self, actor, placename):
        self.map.places[placename].soldiers[actor.name] -= 1
        actor.deck.add_card(self.deck.draw_card())
        self.map.places[placename].update_owner()
        if len(self.deck.cards) >= 0: # DECK ONE LINER
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)

    def activate_royal_claim(self, actor):
        for place in self.map.places.values():
            if place.owner == actor.name:
                actor.victory_points += 1
        self.check_victory_points()
        actor.royal_claim = False
        self.discard_deck.add_card(actor.persistent_effect_deck.get_the_card(53))

    def cat_birdsong_wood(self):
        for key in list(self.map.places.keys()):
            for building_slot in self.map.places[key].building_slots:
                if building_slot[0] == "sawmill" and self.map.count_on_map(('token', 'wood')) < 8:
                    self.map.places[key].update_pieces(tokens = self.map.places[key].tokens + ["wood"])  

    def add_card_to_decree(self, action, card_ID, card_suit):
        self.eyrie.decree[action].append((card_ID, card_suit))

        if self.eyrie.decree_deck.add_card(self.eyrie.deck.get_the_card(card_ID)) is not None:
            raise ValueError("Eyrie tried to add wrong card to decree deck")

    def place_roost_if_zero_roost(self, place_name):
        try:
            self.map.places[place_name].building_slots[self.map.places[place_name].building_slots.index(('empty', 'No one'))] = ('roost', 'bird')
            self.map.places[place_name].soldiers['bird'] += 3
            self.map.places[place_name].update_owner()
        except ValueError:
            raise ValueError("Error in get_no_roosts_left_options")

    def cat_use_bird_card_to_gain_move(self, cardID):
        if total_common_card_info[cardID][2] == "dominance":
            self.dominance_discard_deck.add_card(self.marquise.deck.get_the_card(cardID))
        else:
            self.discard_deck.add_card(self.marquise.deck.get_the_card(cardID))


    # Alliance
    def revolt(self, place, card_ID1, card_ID2, soldiers_to_gain):
        # Clear all buildings
        victory_points = 0
        victory_points += place.clear_buildings()
        self.count_lost_points_marquise(place=place)
        victory_points += place.clear_tokens(exception_faction = "alliance")
        place.clear_soldiers(exception_faction="alliance")

        # Add a base for the alliance
        place.add_building('base', 'alliance')

        # If the vagabond is present, damage 3 vagabond items
        if place.vagabond_is_here:
            for item in self.vagabond.items_to_damage[:3]:
                self.vagabond.damage_item(item)
        if total_common_card_info[card_ID1][2] == "dominance":
            self.dominance_discard_deck.add_card(self.alliance.supporter_deck.get_the_card(card_ID1))
        else:
            self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(card_ID1))

        if total_common_card_info[card_ID2][2] == "dominance":
            self.dominance_discard_deck.add_card(self.alliance.supporter_deck.get_the_card(card_ID2))
        else:
            self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(card_ID2))

        for _ in range(soldiers_to_gain):
            if sum([place.soldiers["alliance"] for place in self.map.places.values()]) + self.alliance.total_officers >= 10:
                break
            place.soldiers["alliance"] += 1

        if sum([place.soldiers["alliance"] for place in self.map.places.values()]) + self.alliance.total_officers <= 10:
            self.alliance.total_officers += 1

        place.update_owner()
        self.alliance.victory_points += victory_points
        self.check_victory_points()


    def spread_sympathy(self, place_name, card_ids):
        self.map.places[place_name].update_pieces(tokens = self.map.places[place_name].tokens + ['sympathy'])

        for cardID in card_ids:
            if total_common_card_info[cardID][2] == "dominance":
                self.dominance_discard_deck.add_card(self.alliance.supporter_deck.get_the_card(cardID))
            else:
                self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(cardID))

        victory_points = sympathy_VPs[self.map.count_on_map(what_to_look_for=('token', 'sympathy'), per_suit = False)]
        self.alliance.victory_points += victory_points
        self.check_victory_points()


    def slip(self, placename, card_to_give_if_sympathy):
        if 'sympathy' in self.map.places[placename].tokens:
            if not card_to_give_if_sympathy and len(self.vagabond.deck.cards) > 0:
                options = self.alliance.take_card_from_a_player_options(self.vagabond)
                card_id = alliance_choose_card(options)
                self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_id))
            if not card_to_give_if_sympathy and len(self.vagabond.deck.cards) == 0:
                self.alliance.supporter_deck.add_card(self.deck.draw_card())
                if len(self.deck.cards) == 0:
                    self.deck = self.discard_deck
                    self.deck.shuffle_deck()
                    self.discard_deck = Deck(empty=True)
            else:
                self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_to_give_if_sympathy.ID))
        self.map.move_vagabond(placename)


    def remove_soldiers_from_vagabond_items(self, items, defender):
        new_items = []
        for item in items:
            if not item == defender:
                new_items.append(item)
        return new_items


    def get_battle_damages(self, attacker, defender, dice_rolls, place_name, armorers: list[bool, bool] = False, sappers:bool = False, brutal_tactics:bool=False, card_ID=None):
        """
        :param attacker: str
        :param defender: str
        :param dice_rolls: list, 2 0-3 nums descending order
        """
        # So vagabond cant attack its own soldiers with its own soldiers
        if attacker == "vagabond":
            if self.vagabond.relations[defender] == "friendly":
                self.vagabond.allied_soldiers = self.remove_soldiers_from_vagabond_items(self.vagabond.allied_soldiers, defender)
                self.vagabond.items_to_damage = self.remove_soldiers_from_vagabond_items(self.vagabond.items_to_damage, defender)


        dmg_attacker = 0
        dmg_defender = 0

        # Regular battle
        if attacker != 'vagabond' and defender != 'vagabond':
            if defender != 'alliance':
                dmg_attacker += min(dice_rolls[0], self.map.places[place_name].soldiers[attacker])
                dmg_defender += min(dice_rolls[1], self.map.places[place_name].soldiers[defender])

            elif defender == 'alliance':
                dmg_attacker += min(dice_rolls[1], self.map.places[place_name].soldiers[attacker])
                dmg_defender += min(dice_rolls[0], self.map.places[place_name].soldiers[defender])

        elif defender == 'vagabond':
                dmg_attacker += min(dice_rolls[0], self.map.places[place_name].soldiers[attacker])
                dmg_defender += min(dice_rolls[1], len(list(item for item in self.vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(self.vagabond.allied_soldiers))

        elif attacker == 'vagabond':
            if defender != 'alliance':
                dmg_attacker += min(dice_rolls[0], len(list(item for item in self.vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(self.vagabond.allied_soldiers))
                dmg_defender += min(dice_rolls[1], self.map.places[place_name].soldiers[defender])

            elif defender == 'alliance':
                dmg_attacker += min(dice_rolls[1], len(list(item for item in self.vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(self.vagabond.allied_soldiers))
                dmg_defender += min(dice_rolls[0], self.map.places[place_name].soldiers[defender])

        if armorers[0]:
            for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
                if actor.name == attacker:
                    actor.armorers = False
                    self.discard_deck.add_card(actor.persistent_effect_deck.get_a_card_like_it("armorers"))
            dmg_defender = 0

        if armorers[1]:
            for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
                if actor.name == defender:
                    actor.armorers = False
                    self.discard_deck.add_card(actor.persistent_effect_deck.get_a_card_like_it("armorers"))
            dmg_attacker = 0        

        # No defender
        if  defender != 'vagabond' and self.map.places[place_name].soldiers[defender] == 0:
            dmg_attacker = min(dmg_attacker, 1)

        if sappers:
            for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
                if actor.name == defender:
                    actor.sappers = False
                    self.discard_deck.add_card(actor.persistent_effect_deck.get_a_card_like_it("sappers"))
            dmg_defender += 1

        if brutal_tactics:
            dmg_attacker += 1


        for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
            # OWL
            if attacker == 'bird' and actor.name == 'bird' and actor.leader == 'Commander':
                dmg_attacker += 1
            if brutal_tactics and actor.name == defender:
                actor.victory_points += 1

        if card_ID:
            self.eyrie.remove_from_temp_decree(card_ID, 'battle')

        self.check_victory_points()
        return dmg_attacker, dmg_defender


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

    def resolve_battle(self, place, attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces=None, defender_chosen_pieces=None, card_to_give_if_sympathy=None):
        """
        :param self.map: Map
        :param place_name: str
        :param attacker: str
        :param defender: str
        :param dice_rolls: list, 2 0-3 nums descending order
        :param marquise: Marquise
        :param eyrie: Eyrie
        :param alliance: Alliance
        :param vagabond: Vagabond
        :param discard_deck: DiscardDeck
        :param vagabond_items: list, items to damage
        """ 
        if attacker != "vagabond" and place.soldiers[attacker] == 0:
            logging.debug("No attacker because no soldiers")
            return
        
        # So vagabond cant attack its allies with its allies
        if attacker == "vagabond":
            if self.vagabond.relations[defender] == "friendly":
                self.vagabond.allied_soldiers = self.remove_soldiers_from_vagabond_items(self.vagabond.allied_soldiers, defender)
                self.vagabond.items_to_damage = self.remove_soldiers_from_vagabond_items(self.vagabond.items_to_damage, defender)

        victory_points_attacker = 0
        victory_points_defender = 0
        sympathy_killed = False

        # Process attacker's damage
        if defender == "vagabond":
            logging.debug("Vagabond getting {self.vagabond.items_to_damage[:dmg_attacker} damaged")
            for item in self.vagabond.items_to_damage[:dmg_attacker]:
                self.vagabond.damage_item(item)
        else:
            # If attacker dealt more damage than defender's soldiers, remove additional pieces
            extra_dmg_attacker = max(dmg_attacker - place.soldiers[defender], 0)

            # Accounting for the killed soldiers
            if attacker == "vagabond": 
                logging.debug(f"vagabond is getting {dmg_attacker-extra_dmg_attacker} points")
                victory_points_attacker += dmg_attacker-extra_dmg_attacker
            # If a defender soldier dies while set relations to hostile
            if attacker == "vagabond" and dmg_attacker-extra_dmg_attacker > 0 and self.vagabond.relations[defender] != "hostile":
                logging.debug(f"vagabond became hostile with {defender}")
                self.vagabond.relations[defender] = "hostile"
                victory_points_attacker-=1 # THAT one soldier doesn't count as VP
            if extra_dmg_attacker <=0:
                logging.debug(f"{defender} lost {dmg_attacker} soldiers")
                place.soldiers[defender] -= dmg_attacker
            else:
                place.soldiers[defender] = 0
                for piece in defender_chosen_pieces[:extra_dmg_attacker]:
                    if piece[1] == "building":
                        place.remove_building(piece[0])
                        victory_points_attacker += 1
                        if attacker == "vagabond" and self.vagabond.relations[defender] == "hostile":
                            victory_points_attacker += 1
                        if piece[0] == 'base':
                            self.alliance.losing_a_base(place_suit=place.suit, discard_deck=self.discard_deck)
                        if piece[0] == 'sawmill' or piece[0] == 'workshop' or piece[0] == 'recruiter':
                            logging.debug(f"Marquise lost {buildings_list_marquise[piece[0]]['VictoryPoints'][self.map.count_on_map(('building', piece[0]))+1]} VPs, as it lost a {piece[0]}")
                            self.marquise.victory_points -= buildings_list_marquise[piece[0]]["VictoryPoints"][self.map.count_on_map(("building", piece[0]))+1] # +1 because we already removed the building
                    elif piece[1] == "token":
                        logging.debug(f"{defender} lost {piece[0]}")
                        place.tokens.remove(piece[0])
                        victory_points_attacker += 1
                        if attacker == "vagabond" and self.vagabond.relations[defender] == "hostile":
                            victory_points_attacker += 1
                        if piece[0] == "sympathy":
                            sympathy_killed = True
                            self.alliance.victory_points -= sympathy_VPs[self.map.count_on_map(("token", "sympathy"))+1]


        # Process defender's damage
        if attacker == "vagabond":
            items = 0
            soldiers = 0
            for item in self.vagabond.items_to_damage[:dmg_defender]:
                self.vagabond.damage_item(item, place)
                if isinstance(item, Item):
                    items += 1
                else:
                    soldiers += 1
            if soldiers > items:
                self.vagabond.relations[item] = "hostile"

        else:
            # If defender dealt more damage than attacker's soldiers, remove additional pieces
            extra_dmg_defender = max(dmg_defender - place.soldiers[attacker], 0)
            if defender == "vagabond" and dmg_defender-extra_dmg_defender > 0:
                self.vagabond.relations[attacker] = "hostile"

            if extra_dmg_defender <=0:
                place.soldiers[attacker] -= dmg_defender
            else:
                place.soldiers[attacker] = 0
                for piece in attacker_chosen_pieces[:extra_dmg_defender]:
                    if piece[1] == "building":
                        place.remove_building(piece[0])
                        victory_points_defender += 1
                        if piece[0] == 'sawmill' or piece[0] == 'workshop' or piece[0] == 'recruiter':
                            logging.debug(f"Marquise lost {buildings_list_marquise[piece[0]]['VictoryPoints'][self.map.count_on_map(('building', piece[0]))+1]} VPs, as it lost a {piece[0]}")
                            self.marquise.victory_points -= buildings_list_marquise[piece[0]]["VictoryPoints"][self.map.count_on_map(("building", piece[0]))+1] # +1 because we already removed the building
                    elif piece[1] == "token":
                        logging.debug(f"{attacker} lost {piece[0]}")
                        place.tokens.remove(piece[0])
                        victory_points_defender += 1
                        if piece[0] == "sympathy":
                            sympathy_killed = True
                            self.alliance.victory_points -= sympathy_VPs[self.map.count_on_map(("token", "sympathy"))+1]

        for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
            if actor.name == attacker:
                actor.victory_points += victory_points_attacker
                if actor.name != "alliance":
                    if sympathy_killed and card_to_give_if_sympathy:
                        logging.debug(f"alliance is getting {card_to_give_if_sympathy}")
                        self.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID)) # CORRECT ASSUMING card_to_give_if_no_sympathy is correct
                    if sympathy_killed and not card_to_give_if_sympathy:
                        if len(actor.deck.cards) == 0:
                            logging.debug(f"alliance drew a card from the deck")
                            self.alliance.supporter_deck.add_card(self.deck.draw_card())
                        else:
                            logging.debug(f"alliance choose a card")
                            options = self.alliance.take_card_from_a_player_options(self.vagabond)
                            card_id = alliance_choose_card(options)
                            self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_id))


            elif actor.name == defender:
                actor.victory_points += victory_points_defender
                if actor.name != "alliance":
                    if sympathy_killed and card_to_give_if_sympathy:
                        self.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID)) # CORRECT ASSUMING card_to_give_if_no_sympathy is correct
                    if sympathy_killed and not card_to_give_if_sympathy:
                        if len(actor.deck.cards) == 0:
                            self.alliance.supporter_deck.add_card(self.deck.draw_card())
                        else:  
                            options = self.alliance.take_card_from_a_player_options(self.vagabond)
                            card_id = alliance_choose_card(options)
                            self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_id))


        place.update_owner()
        if len(self.deck.cards) <=0:
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)
        self.check_victory_points()


    def move(self, move_action, card_to_give_if_sympathy):
        if move_action.who != 'vagabond':
            self.map.places[move_action.start].soldiers[move_action.who] -= move_action.how_many
            self.map.places[move_action.end].soldiers[move_action.who] += move_action.how_many

        if move_action.who != 'alliance' and self.map.places[move_action.end].tokens.count("sympathy") > 0:
            for actor in [self.eyrie, self.vagabond, self.marquise]:
                if actor.name == move_action.who and card_to_give_if_sympathy:
                    self.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID))
                elif actor.name == move_action.who and not card_to_give_if_sympathy and len(actor.deck.cards) == 0:
                    self.alliance.supporter_deck.add_card(self.deck.draw_card())
                elif actor.name == move_action.who and not card_to_give_if_sympathy and len(actor.deck.cards) > 0:
                    options = self.alliance.take_card_from_a_player_options(self.vagabond)
                    card_id = alliance_choose_card(options)
                    self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_id))

        if len(self.deck.cards) <= 0:
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)

        if move_action.who == 'vagabond':
            self.map.move_vagabond(move_action.end)
            boot_cost = 2 if self.vagabond.relations[self.map.places[move_action.end].owner] == 'hostile' else 1
            for _ in range(boot_cost):
                self.vagabond.exhaust_item(Item('boot'))
            if move_action.vagabond_allies[0]:
                self.map.places[move_action.start].soldiers[move_action.vagabond_allies[1]] -= move_action.vagabond_allies[0]
                self.map.places[move_action.end].soldiers[move_action.vagabond_allies[1]] += move_action.vagabond_allies[0]

        if move_action.who == 'alliance':
            for actor in [self.eyrie, self.vagabond, self.marquise]:
                if actor.name == move_action.who:
                    actor.current_officers -= 1

        if move_action.who == "bird":
            self.eyrie.remove_from_temp_decree(move_action.card_ID, 'move')

        self.map.update_owners()

    def craft(self, actor, costs: CraftDTO):
        if costs.card.craft == "ambush":
            raise ValueError("Ambush is not a craftable card")

        if costs.cost == "anything": # Royal claim card, Making the AI choose what to deactivate is too much work for now
            i = 4
            for _ in range(i):
                for key in actor.craft_activations.keys():
                    if not i:
                        break
                    if actor.craft_activations[key] > 0:
                        actor.craft_activations[key] -= 1
                        i -= 1
                if not i:
                    break
        elif costs.cost:
            actor.deactivate(costs.cost)

        if isinstance(costs.card.craft, Item):
            actor.add_item(costs.card.craft)
            self.map.craftables.remove(costs.card.craft)
            if actor.name == "bird" and actor.leader!= "Builder":
                actor.victory_points += 1
            else:
                actor.victory_points += costs.card.craft.crafting_reward()
            self.check_victory_points()
            self.discard_deck.add_card(actor.deck.get_the_card(costs.card.ID))


        elif costs.card.craft in persistent_effects:
            # Persistent effects
            if costs.card.craft == "cobbler":
                actor.cobbler = True
            if costs.card.craft == "tax_collector":
                actor.tax_collector = True
            if costs.card.craft == "armorers":
                actor.armorers = True
            if costs.card.craft == "sappers":
                actor.sappers = True
            if costs.card.craft == "command_warren":
                actor.command_warren = True
            if costs.card.craft == "scouting_party":
                actor.scouting_party = True
            if costs.card.craft == "codebreakers":
                actor.codebreakers = True
            if costs.card.craft == "stand_and_deliver":
                actor.stand_and_deliver = True
            if costs.card.craft == "better_burrow_bank":
                actor.better_burrow_bank = True
            if costs.card.craft == "royal_claim":
                actor.royal_claim = True
            if costs.card.craft == "brutal_tactics":
                actor.brutal_tactics = True
            actor.persistent_effect_deck.add_card(actor.deck.get_the_card(costs.card.ID))
        # special effects
        elif costs.card.craft == "favor":
                self.favor(actor, costs.card.craft_suit)
                self.discard_deck.add_card(actor.deck.get_the_card(costs.card.ID))
        elif costs.card.craft == "dominance":
                self.dominance(actor, costs.card.card_suit)
                actor.deck.get_the_card(costs.card.ID) # remove from the game

    def count_lost_points_marquise(self, place):
        lost_points = 0
        lost_sawmills = 0
        lost_workshops = 0
        lost_recruiters = 0
        for slot in place.building_slots:
            if slot[0] == "sawmill":
                lost_sawmills += 1
            elif slot[0] == "workshop":
                lost_workshops += 1
            elif slot[0] == "recruiter":
                lost_recruiters += 1

        for i in range(lost_sawmills):
            lost_points += buildings_list_marquise['sawmill']["VictoryPoints"][self.map.count_on_map(("building", 'sawmill'))-i]
        for i in range(lost_workshops):
            lost_points += buildings_list_marquise['workshop']["VictoryPoints"][self.map.count_on_map(("building", 'workshop'))-i]
        for i in range(lost_recruiters):
            lost_points += buildings_list_marquise['recruiter']["VictoryPoints"][self.map.count_on_map(("building", 'recruiter'))-i]
        logging.debug(f"Marquise lost {lost_points} points")
        self.marquise.victory_points -= lost_points
    
        
    def favor(self, actor, suit):
        victory_points = 0
        for place in self.map.places.values():
            if place.suit == suit:
                for key in place.soldiers.keys():
                    if key != actor.name and key != "vagabond":
                        place.soldiers[key] = 0
                if ('base', 'alliance') in place.building_slots and actor.name != "alliance":
                    self.alliance.losing_a_base(place_suit=place.suit, discard_deck=self.discard_deck)
                if actor.name != 'marquise':
                    self.count_lost_points_marquise(place)
                if actor.name != "vagabond" and place.vagabond_is_here:
                    for item in self.vagabond.items_to_damage[:3]:
                        self.vagabond.damage_item(item)
                victory_points += place.clear_buildings(exception_faction=actor.name)
                victory_points += place.clear_tokens(exception_faction=actor.name)
        actor.victory_points += victory_points
        self.check_victory_points()
        self.map.update_owners()



    def dominance(self, user, suit):
        if user == "vagabond":
            min_points = 100
            min_point_actorname = None
            for actor in [self.eyrie, self.marquise, self.alliance]:
                if actor != "vagabond" and actor.win_condition != "coalition_major":
                    if actor.victory_points < min_points:
                        min_points = actor.victory_points
                        min_point_actorname = actor.name

            for actor in [self.eyrie, self.marquise, self.alliance]:
                if actor.name == min_point_actorname:
                    actor.win_condition = "coalition_major"
            user.win_condition = "coalition_minor"
        else:
            user.win_condition = suit


    def ambush(self, place, attacker, defender, bird_or_suit_defender, bird_or_suit_attacker):
        if bird_or_suit_defender == "suit":
            for card in defender.deck.cards:
                if card.craft == "ambush" and card.card_suit == place.suit:
                    self.discard_deck.add_card(defender.deck.get_the_card(card.ID))
        if bird_or_suit_defender == "bird":
            for card in defender.deck.cards:
                if card.craft == "ambush" and card.card_suit == "bird":
                    self.discard_deck.add_card(defender.deck.get_the_card(card.ID))

        if bird_or_suit_attacker or attacker.scouting_party:
            if not attacker.scouting_party and bird_or_suit_attacker == "suit":
                for card in attacker.deck.cards:
                    if card.craft == "ambush" and card.card_suit == place.suit:
                        self.discard_deck.add_card(attacker.deck.get_the_card(card.ID))
            if not attacker.scouting_party and bird_or_suit_attacker == "bird":
                for card in attacker.deck.cards:
                    if card.craft == "ambush" and card.card_suit == "bird":
                        self.discard_deck.add_card(attacker.deck.get_the_card(card.ID))
            return

        if attacker.name == "vagabond":
            for item in self.vagabond.items_to_damage[:2]:
                self.vagabond.damage_item(item)

        else:
            place.soldiers[attacker.name] -= 2 
            place.soldiers[attacker.name] = max(place.soldiers[attacker.name], 0)
        place.update_owner()

    def build(self, place, actor, building, cost = 0, card_ID=None):
        if actor.name == "bird":
            actor.remove_from_temp_decree(card_ID, "build")
        if actor.name == "cat": #Choosing which woods to remove is too much work for now
            i = cost
            for _ in range(i):
                for place in self.map.places.values():
                    if not i:
                        break
                    if "wood" in place.tokens and place.owner == 'cat':
                        place.tokens.remove("wood")
                        i -= 1
                if not i:
                    break

            actor.victory_points += buildings_list_marquise[building]["VictoryPoints"][self.map.count_on_map(("building", building))]
        for i in range(len(place.building_slots)):
            if place.building_slots[i] == ("empty", "No one"):
                place.building_slots[i] = (building, actor.name)
                break
        place.update_owner()
        self.check_victory_points()

    def recruit_cat(self):
        for place in self.map.places.values():
            if ("recruiter", "cat") in place.building_slots and sum([place.soldiers["cat"] for place in self.map.places.values()]) < 25:
                place.soldiers["cat"] += 1
        self.map.update_owners()

    def recruit(self, place, actor, card_ID = None):
        if actor.name == "bird" and actor.leader == "Charismatic":
            place.soldiers[actor.name] += 2
            place.update_owner()   
        else:
            place.soldiers[actor.name] += 1
            place.update_owner()
        
        if actor.name == "alliance":
            self.alliance.current_officers -= 1
        
        if actor.name == "bird":
            self.eyrie.remove_from_temp_decree(card_ID, 'recruit')

    def overwork(self, placename, card_id):
        self.map.places[placename].tokens += ['wood']
        if total_common_card_info[card_id][2] == "dominance":
            self.dominance_discard_deck.add_card(self.marquise.deck.get_the_card(card_id))
        else:
            self.discard_deck.add_card(self.marquise.deck.get_the_card(card_id))

    def eyrie_get_points(self):
        roosts = self.map.count_on_map(("building", "roost"))
        self.eyrie.victory_points += eyrie_roost_VPs[roosts]
        self.check_victory_points()


    def bird_turmoil(self, new_commander):
        
        vp_loss = 0
        for decree_field in self.eyrie.decree.values():
            for value in decree_field:
                if value[1] == 'bird':
                    vp_loss += 1
        self.eyrie.victory_points -= vp_loss
        self.eyrie.victory_points = max(self.eyrie.victory_points, 0)

        self.eyrie.change_role(new_commander)
        self.eyrie.setup_based_on_leader()

        # ALL cards to the discard_deck! Loyal viziers are not here.
        for card in self.eyrie.decree_deck.cards:
            if card.craft == "dominance":
                self.dominance_discard_deck.add_card(self.eyrie.decree_deck.get_the_card(card.ID)) 
            else:
                self.discard_deck.add_card(self.eyrie.decree_deck.get_the_card(card.ID))
        


    def mobilize(self, card_ID):
        self.alliance.supporter_deck.add_card(self.alliance.deck.get_the_card(card_ID))

    def train(self, card_ID):
        if total_common_card_info[card_ID][2] == "dominance":
            self.dominance_discard_deck.add_card(self.alliance.deck.get_the_card(card_ID))
        else:
            self.discard_deck.add_card(self.alliance.deck.get_the_card(card_ID))
        self.alliance.total_officers += 1

    def organize(self, placename):
        symp_count = self.map.count_on_map(("token", "sympathy"), per_suit=False)
        self.map.places[placename].soldiers["alliance"] -= 1
        self.map.places[placename].tokens += ["sympathy"]
        self.alliance.victory_points += sympathy_VPs[symp_count]
        self.check_victory_points()

    # Vagabond
    def explore_ruin(self, placename):
        for i in range(len(self.map.places[placename].building_slots)):
            if self.map.places[placename].building_slots[i][0] == "ruin":
                self.vagabond.add_item(self.map.places[placename].building_slots[i][1])
                self.map.places[placename].building_slots[i] = ("empty", "No one")
                self.vagabond.satchel[self.vagabond.satchel.index(Item('torch'))].exhausted = True
                self.vagabond.victory_points += 1
                self.check_victory_points()
                return
        raise ValueError("Try to explore but no ruin")

    def aid(self, other_player, choosen_card_id, choosen_item, consequitive_aids):

        other_player.deck.add_card(self.vagabond.deck.get_the_card(choosen_card_id))

        if choosen_item is not None:
            other_player.items.remove(choosen_item)
            self.vagabond.add_item(choosen_item)
        
        if self.vagabond.relations[other_player.name] == "friendly":
            self.vagabond.victory_points += 2
            self.check_victory_points()
            return 0
        
        if self.vagabond.relations[other_player.name] == "hostile":
            raise ValueError("You can't aid a hostile player")

        if self.vagabond.relations[other_player.name] == "indifferent":
            self.vagabond.victory_points += 1
            self.check_victory_points()
            self.vagabond.relations[other_player.name] = "good"
            return 0

        if self.vagabond.relations[other_player.name] == "good" and consequitive_aids == 1:
            self.vagabond.victory_points += 2
            self.check_victory_points()
            self.vagabond.relations[other_player.name] = "very good"
            return 0

        if self.vagabond.relations[other_player.name] == "very good" and consequitive_aids == 2:
            self.vagabond.victory_points += 2
            self.check_victory_points()
            self.vagabond.relations[other_player.name] = "friendly"
            return 0
        
        return consequitive_aids + 1 # Reset at the end of every vagabond turn

    def steal(self, other_player_name):
        for player in [self.marquise, self.alliance, self.eyrie]:
            if player.name == other_player_name:
                player.deck.shuffle_deck()
                self.vagabond.deck.add_card(player.deck.draw_card())
                player.deck.cards.sort(key=lambda x: x.ID)
        self.vagabond.satchel[self.vagabond.satchel.index(Item('torch'))].exhausted = True

    def complete_quest(self, quest_card_ID, draw_or_VP):
        self.discard_quest_deck.add_card(self.vagabond.quest_deck.get_the_card(quest_card_ID))
        self.vagabond.quest_deck.add_card(self.quest_deck.draw_card())

        if draw_or_VP == "draw":
            self.vagabond.deck.add_card(self.deck.draw_card())
            if len(self.deck.cards) <=0:
                self.deck = self.discard_deck
                self.deck.shuffle_deck()
                self.discard_deck = Deck(empty=True)
        if draw_or_VP == "VP":
            self.vagabond.victory_points += sum([card.suit == vagabond_quest_card_info[quest_card_ID][-1] for card in self.discard_quest_deck.cards])
            self.check_victory_points()

        item1 = vagabond_quest_card_info[quest_card_ID][1]
        item2 = vagabond_quest_card_info[quest_card_ID][2]
        self.vagabond.exhaust_item(item1)
        self.vagabond.exhaust_item(item2)
        self.vagabond.quest_deck.add_card(self.quest_deck.draw_card())


    def strike(self, placename, opponent, target, card_to_give_if_sympathy):
        if target == "wood" or target == "keep" or target == "sympathy":
            self.map.places[placename].tokens.remove(target)
            self.vagabond.victory_points += 1
            self.check_victory_points()
            if target == "sympathy" and card_to_give_if_sympathy:
                self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_to_give_if_sympathy))
            if target == "sympathy" and not card_to_give_if_sympathy and len(self.vagabond.deck.cards) == 0:
                self.alliance.supporter_deck.add_card(self.deck.draw_card())
                if len(self.deck.cards) <= 0:
                    self.deck = self.discard_deck
                    self.deck.shuffle_deck()
                    self.discard_deck = Deck(empty=True)
            if target == "sympathy" and not card_to_give_if_sympathy and len(self.vagabond.deck.cards) > 0:
                options = self.alliance.take_card_from_a_player_options(self.vagabond)
                card_id = alliance_choose_card(options)
                self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_id))
            if target == "sympathy":
                self.alliance.victory_points -= sympathy_VPs[self.map.count_on_map(("token", "sympathy"))+1]

        elif target == "soldier":
            self.map.places[placename].soldiers[opponent] -= 1
            self.vagabond.relations[opponent] = "hostile"

        else:
            for i in range(len(self.map.places[placename].building_slots)):
                if self.map.places[placename].building_slots[i][0] == target:
                    self.map.places[placename].building_slots[i] = ("empty", "No one")
                    victory_points += 1
                    self.check_victory_points()
                    if target == 'sawmill' or target == 'workshop' or target == 'recruiter':
                        self.marquise.victory_points -= buildings_list_marquise[target]["VictoryPoints"][self.map.count_on_map(("building", target))+1] # +1 because we already removed the building
                    if target == 'base':
                        self.alliance.losing_a_base(place_suit=self.map.places[placename].suit, discard_deck=self.discard_deck)
                    break
        self.map.places[placename].update_owner()
        
