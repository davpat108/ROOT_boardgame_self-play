from actors import Eyrie, Marquise, Vagabond, Alliance, Item
from deck import Deck, Card
from configs import total_common_card_info
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
    
