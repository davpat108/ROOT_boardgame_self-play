from item import Item
from deck import Deck, Card
from dtos import CraftDTO, MoveDTO, Battle_DTO, ActionDTO
from configs import sympathy_VPs, eyrie_roost_VPs, persistent_effects, Immediate_non_item_effects
# BIRDSONG
def cat_birdsong_wood(map):
    for key in list(map.places.keys()):
        for building_slot in map.places[key].building_slots:
            if building_slot[0] == "sawmill":
                map.places[key].update_pieces(tokens = map.places[key].tokens + ["wood"])  

def add_card_to_decree(eyrie, action, card_ID, card_suit):
    eyrie.decree[action].append(card_suit)
    
    if eyrie.decree_deck.add_card(eyrie.deck.get_the_card(card_ID)) is not None:
        raise ValueError("Eyrie tried to add wrong card to decree deck")
    
def place_roost_if_zero_roost(map, place_name):
    try:
        map.places[place_name].building_slots[map.places[place_name].building_slots.index(('empty', 'No one'))] = ('roost', 'bird')
        map.places[place_name].soldiers['bird'] += 3
    except ValueError:
        raise ValueError("Error in get_no_roosts_left_options")

# Alliance
def revolt(map, place, vagabond_items, vagabond, alliance, cost, soldiers_to_gain, discard_deck):
    # Clear all buildings
    victory_points = 0
    victory_points += place.clear_buildings()
    victory_points += place.clear_tokens(exception_token="sympathy")
    place.clear_soldiers(exception_faction="alliance")

    # Add a base for the alliance
    place.add_building('base', 'alliance')

    # If the vagabond is present, damage 3 vagabond items
    if place.vagabond_is_here:
        for item in vagabond_items[:3]:
            vagabond.damage_item(item)

    discard_deck.add_card(alliance.supporter_deck.get_the_card(cost[0]))
    discard_deck.add_card(alliance.supporter_deck.get_the_card(cost[1]))

    for _ in range(soldiers_to_gain):
        if sum([place.soldiers["alliance"] for place in map.places.values()]) + alliance.total_officers >= 10:
            break
        place.soldiers["alliance"] += 1

    if sum([place.soldiers["alliance"] for place in map.places.values()]) + alliance.total_officers <= 10:
        alliance.total_officers += 1

    place.update_owner()
    alliance.victory_points += victory_points


def spread_sympathy(map, alliance, discard_deck, place_name, card_ids):
    map.places[place_name].update_pieces(tokens = map.places[place_name].tokens + ['sympathy'])

    for cardID in card_ids:
        if discard_deck.add_card(alliance.supporter_deck.get_the_card(cardID)) is not None:
            raise ValueError("Error in spread_sympathy: card not in supporter deck")
    
    victory_points = sympathy_VPs[map.count_on_map(what_to_look_for=('token', 'sympathy'), per_suit = False)]
    alliance.victory_points += victory_points

# Refresh items for vagabond already implemented in Vagabond class

def slip(map, place, vagabond, alliance, card_to_give_if_sympathy):
    if 'sympathy' in map.places[place.name].tokens:
        alliance.supporter_deck.add_card(vagabond.deck.get_the_card(card_to_give_if_sympathy.ID))
    map.move_vagabond(place.name)

# DAYLIGHT


