from actors import Marquise, Eyrie, Alliance, Vagabond
from item import Item
from dtos import MoveDTO, CraftDTO, Battle_DTO, OverworkDTO
from map import build_regular_forest
from deck import Deck, QuestDeck
from configs import sympathy_VPs, eyrie_roost_VPs, persistent_effects, Immediate_non_item_effects, eyrie_leader_config, buildings_list_marquise, vagabond_quest_card_info
import random



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
            self.quest_deck = QuestDeck()
            self.discard_quest_deck = QuestDeck(empty=True)

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


            # VAGABOND_STUFF
        else:
            vagabond_roles = ["Thief"] # ["Thief", "Ranger", "Tinkerer"]
            eyrie_leaders = ["Despot", "Commander", "Charismatic", "Builder"]

            self.marquise = Marquise(map=self.map)
            self.eyrie = Eyrie(map=self.map, role=random.choice(eyrie_leaders))
            self.alliance = Alliance(map=self.map)
            self.vagabond = Vagabond(map=self.map, role=random.choice(vagabond_roles))

            self.deck = Deck()
            self.discard_deck = Deck(empty=True)
            self.quest_deck = QuestDeck()
            self.discard_quest_deck = QuestDeck(empty=True)

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
        if victim == "No one":
            return
        victim.deck.shuffle_deck()
        taker.deck.add_card(victim.deck.draw_card())
        victim.victory_points += 1

    def better_burrow_bank(self, actor, other):
        actor.deck.add_card(self.deck.draw_card())
        if len(self.deck.cards) >= 0: # DECK ONE LINER
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)
        other.deck.add_card(self.deck.draw_card())

    def codebreakers(self, actor, other):
        actor.known_hands[other.name] = True

    def discard_down_to_five(self, actor):
        card_options = actor.get_card_prios()
        card_choices = choose_card_prios(card_options)
        # pops the last card in the list, which is the lowest priority card
        while len(actor.deck.cards) > 5:
            self.discard_deck.add_card(actor.deck.get_the_card(card_choices.pop()))


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
        self.discard_deck.add_card(self.marquise.deck.get_the_card(cardID))
        if len(self.deck.cards) >= 0: # DECK ONE LINER
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)

    # Alliance
    def revolt(self, place, card_ID1, card_ID2, soldiers_to_gain):
        # Clear all buildings
        victory_points = 0
        victory_points += place.clear_buildings()
        victory_points += place.clear_tokens(exception_faction = "alliance")
        place.clear_soldiers(exception_faction="alliance")

        # Add a base for the alliance
        place.add_building('base', 'alliance')

        # If the vagabond is present, damage 3 vagabond items
        if place.vagabond_is_here:
            for item in self.vagabond.items_to_damage[:3]:
                self.vagabond.damage_item(item)

        self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(card_ID1))
        self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(card_ID2))

        for _ in range(soldiers_to_gain):
            if sum([place.soldiers["alliance"] for place in self.map.places.values()]) + self.alliance.total_officers >= 10:
                break
            place.soldiers["alliance"] += 1

        if sum([place.soldiers["alliance"] for place in self.map.places.values()]) + self.alliance.total_officers <= 10:
            self.alliance.total_officers += 1

        place.update_owner()
        self.alliance.victory_points += victory_points


    def spread_sympathy(self, place_name, card_ids):
        self.map.places[place_name].update_pieces(tokens = self.map.places[place_name].tokens + ['sympathy'])

        for cardID in card_ids:
            if self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(cardID)) is not None:
                raise ValueError("Error in spread_sympathy: card not in supporter deck")

        victory_points = sympathy_VPs[self.map.count_on_map(what_to_look_for=('token', 'sympathy'), per_suit = False)]
        self.alliance.victory_points += victory_points


    def slip(self, place, card_to_give_if_sympathy):
        if 'sympathy' in self.map.places[place.name].tokens:
            if card_to_give_if_sympathy and len(self.vagabond.deck.cards) > 0:
                options = self.alliance.take_card_from_a_player_options(self.vagabond)
                card_id = alliance_choose_card(options)
                self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_id))
            if card_to_give_if_sympathy and len(self.vagabond.deck.cards) == 0:
                self.alliance.supporter_deck.add_card(self.deck.draw_card())
            else:
                self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_to_give_if_sympathy))
        self.map.move_vagabond(place.name)


    def remove_soldiers_from_vagabond_items(self, items, defender):
        new_items = []
        for item in items:
            if not item == defender:
                new_items.append(item)
        return new_items


    def get_battle_damages(self, attacker, defender, dice_rolls, place_name, armorers: list[bool, bool] = False, sappers:bool = False, brutal_tactics:bool=False):
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
            dmg_defender = 0

        if armorers[1]:
            for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
                if actor.name == defender:
                    actor.armorers = False
            dmg_attacker = 0        

        # No defender
        if  defender != 'vagabond' and self.map.places[place_name].soldiers[defender] == 0:
            dmg_attacker = min(dmg_attacker, 1)

        if sappers:
            for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
                if actor.name == defender:
                    actor.sappers = False
            dmg_defender += 1

        if brutal_tactics:
            dmg_attacker += 1


        for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
            # OWL
            if attacker == 'bird' and actor.name == 'bird' and actor.leader == 'Commander':
                dmg_attacker += 1
            if brutal_tactics and actor.name == defender:
                actor.victory_points += 1




        return dmg_attacker, dmg_defender


    def priority_to_list(self, priorities, place, owner):
        """
        :param priority: str
        :return: list
        """
        chosen_pieces = []
        for piece in priorities:
            for token in place.tokens:
                if token == piece:
                    chosen_pieces.append((token, 'token'))
            for building_slot in place.building_slots:
                if building_slot[0] == piece and building_slot[1] == owner:
                    chosen_pieces.append((building_slot[0], 'building'))

        return chosen_pieces

    def resolve_battle(self, place, attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces=None, defender_chosen_pieces=None, card_to_give_if_sympathy=None, card_ID=None):
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
        if attacker == "alliance":
            self.alliance.current_officers -= 1
        if attacker != "vagabond" and place.soldiers[attacker] == 0:
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
            for item in self.vagabond.items_to_damage[:dmg_attacker]:
                self.vagabond.damage_item(item)
        else:
            # If attacker dealt more damage than defender's soldiers, remove additional pieces
            extra_dmg_attacker = max(dmg_attacker - place.soldiers[defender], 0)

            # Accounting for the killed soldiers
            if attacker == "vagabond": 
                victory_points_attacker += dmg_attacker-extra_dmg_attacker
            # If a defender soldier dies while set relations to hostile
            if attacker == "vagabond" and dmg_attacker-extra_dmg_attacker > 0 and self.vagabond.relations[defender] != "hostile":
                self.vagabond.relations[defender] = "hostile"
                victory_points_attacker-=1 # THAT one soldier doesn't count as VP
            if extra_dmg_attacker <=0:
                place.soldiers[defender] -= dmg_attacker
            else:
                place.soldiers[defender] = 0
                for piece in defender_chosen_pieces[:extra_dmg_attacker]:
                    if piece[1] == "building":
                        place.remove_building(piece[0])
                        victory_points_attacker += 1
                        if attacker == "vagabond" and self.vagabond.relations[defender] == "hostile":
                            victory_points_attacker += 1
                        if piece[0] == 'sawmill' or piece[0] == 'workshop' or piece[0] == 'recruiter':
                            self.marquise.victory_points -= buildings_list_marquise[piece[0]]["VictoryPoints"][self.map.count_on_map(("building", piece[0]))+1] # +1 because we already removed the building
                    elif piece[1] == "token":
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
                            self.marquise.victory_points -= buildings_list_marquise[piece[0]]["VictoryPoints"][self.map.count_on_map(("building", piece[0]))+1] # +1 because we already removed the building
                    elif piece[1] == "token":
                        place.tokens.remove(piece[0])
                        victory_points_defender += 1
                        if piece[0] == "sympathy":
                            sympathy_killed = True
                            self.alliance.victory_points -= sympathy_VPs[self.map.count_on_map(("token", "sympathy"))+1]

        for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
            if actor.name == attacker and actor.name != "alliance":
                actor.victory_points += victory_points_attacker
                if sympathy_killed and card_to_give_if_sympathy:
                    self.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID)) # CORRECT ASSUMING card_to_give_if_no_sympathy is correct
                if sympathy_killed and not card_to_give_if_sympathy:
                    if len(actor.deck.cards) == 0:
                        self.alliance.supporter_deck.add_card(self.deck.draw_card())
                    else:  
                        options = self.alliance.take_card_from_a_player_options(self.vagabond)
                        card_id = alliance_choose_card(options)
                        self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_id))


            elif actor.name == defender and actor.name != "alliance":
                actor.victory_points += victory_points_defender
                if sympathy_killed and card_to_give_if_sympathy:
                    self.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID)) # CORRECT ASSUMING card_to_give_if_no_sympathy is correct
                if sympathy_killed and not card_to_give_if_sympathy:
                    if len(actor.deck.cards) == 0:
                        self.alliance.supporter_deck.add_card(self.deck.draw_card())
                    else:  
                        options = self.alliance.take_card_from_a_player_options(self.vagabond)
                        card_id = alliance_choose_card(options)
                        self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_id))

        if attacker == "bird":
            self.eyrie.remove_from_temp_decree(card_ID, "battle")

        place.update_owner()
        if len(self.deck.cards) <=0:
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)


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

        if costs.card.craft == "dominance":
            actor.deck.get_the_card(costs.card.ID)
        else:
            self.discard_deck.add_card(actor.deck.get_the_card(costs.card.ID))
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

        else:
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
            # Immidiate effects
            if costs.card.craft == "favor":
                self.favor(actor, costs.card.craft_suit)
            if costs.card.craft == "dominance":
                self.dominance(actor, costs.card.card_suit)


    def favor(self, actor, suit):
        victory_points = 0
        for place in self.map.places.values():
            if place.suit == suit:
                for key in place.soldiers.keys():
                    if key != actor.name and key != "vagabond":
                        place.soldiers[key] = 0
                if actor.name != "vagabond" and place.vagabond_is_here:
                    for item in self.vagabond.items_to_damage[:3]:
                        self.vagabond.damage_item(item)
                victory_points += place.clear_buildings(exception_faction=actor.name)
                victory_points += place.clear_tokens(exception_faction=actor.name)
        actor.victory_points += victory_points
        self.map.update_owners()



    def dominance(self, user, suit):
        if user == "vagabond":
            min_points = 100
            min_point_actorname = None
            for actor in [self.eyrie, self.marquise, self.alliance]:
                if actor != "vagabond":
                    if actor.victory_points < min_points:
                        min_points = actor.victory_points
                        min_point_actorname = actor.name

            for actor in [self.eyrie, self.marquise, self.alliance]:
                if actor.name == min_point_actorname:
                    actor.win_condition = "coalition"
            user.win_condition = "coalition"
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

    def overwork(self, place, card_id):
        place.tokens += ['wood']
        self.discard_deck.add_card(self.marquise.deck.get_the_card(card_id))

    def eyrie_get_points(self):
        roosts = self.map.count_on_self.map(("building", "roost"))
        self.eyrie.victory_points += eyrie_roost_VPs[roosts]


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
        for _ in range(len(self.eyrie.decree_deck.cards)):
            self.discard_deck.add_card(self.eyrie.decree_deck.draw_card())
        
    


    def spread_symp(self, place, cost):
        symp_count = self.map.count_on_self.map(("token", "sympathy"), per_suit=False)
        place.tokens.append("sympathy")
        for i in range(len(cost)):
            self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(cost[i]))

        self.alliance.victory_points += sympathy_VPs[symp_count]
        place.update_owner()


    def mobilize(self, card_ID):
        self.alliance.supporter_deck.add_card(self.alliance.deck.get_the_card(card_ID))

    def train(self, card_ID):
        self.discard_deck.add_card(self.alliance.deck.get_the_card(card_ID))
        self.alliance.total_officers += 1

    def organize(self, placename):
        symp_count = self.map.count_on_map(("token", "sympathy"), per_suit=False)
        self.map.places[placename].soldiers["alliance"] -= 1
        self.map.places[placename].tokens += ["sympathy"]
        self.alliance.victory_points += sympathy_VPs[symp_count]
        self.alliance.current_officers -= 1

    # Vagabond
    def explore_ruin(self, placename):
        for i in range(len(self.map.places[placename].building_slots)):
            if self.map.places[placename].building_slots[i][0] == "ruin":
                self.vagabond.add_item(self.map.places[placename].building_slots[i][1])
                self.map.places[placename].building_slots[i] = ("empty", "No one")
                self.vagabond.satchel[self.vagabond.satchel.index(Item('torch'))].exhausted = True
                self.vagabond.victory_points += 1
                return
        raise ValueError("Try to explore but no ruin")

    def aid(self, other_player, choosen_card_id, choosen_item, consequitive_aids):

        other_player.deck.add_card(self.vagabond.deck.get_the_card(choosen_card_id))

        if choosen_item is not None:
            other_player.items.remove(choosen_item)
            self.vagabond.add_item(choosen_item)
        
        if self.vagabond.relations[other_player.name] == "friendly":
            self.vagabond.victory_points += 2
            return 0
        
        if self.vagabond.relations[other_player.name] == "hostile":
            raise ValueError("You can't aid a hostile player")

        if self.vagabond.relations[other_player.name] == "indifferent":
            self.vagabond.victory_points += 1
            self.vagabond.relations[other_player.name] = "good"
            return 0

        if self.vagabond.relations[other_player.name] == "good" and consequitive_aids == 1:
            self.vagabond.victory_points += 2
            self.vagabond.relations[other_player.name] = "very good"
            return 0

        if self.vagabond.relations[other_player.name] == "very good" and consequitive_aids == 2:
            self.vagabond.victory_points += 2
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

        item1 = vagabond_quest_card_info[quest_card_ID][1]
        item2 = vagabond_quest_card_info[quest_card_ID][2]
        self.vagabond.exhaust_item(item1)
        self.vagabond.exhaust_item(item2)
        self.vagabond.quest_deck.add_card(self.quest_deck.draw_card())


    def strike(self, placename, opponent, target, card_to_give_if_sympathy):
        if target == "wood" or target == "keep" or target == "sympathy":
            self.map.places[placename].tokens.remove(target)
            self.vagabond.victory_points += 1
            if target == "sympathy" and card_to_give_if_sympathy:
                self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_to_give_if_sympathy))
            if target == "sympathy" and not  card_to_give_if_sympathy:
                self.alliance.supporter_deck.add_card(self.deck.draw_card())
                if len(self.deck.cards) <= 0:
                    self.deck = self.discard_deck
                    self.deck.shuffle_deck()
                    self.discard_deck = Deck(empty=True)
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
                    if target == 'sawmill' or target == 'workshop' or target == 'recruiter':
                        self.marquise.victory_points -= buildings_list_marquise[target]["VictoryPoints"][self.map.count_on_map(("building", target))+1] # +1 because we already removed the building
                    break
        self.map.places[placename].update_owner()
        
