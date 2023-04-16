from actors import Marquise, Eyrie, Alliance, Vagabond
from item import Item
from dtos import MoveDTO, CraftDTO, Battle_DTO, OverworkDTO
from map import build_regular_forest
from deck import Deck, QuestDeck
from configs import sympathy_VPs, eyrie_roost_VPs, persistent_effects, Immediate_non_item_effects, eyrie_leader_config
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

    def stand_and_deliver(self, taker, victim):
        victim.deck.shuffle_deck()
        taker.deck.add_card(victim.deck.draw_card())
        taker.victory_points += 1

    def better_burrow_bank(self, actor, other):
        actor.deck.add_card(self.deck.draw_card())
        if len(self.deck.cards) == 0: # DECK ONE LINER
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)
        other.deck.add_card(self.deck.draw_card())

    def codebreakers(self, actor, other):
        actor.known_hands[other.name] = True

    def tax_collection(self, actor, placename):
        self.map.places[placename].soldiers[actor.name] -= 1
        actor.deck.add_card(self.deck.draw_card())
        self.map.places[placename].update_owner()
        if len(self.deck.cards) == 0: # DECK ONE LINER
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
                if building_slot[0] == "sawmill":
                    self.map.places[key].update_pieces(tokens = self.map.places[key].tokens + ["wood"])  

    def add_card_to_decree(self, action, card_ID, card_suit):
        self.eyrie.decree[action].append(card_suit)

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
        if len(self.deck.cards) == 0: # DECK ONE LINER
            self.deck = self.discard_deck
            self.deck.shuffle_deck()
            self.discard_deck = Deck(empty=True)


    # Alliance
    def revolt(self, place, cost, soldiers_to_gain):
        # Clear all buildings
        victory_points = 0
        victory_points += place.clear_buildings()
        victory_points += place.clear_tokens(exception_token="sympathy")
        place.clear_soldiers(exception_faction="alliance")

        # Add a base for the alliance
        place.add_building('base', 'alliance')

        # If the vagabond is present, damage 3 vagabond items
        if place.vagabond_is_here:
            for item in self.vagabond.items_to_damage[:3]:
                self.vagabond.damage_item(item)

        self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(cost[0]))
        self.discard_deck.add_card(self.alliance.supporter_deck.get_the_card(cost[1]))

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

        victory_points = sympathy_VPs[self.map.count_on_self.map(what_to_look_for=('token', 'sympathy'), per_suit = False)]
        self.alliance.victory_points += victory_points

    def slip(self, place, card_to_give_if_sympathy):
        if 'sympathy' in self.map.places[place.name].tokens:
            self.alliance.supporter_deck.add_card(self.vagabond.deck.get_the_card(card_to_give_if_sympathy.ID))
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

        elif attacker == 'vagabond': # Should cover all cases
            if defender != 'alliance':
                dmg_attacker += min(dice_rolls[0], len(list(item for item in self.vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(self.vagabond.allied_soldiers))
                dmg_defender += min(dice_rolls[1], self.map.places[place_name].soldiers[defender])

            elif defender == 'alliance':
                dmg_attacker += min(dice_rolls[1], len(list(item for item in self.vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(self.vagabond.allied_soldiers))
                dmg_defender += min(dice_rolls[0], self.map.places[place_name].soldiers[defender])

        if armorers[0]:
            dmg_defender = 0

        if armorers[1]:
            dmg_attacker = 0        

        # No defender
        if  defender != 'vagabond' and self.map.places[place_name].soldiers[defender] == 0:
            dmg_attacker = min(dmg_attacker, 1)

        if sappers:
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
            extra_dmg_attacker = dmg_attacker - place.soldiers[defender]
            if attacker == "vagabond":
                victory_points_attacker += dmg_attacker-extra_dmg_attacker
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
                    elif piece[1] == "token":
                        place.tokens.remove(piece[0])
                        victory_points_attacker += 1
                        if attacker == "vagabond" and self.vagabond.relations[defender] == "hostile":
                            victory_points_attacker += 1
                        if piece[0] == "sympathy":
                            sympathy_killed = True


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
            extra_dmg_defender = dmg_defender - place.soldiers[attacker]
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
                    elif piece[1] == "token":
                        place.tokens.remove(piece[0])
                        victory_points_defender += 1
                        if piece[0] == "sympathy":
                            sympathy_killed = True

        for actor in [self.eyrie, self.vagabond, self.marquise, self.alliance]:
            if actor.name == attacker:
                actor.victory_points += victory_points_attacker
                if sympathy_killed and card_to_give_if_sympathy:
                    self.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID)) # CORRECT ASSUMING card_to_give_if_no_sympathy is correct


            elif actor.name == defender:
                actor.victory_points += victory_points_defender
                if sympathy_killed and card_to_give_if_sympathy:
                    self.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID))#CORRECT ASSUMING card_to_give_if_no_sympathy is correct
        place.update_owner()

    def move(self, starting_place, destination, quantity, actor, card_to_give_if_sympathy, boot_cost):
        # TODO vagabond moveing with allied soldiers
        if actor.name != 'vagabond':
            starting_place.soldiers[actor.name] -= quantity
            destination.soldiers[actor.name] += quantity

        if actor.name != 'alliance' and destination.tokens.count("sympathy") > 0:
            self.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID))

        if actor.name == 'vagabond':
            self.map.move_vagabond(destination.name)
            for _ in range(boot_cost):
                actor.exhaust_item(Item('boot'))

        if actor.name == 'alliance':
            actor.current_officers -= 1
        self.map.update_owners()

    def craft(self, actor, costs: CraftDTO):

        if costs.card.craft == "ambush":
            raise ValueError("Ambush is not a craftable card")

        if costs.card.craft == "dominance":
            actor.deck.get_the_card(costs.card.ID)
        else:
            self.discard_deck.add_card(actor.deck.get_the_card(costs.card.ID))

        if actor == "vagabond":
            for _ in range(sum(costs.cost.values())):
                actor.exhaust_item("hammer")
        else:
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
            if actor == "bird" and actor.leader!= "Builder":
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


    def ambush(self, place, attacker, counterambush):
        if counterambush or attacker.scouting_party:
            return

        if attacker.name == "vagabond":
            for item in self.vagabond.items_to_damage[:2]:
                self.vagabond.damage_item(item)

        else:
            place.soldiers[attacker.name] -= 2 
            place.soldiers[attacker.name] = max(place.soldiers[attacker.name], 0)


    def build(self, place, actor, building, cost = 0):
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
        for building_slot in place.building_slots:
            if building_slot == ("empty", "No one"):
                building_slot = (building, actor.name)
                break
        place.update_owner()

    def recruit_cat(self):
        for place in self.map.place.values():
            if ("recruiter", "cat") in place.building_slots and sum([place.soldiers["cat"] for place in self.map.places.values()]) < 25:
                place.soldiers["cat"] += 1
        self.map.update_owners()

    def recruit(self, place, actor):
        if actor.name == "bird" and actor.leader == "Charismatic":
            place.soldiers[actor.name] += 2
            place.update_owner()   
        else:
            place.soldiers[actor.name] += 1
            place.update_owner()

    def overwork(self, place, card_id):
        place.tokens.wood += 1
        self.discard_deck.add_card(self.marquise.deck.get_the_card(card_id))

    def eyrie_get_points(self):
        roosts = self.map.count_on_self.map(("building", "roost"))
        self.eyrie.victory_points += eyrie_roost_VPs[roosts]


    def bird_turmoil(self, new_commander):
        
        vp_loss = 0
        for decree_field in self.eyrie.decree.values():
            for value in decree_field:
                value[1] == 'bird'
                vp_loss += 1
        self.eyrie.victory_points -= vp_loss

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


    def mobilize(self, card):
        self.alliance.supporter_deck.add_card(self.alliance.deck.get_the_card(card.ID))

    def train(self, card):
        self.discard_deck.add_card(self.alliance.deck.get_the_card(card.ID))
        self.alliance.total_officers += 1

    def organize(self, place):
        symp_count = self.map.count_on_self.map(("token", "sympathy"), per_suit=False)
        place.solderiers["alliance"] -= 1
        place.tokens += ["sympathy"]
        self.alliance.victory_points += sympathy_VPs[symp_count]

    # Vagabond
    def explore_ruin(self, place):
        for building_slot in place.building_slots:
            if building_slot[0] == "ruin":
                self.vagabond.add_item(building_slot[1])
                building_slot = ("empty", "No one")
                self.vagabond.satchel[self.vagabond.satchel.index(Item('torch'))].exhausted = True
                self.vagabond.victory_points += 1
                return
        raise ValueError("Try to explore but no ruin")

    def aid(self, other_player, choosen_item, choosen_card):
        other_player.deck.add_card(self.vagabond.deck.get_the_card(choosen_card.ID))
        other_player.item.remove(choosen_item)
        self.vagabond.add_item(choosen_item)
        # VPS

    def steal(self, other_player, choosen_card):
        self.vagabond.deck.add_card(other_player.deck.get_the_card(choosen_card.ID))
        self.vagabond.satchel[self.vagabond.satchel.index(Item('torch'))].exhausted = True

    def complete_quest(self, quest_card, items, draw_or_VP):
        self.quest_discard_deck.add_card(self.vagabond.quest_deck.get_the_card(quest_card.ID))
        self.vagabond.quest_deck.add_card(self.quest_deck.draw_card())

        if draw_or_VP == "draw":
            self.vagabond.deck.add_card(self.deck.draw_card())
        if draw_or_VP == "VP":
            self.vagabond.victory_points += sum([card.suit == quest_card.suit  for card in self.quest_discard_deck])

        self.vagabond.exhaust_item(items[0])
        self.vagabond.exhaust_item(items[1])


    def strike(self, place, opponent, target):
        if target == "wood" or target == "keep" or target == "sympathy":
            place.tokens.remove(target)
            if self.vagabond.relationships[opponent.name] == "hostile":
                victory_points += 1
            self.vagabond.victory_points += 1

        elif target == "soldier":
            place.soldiers[opponent.name] -= 1
            if self.vagabond.relationships[opponent.name] == "hostile":
                victory_points += 1
            self.vagabond.relationships[opponent.name] = "hostile"

        else:
            for building_slot in place.building_slots:
                if building_slot[0] == target:
                    building_slot = ("empty", "No one")
                    if self.vagabond.relationships[opponent.name] == "hostile":
                        victory_points += 1
                    victory_points += 1
                    break
        place.update_owner()


def random_choose(options):
    return random.choice(options)