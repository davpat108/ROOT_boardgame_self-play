from item import Item
from deck import Deck, Card
from configs import sympathy_VPs
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
    
def revolt(map, alliance, discard_deck, place_name, cardID1, cardID2, vagabond, vagabond_item_breaks):
    victory_points = 0
    if cardID1 == cardID2:
        raise ValueError("Error in revolt: cardID1 == cardID2")
    #Get soldiers
    sympathies = map.count_on_map(what_to_look_for=('token', 'sympathy'), per_suit = True)
    soldiers = sympathies[map.places[place_name].suit] + 1

    # VPs
    for slot in map.places[place_name].building_slots:
        if slot[1] != 'No one':
            victory_points += 1
    
    for token in map.places[place_name].tokens:
        if token != 'sympathy':
            victory_points += 1

    # place base and remove everything else
    map.places[place_name].building_slots[0] = ('base', 'alliance')
    for i in range(len(map.places[place_name].building_slots)-1):
        map.places[place_name].building_slots[i+1] = ('empty', 'No one')

    
    map.places[place_name].update_pieces(soldiers = {'cat': soldiers, 'bird': 0, 'alliance': soldiers}, tokens=['sympathy'])

    if discard_deck.add_card(alliance.supporter_deck.get_the_card(cardID1)) is not None \
          or discard_deck.add_card(alliance.supporter_deck.get_the_card(cardID2)) is not None:
        raise ValueError("Error in revolt: card not in supporter deck")
    

    if map.places[place_name].vagabond_is_here:
        for item in vagabond_item_breaks:
            vagabond.damage(item)
    
    alliance.victory_points += victory_points

def spread_sympathy(map, alliance, discard_deck, place_name, card_ids):
    map.places[place_name].update_pieces(tokens = map.places[place_name].tokens + ['sympathy'])

    for cardID in card_ids:
        if discard_deck.add_card(alliance.supporter_deck.get_the_card(cardID)) is not None:
            raise ValueError("Error in spread_sympathy: card not in supporter deck")
    
    victory_points = sympathy_VPs[map.count_on_map(what_to_look_for=('token', 'sympathy'), per_suit = False)]
    alliance.victory_points += victory_points

# Refresh items for vagabond already implemented in Vagabond class

def slip(map, where, vagabond, alliance, card_to_give_if_sympathy):
    if 'sympathy' in map.places[where.end].tokens:
        vagabond.deck.add_card(alliance.deck.get_the_card(card_to_give_if_sympathy.ID))
    map.move_vagabond(where.end)

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

def ambush():
    pass

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
                alliance.deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID)) # CORRECT ASSUMING card_to_give_if_no_sympathy is correct

                
        elif actor.name == defender:
            actor.victory_points += victory_points_defender
            if sympathy_killed and card_to_give_if_sympathy:
                alliance.deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy.ID))#CORRECT ASSUMING card_to_give_if_no_sympathy is correct

def move(map, starting_place, destination, quantity, actor, alliance, card_to_give_if_sympathy, boot_cost = None):
    if actor.name != 'vagabond':
        starting_place.soldiers[actor.name] -= quantity
        destination.soldiers[actor.name] += quantity

    if actor.name != 'alliance' and destination.tokens.count("sympathy") > 0:
        actor.deck.add_card(alliance.deck.get_the_card(card_to_give_if_sympathy.ID))
    
    if actor.name == 'vagabond':
        map.move_vagabond(destination.name)
        for _ in range(boot_cost):
            actor.exhaust_item(Item('boot'))

def craft(actor, card, discard_deck, costs = []):

    actor.add_item(card.craft)
    discard_deck.add_card(actor.deck.get_the_card(card.ID))

    if actor == "vagabond":
        for cost in costs:
            actor.exhaust_item("hammer")
    else:
        for cost in costs:
            actor.deactivate(card.craft_suit)