def random_choose(options):
    return random.choice(options)

# ALLIANCE PICK AND CHOOSE CARD
def alliance_choose_card(options):
    return random_choose(options)

def choose_card_prios(card_IDS):
    return random.shuffle(card_IDS)

#BATTLE HELPER FUNCTIONS
def get_loss_prios(actor_name):
    if actor_name == 'bird':
        return ['roost']
    if actor_name == 'cat':
        options = ['sawmill', 'workshop', 'recruiter', 'wood', 'keep']
        random.shuffle(options)
        return options
    if actor_name == 'alliance':
        return ['sympathy', "base"]
    if actor_name == 'vagabond':
        return []
    
def roll_dice():
    dice1 = random.randint(0,3)
    dice2 = random.randint(0,3)
    return [dice1, dice2]

def get_sappers_usage(defender_name, game):
    for actor in [game.marquise, game.alliance, game.eyrie, game.vagabond]:
        if actor.name == defender_name:
            return actor.get_sappers_options()
    
def get_ambush_usage(defender_name, game, placename):
    for actor in [game.marquise, game.alliance, game.eyrie, game.vagabond]:
        if actor.name == defender_name:
            ambush_options = actor.get_ambush_options(game.map.places[placename])
    return ambush_options


def battle_cat(game, option):
    # AMBUSH
    ambush_options_defender = get_ambush_usage(option.against_whom, game, option.where)
    ambush_option = random_choose(ambush_options_defender)
    if ambush_option:
        options_attacker = game.marquise.get_ambush_options(game.map.places[option.where])
        game.ambush(place = option.where, attacker=game.marquise, defender=game.eyrie, bird_or_suit_defender=ambush_options_defender[1], bird_or_suit_attacker=options_attacker[0])
    # BATTLE
    if option.against_whom == 'vagabond':
        game.vagabond.get_item_dmg_options()
    dice_rolls = roll_dice()
    card_to_give_if_sympathy = game.marquise.card_to_give_to_alliace_options(game.map.places[option.where].suit)
    attacker_chosen_pieces = game.priority_to_list(get_loss_prios('cat'), option.where, 'cat')
    defender_chosen_pieces = game.priority_to_list(get_loss_prios(option.against_whom), option.where, option.against_whom)
    dmg_attacker, dmg_defender = game.get_battle_damages('cat', option.against_whom, dice_rolls, option.where, sappers = get_sappers_usage(option.against_whom, game), armorers = option.armorer_usage, brutal_tactics = option.brutal_tactics_usage)
    game.resolve_battle(option.where, 'cat', option.against_whom, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_sympathy)