def get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False, vagabond_items= None):
    """
    :param attacker: str
    :param defender: str
    :param dice_rolls: list, 2 0-3 nums descending order
    """
    # So vagabond cant attack its allies with its allies
    if attacker == "vagabond":
        if vagabond.relations[defender] == "friendly":
            vagabond.allied_soldiers = remove_soldiers_from_vagabond_items(vagabond.allied_soldiers, defender)
            vagabond_items = remove_soldiers_from_vagabond_items(vagabond_items, defender)

    
    dmg_attacker = 0
    dmg_defender = 0

    # Regular battle
    if attacker != 'vagabond' and defender != 'vagabond':
        if defender != 'alliance':
            dmg_attacker += min(dice_rolls[0], map.places[place_name].soldiers[attacker])
            dmg_defender += min(dice_rolls[1], map.places[place_name].soldiers[defender])

        elif defender == 'alliance':
            dmg_attacker += min(dice_rolls[1], map.places[place_name].soldiers[attacker])
            dmg_defender += min(dice_rolls[0], map.places[place_name].soldiers[defender])
    
    elif defender == 'vagabond':
            dmg_attacker += min(dice_rolls[0], map.places[place_name].soldiers[attacker])
            dmg_defender += min(dice_rolls[1], len(list(item for item in vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(vagabond.allied_soldiers))

    elif attacker == 'vagabond': # Should cover all cases
        if defender != 'alliance':
            dmg_attacker += min(dice_rolls[0], len(list(item for item in vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(vagabond.allied_soldiers))
            dmg_defender += min(dice_rolls[1], map.places[place_name].soldiers[defender])

        elif defender == 'alliance':
            dmg_attacker += min(dice_rolls[1], len(list(item for item in vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(vagabond.allied_soldiers))
            dmg_defender += min(dice_rolls[0], map.places[place_name].soldiers[defender])

    # No defender
    if  defender != 'vagabond' and map.places[place_name].soldiers[defender] == 0:
        dmg_attacker = min(dmg_attacker, 1)

    # Sapper
    for actor in [eyrie, vagabond, marquise, alliance]:
        if actor.sappers != 0 and attacker == actor.name:
            dmg_attacker += actor.sappers
        if actor.sappers != 0 and defender == actor.name:
            dmg_defender += actor.sappers
        # OWL
        if actor.name == 'bird' and actor.leader == 'Commander' and attacker == 'bird':
            dmg_attacker += 1

    for actor in [eyrie, vagabond, marquise, alliance]:
        if actor.armorers != 0 and defender == actor.name:
            dmg_attacker = 0

    if armorers:
        dmg_attacker = 0

    return dmg_attacker, dmg_defender
    

def priority_to_list(priorities, place, owner):
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

def remove_soldiers_from_vagabond_items(items, defender):
    new_items = []
    for item in items:
        if not item == defender:
            new_items.append(item)
    return new_items

def resolve_battle(place, attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces=None, defender_chosen_pieces=None, vagabond_items=None, card_to_give_if_sympathy=None):
    """
    :param map: Map
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
        if vagabond.relations[defender] == "friendly":
            vagabond.allied_soldiers = remove_soldiers_from_vagabond_items(vagabond.allied_soldiers, defender)
            vagabond_items = remove_soldiers_from_vagabond_items(vagabond_items, defender)
    victory_points_attacker = 0
    victory_points_defender = 0
    sympathy_killed = False
    # Process attacker's damage
    if defender == "vagabond":
        for item in vagabond_items[:dmg_attacker]:
            vagabond.damage_item(item)
    else:
        # If attacker dealt more damage than defender's soldiers, remove additional pieces
        extra_dmg_attacker = dmg_attacker - place.soldiers[defender]
        if attacker == "vagabond":
            victory_points_attacker += dmg_attacker-extra_dmg_attacker
        if attacker == "vagabond" and dmg_attacker-extra_dmg_attacker > 0 and vagabond.relations[defender] != "hostile":
            vagabond.relations[defender] = "hostile"
            victory_points_attacker-=1 # THAT one soldier doesn't count as VP
        if extra_dmg_attacker <=0:
            place.soldiers[defender] -= dmg_attacker
        else:
            place.soldiers[defender] = 0
            for piece in defender_chosen_pieces[:extra_dmg_attacker]:
                if piece[1] == "building":
                    place.remove_building(piece[0])
                    victory_points_attacker += 1
                    if attacker == "vagabond" and vagabond.relations[defender] == "hostile":
                        victory_points_attacker += 1
                elif piece[1] == "token":
                    place.tokens.remove(piece[0])
                    victory_points_attacker += 1
                    if attacker == "vagabond" and vagabond.relations[defender] == "hostile":
                        victory_points_attacker += 1
                    if piece[0] == "sympathy":
                        sympathy_killed = True


    # Process defender's damage
    if attacker == "vagabond":
        items = 0
        soldiers = 0
        for item in vagabond_items[:dmg_defender]:
            vagabond.damage_item(item, place)
            if isinstance(item, Item):
                items += 1
            else:
                soldiers += 1
        if soldiers > items:
            vagabond.relations[item] = "hostile"

    else:
        # If defender dealt more damage than attacker's soldiers, remove additional pieces
        extra_dmg_defender = dmg_defender - place.soldiers[attacker]
        if defender == "vagabond" and dmg_defender-extra_dmg_defender > 0:
            vagabond.relations[attacker] = "hostile"
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
    
    for actor in [eyrie, vagabond, marquise, alliance]:
        if actor.name == attacker:
            actor.victory_points += victory_points_attacker
            if sympathy_killed and card_to_give_if_sympathy:
                alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID)) # CORRECT ASSUMING card_to_give_if_no_sympathy is correct

                
        elif actor.name == defender:
            actor.victory_points += victory_points_defender
            if sympathy_killed and card_to_give_if_sympathy:
                alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID))#CORRECT ASSUMING card_to_give_if_no_sympathy is correct
    place.update_owner()

def move(map, starting_place, destination, quantity, actor, alliance, card_to_give_if_sympathy, boot_cost):
    # TODO vagabond moveing with allied soldiers
    if actor.name != 'vagabond':
        starting_place.soldiers[actor.name] -= quantity
        destination.soldiers[actor.name] += quantity

    if actor.name != 'alliance' and destination.tokens.count("sympathy") > 0:
        alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID))
    
    if actor.name == 'vagabond':
        map.move_vagabond(destination.name)
        for _ in range(boot_cost):
            actor.exhaust_item(Item('boot'))
    
    if actor.name == 'alliance':
        actor.current_officers -= 1
    map.update_owners()

def craft(map, actor, discard_deck, vagabond, vagabond_items, costs: CraftDTO):

    if costs.card.craft == "ambush":
        raise ValueError("Ambush is not a craftable card")
    
    if costs.card.craft == "dominance":
        actor.deck.get_the_card(costs.card.ID)
    else:
        discard_deck.add_card(actor.deck.get_the_card(costs.card.ID))

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
        map.craftables.remove(costs.card.craft)
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
            favor(map, actor, costs.card.craft_suit, vagabond, vagabond_items)
        if costs.card.craft == "dominance":
            dominance(actor, costs.card.building, costs.card.cost)
        
        
def favor(map, actor, suit, vagabond, vagabond_items):
    victory_points = 0
    for place in map.places.values():
        if place.suit == suit:
            for key in place.soldiers.keys():
                if key != actor.name and key != "vagabond":
                    place.soldiers[key] = 0
            if actor.name != "vagabond" and place.vagabond_is_here:
                for item in vagabond_items[:3]:
                    vagabond.damage_item(item)
            victory_points += place.clear_buildings(exception_faction=actor.name)
            victory_points += place.clear_tokens(exception_faction=actor.name)
    actor.victory_points += victory_points
    map.update_owners()

            

def dominance(user, actors, suit):
    if user == "vagabond":
        min_points = 100
        min_point_actorname = None
        for actor in actors:
            if actor != "vagabond":
                if actor.victory_points < min_points:
                    min_points = actor.victory_points
                    min_point_actorname = actor.name

        for actor in actors:
            if actor.name == min_point_actorname:
                actor.win_condition = "coalition"
        user.win_condition = "coalition"
    else:
        user.win_condition = suit
        

def ambush(place, attacker, counterambush, vagabond, vagabond_items):
    if counterambush:
        return
    
    if attacker.name == "vagabond":
        for item in vagabond_items[:2]:
            vagabond.damage_item(item)
    
    else:
        place.soldiers[attacker.name] -= 2 
        place.soldiers[attacker.name] = max(place.soldiers[attacker.name], 0)


def build(map, place, actor, building, cost = 0):
    if actor.name == "cat": #Choosing which woods to remove is too much work for now
        i = cost
        for _ in range(i):
            for place in map.places.values():
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

def recruit_cat(map):
    for place in map.place.values():
        if ("recruiter", "cat") in place.building_slots and sum([place.soldiers["cat"] for place in map.places.values()]) < 25:
            place.soldiers["cat"] += 1
    map.update_owners()

def recruit(place, actor):
    place.soldiers[actor.name] += 1
    place.update_owner()

def overwork(place):
    place.tokens.wood += 1

def eyrie_get_points(map, eyrie):
    roosts = map.count_on_map(("building", "roost"))
    eyrie.victory_points += eyrie_roost_VPs[roosts]


def spread_symp(map, place, cost, discard_deck, alliance):
    symp_count = map.count_on_map(("token", "sympathy"), per_suit=False)
    place.tokens.append("sympathy")
    for i in range(len(cost)):
        discard_deck.add_card(alliance.supporter_deck.get_the_card(cost[i]))
    
    alliance.victory_points += sympathy_VPs[symp_count]
    place.update_owner()
    

def mobilize(card, alliance):
    alliance.supporter_deck.add_card(alliance.deck.get_the_card(card.ID))

def train(card, alliance, discard_deck):
    discard_deck.add_card(alliance.deck.get_the_card(card.ID))
    alliance.total_officers += 1
    
def organize(map, place, alliance):
    symp_count = map.count_on_map(("token", "sympathy"), per_suit=False)
    place.solderiers["alliance"] -= 1
    place.tokens += ["sympathy"]
    alliance.victory_points += sympathy_VPs[symp_count]

# Vagabond
def explore_ruin(vagabond, place):
    for building_slot in place.building_slots:
        if building_slot[0] == "ruin":
            vagabond.add_item(building_slot[1])
            building_slot = ("empty", "No one")
            vagabond.satchel[vagabond.satchel.index(Item('torch'))].exhausted = True
            vagabond.victory_points += 1
            return
    raise ValueError("Try to explore but no ruin")

def aid(other_player, vagabond, choosen_item, choosen_card):
    other_player.deck.add_card(vagabond.deck.get_the_card(choosen_card.ID))
    other_player.item.remove(choosen_item)
    vagabond.add_item(choosen_item)
    # VPS

def steal(vagabond, other_player, choosen_card):
    vagabond.deck.add_card(other_player.deck.get_the_card(choosen_card.ID))
    vagabond.satchel[vagabond.satchel.index(Item('torch'))].exhausted = True

def complete_quest(quest_discard_deck, quest_card, quest_deck, common_deck, vagabond, items, draw_or_VP):
    quest_discard_deck.add_card(vagabond.quest_deck.get_the_card(quest_card.ID))
    vagabond.quest_deck.add_card(quest_deck.draw_card())

    if draw_or_VP == "draw":
        vagabond.deck.add_card(common_deck.draw_card())
    if draw_or_VP == "VP":
        vagabond.victory_points += sum([card.suit == quest_card.suit  for card in quest_discard_deck])

    vagabond.exhaust_item(items[0])
    vagabond.exhaust_item(items[1])


def strike(place, opponent, target, vagabond):
    if target == "wood" or target == "keep" or target == "sympathy":
        place.tokens.remove(target)
        if vagabond.relationships[opponent.name] == "hostile":
            victory_points += 1
        vagabond.victory_points += 1

    elif target == "soldier":
        place.soldiers[opponent.name] -= 1
        if vagabond.relationships[opponent.name] == "hostile":
            victory_points += 1
        vagabond.relationships[opponent.name] = "hostile"

    else:
        for building_slot in place.building_slots:
            if building_slot[0] == target:
                building_slot = ("empty", "No one")
                if vagabond.relationships[opponent.name] == "hostile":
                    victory_points += 1
                victory_points += 1
                break
    place.update_owner()