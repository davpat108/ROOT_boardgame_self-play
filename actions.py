from actors import Eyrie, Marquise, Vagabond, Alliance, Item
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

def slip(map, where):
    map.move_vagabond(where.end)