def battle_bird(game, option):
    # AMBUSH
    ambush_options_defender = get_ambush_usage(option.against_whom, game, option.where)
    ambush_option = random_choose(ambush_options_defender)
    if ambush_option:
        options_attacker = game.eyrie.get_ambush_options(game.map.places[option.where])
        game.ambush(place = option.where, attacker=game.marquise, defender=game.eyrie, bird_or_suit_defender=ambush_options_defender[1], bird_or_suit_attacker=options_attacker[0])
    # BATTLE
    if option.against_whom == 'vagabond':
        game.vagabond.get_item_dmg_options()
    dice_rolls = roll_dice()
    card_to_give_if_sympathy = game.marquise.card_to_give_to_alliace_options(game.map.places[option.where].suit)
    attacker_chosen_pieces = game.priority_to_list(get_loss_prios('bird'), option.where, 'bird')
    defender_chosen_pieces = game.priority_to_list(get_loss_prios(option.against_whom), option.where, option.against_whom)
    dmg_attacker, dmg_defender = game.get_battle_damages('bird', option.against_whom, dice_rolls, option.where, sappers = get_sappers_usage(option.against_whom, game), armorers = option.armorer_usage, brutal_tactics = option.brutal_tactics_usage, card_ID = option.card_ID)
    game.resolve_battle(option.where, 'bird', option.against_whom, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_sympathy)

def battle_alliance(game, option):
    # AMBUSH
    ambush_options_defender = get_ambush_usage(option.against_whom, game, option.where)
    ambush_option = random_choose(ambush_options_defender)
    if ambush_option:
        options_attacker = game.alliance.get_ambush_options(game.map.places[option.where])
        game.ambush(place = option.where, attacker=game.alliance, defender=game.eyrie, bird_or_suit_defender=ambush_options_defender[1], bird_or_suit_attacker=options_attacker[0])
    # BATTLE
    if option.against_whom == 'vagabond':
        game.vagabond.get_item_dmg_options()
    dice_rolls = roll_dice()
    card_to_give_if_sympathy = game.marquise.card_to_give_to_alliace_options(game.map.places[option.where].suit)
    attacker_chosen_pieces = game.priority_to_list(get_loss_prios('alliance'), option.where, 'alliance')
    defender_chosen_pieces = game.priority_to_list(get_loss_prios(option.against_whom), option.where, option.against_whom)
    dmg_attacker, dmg_defender = game.get_battle_damages('alliance', option.against_whom, dice_rolls, option.where, sappers = get_sappers_usage(option.against_whom, game), armorers = option.armorer_usage, brutal_tactics = option.brutal_tactics_usage)
    game.resolve_battle(option.where, 'alliance', option.against_whom, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_sympathy)

def get_all_daylight_option_cat(game, recruited_already=False):
    options = []
    options += game.marquise.get_battles(game.map)
    options += game.marquise.get_moves(game.map)
    if not recruited_already:
        options += game.marquise.get_can_recruit(game.map)
    options += game.marquise.get_build_options(game.map)
    options += game.marquise.get_overwork(game.map)
    return options

def get_all_daylight_option_alliance(game):
    options = [False]
    options += game.alliance.get_options_craft(game.map)
    options += game.alliance.get_mobilize_options()
    options += game.alliance.get_train_options(game.map)
    return options

def get_all_evening_option_alliance(game):
    options = [False]
    options += game.alliance.get_options_craft(game.map)
    options += game.alliance.get_mobilize_options()
    options += game.alliance.get_train_options(game.map)
    return options

def move_and_account_to_sympathy(game, choice):
    card_to_give_if_sympathy = game.marquise.card_to_give_to_alliace_options(game.map.places[choice.where].suit)
    game.move(choice, card_to_give_if_sympathy)


def cat_daylight_actions(game, choice, recruited_already=False):
    recruited = recruited_already
    moved = False
    # BATTLE
    if isinstance(choice, Battle_DTO):
        battle_cat(game, choice)
    # RECRUIT
    elif choice[1] == 'recruit' and not recruited_already:
        recruited = True
        game.recruit_cat()
    # MOVE
    elif isinstance(choice, MoveDTO):
        move_and_account_to_sympathy(game, choice)
        moved = True
    # BUILD
    elif len(choice) == 3:
        game.build(place=choice[0], building=choice[1], actor=game.marquise, cost = choice[2])
    # OVERWORK
    elif isinstance(choice, OverworkDTO):
        game.overwork(choice.place, choice.cardID)
    
    return recruited, moved

def eyrie_birdsong_actions(game):
        # DRAW IF HAND EMPTY
    if len(game.eyrie.deck.cards) == 0:
        game.eyrie.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) >= 0: # DECK ONE LINER
            game.deck = game.discard_deck
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)
    
    # ADD UP TO TWO CARDS TO DECREE
    options = game.eyrie.get_decree_options()
    choice = random_choose(options)
    game.eyrie.add_card_to_decree(*choice)
    options = game.eyrie.get_decree_options()
    options.append(False)
    choice = random_choose(options)
    if choice:
        game.eyrie.add_card_to_decree(*choice)
    options = game.eyrie.get_no_roosts_left_options(game.map)
    if options:
        choice = random_choose(options)
        game.place_roost_if_zero_roost(choice)
        
def eyrie_daylight_actions(game):
    choice = True
    game.eyrie.refresh_craft_activations(game.map)
    while choice:
        options = game.eyrie.get_options_craft(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            game.craft(game.eyrie, choice)

    game.eyrie.refresh_temp_decree()
    turmoil = False

    for _ in range(len(game.eyrie.decrees['recruit'])):
        options = game.eyrie.get_resolve_recruit(game.map)
        if options:
            choice = random_choose(options)
            game.recruit(place = choice[0], actor = game.eyrie, card_ID=choice[1])
        else:
            turmoil = True
            break
    if not turmoil:
        for _ in range(len(game.eyrie.decrees['move'])):
            options = game.eyrie.get_resolve_move(game.map)
            if options:
                choice = random_choose(options)
                move_and_account_to_sympathy(game, choice)
            else:
                turmoil = True
                break
    if not turmoil:  
        for _ in range(len(game.eyrie.decrees['battle'])):
            options = game.eyrie.get_resolve_battle(game.map)
            if options:
                choice = random_choose(options)
                battle_bird(game, choice)
            else:
                turmoil = True
                break
    if not turmoil:
        for _ in range(len(game.eyrie.decrees['build'])):
            options = game.eyrie.get_resolve_build(game.map)
            if options:
                choice = random_choose(options)
                game.build(place=choice[0], building="roost", actor=game.eyrie, card_ID = choice[1])
            else:
                turmoil = True
                break
    
    if turmoil:
        options = game.eyrie.get_turmoil_options()
        choice = random_choose(options)
        game.bird_turmoil(choice)
    

def alliance_daylight_actions(game, choice):
    # CRAFT
    if isinstance(choice, CraftDTO):
        game.craft(game.alliance, choice)
    # MOBILIZE
    elif isinstance(choice, int):
        game.mobilize(choice)
    # TRAIN
    elif choice[1] == 'train':
        game.train(choice[0])
    else:
        raise ValueError("Wrong choice in alliance daylight")
    
def alliance_evening_actions(game, choice):
    # BATTLE
    if isinstance(choice, Battle_DTO):
        battle_alliance(game, choice)
    # MOVE
    elif isinstance(choice, MoveDTO):
        game.move(choice)
    # RECRUIT
    elif choice[1] == 'recruit':
        game.recruit(place = choice[0], actor = game.alliance)
    # ORGANIZE
    elif choice[1] == 'organize':
        game.organize(placename = choice[0])
    else:
        raise ValueError("Wrong choice in alliance evening")