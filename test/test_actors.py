from map import build_regular_forest, Map
from actors import Marquise, Vagabond, Eyrie, Alliance
from deck import Card, Deck
from actions import Battle_DTO, MoveDTO, OverworkDTO
from utils import cat_birdsong_wood
from configs import total_common_card_info

def test_marguise_get_options_craft():
    map = build_regular_forest()
    marguise = Marquise()
    #give marquise a card that can be crafted
    marguise.deck.add_card(Card(*[11, "rabbit", "boot", 1, "rabbit"]))
    #give marquise a card that can be crafted but not enough resources
    marguise.deck.add_card(Card(*[12, "rabbit", "root_tea", 1, "mouse"]))
    marguise.deck.add_card(Card(*[5, "rabbit", "ambush", 0, "ambush"]))
    
    craft_options = marguise.get_options_craft(map)
    assert [craft_option.item for craft_option in craft_options] == ["boot"]
    marguise.get_ambushes()
    assert marguise.ambush == {
            "rabbit": 1,
            "mouse": 0,
            "fox": 0,
            "bird": 0,
        }
    
def test_marquise_battle():
    map = build_regular_forest()
    marguise = Marquise()
    vagabond = Vagabond()
    soldiers = {
			"cat" : 2,
			"bird" : 2,
			"alliance" : 0
		}
    map.places['A'].update_pieces(soldiers = soldiers)
    map.places['A'].update_pieces(tokens = ["sympathy"])
    battle_options = marguise.get_battles(map, vagabond)
    assert battle_options == [Battle_DTO(map.places['A'], "bird"), Battle_DTO(map.places['A'], "alliance")]


def test_marquise_move():
    clearing_num = 4
    suits = ["fox", "rabbit", "mouse", "fox"]
    building_slots = [1, 1, 1, 1]
    vagabond_index = 1
    ruin_indeces = [3]
    paths = ['AB', 'AC', 'BD', 'CD']
    map = Map(4, clearing_num=clearing_num, building_slots=building_slots, suits=suits, vagabond_index=vagabond_index, ruin_indeces=ruin_indeces, paths=paths)
    piece_setup = [('A', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat')], 'tokens' : ['keep']}), # Cats
                       ('B', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat')], 'tokens' : []}), # Cats
                       ('C', {'soldiers' : {'cat': 1, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one')], 'tokens' : []}), # Birds
                       ('D', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one')], 'tokens' : []})] # Birds
    i = 0
    for key in sorted(list(map.places.keys())):
        if map.places[key].name == piece_setup[i][0]:
            map.places[key].update_pieces(**piece_setup[i][1])
            i += 1

    map.update_owners()
    marguise = Marquise()
    move_options = marguise.get_moves(map)
    assert move_options == [MoveDTO(map.places['A'], map.places['B'], 1),
                             MoveDTO(map.places['A'], map.places['C'], 1),
                             MoveDTO(map.places['B'], map.places['A'], 1),  
                              MoveDTO(map.places['B'], map.places['D'], 1),
                                 MoveDTO(map.places['C'], map.places['A'], 1),
                                     MoveDTO(map.places['D'], map.places['B'], 1), 
                                     MoveDTO(map.places['D'], map.places['B'], 2)]
    
def test_marquise_get_connected_wood_tokens():
    map = build_regular_forest()
    cat_birdsong_wood(map)

    marquise = Marquise()
    tokens = marquise.get_wood_tokens_to_build(map, map.places['A'])
    
    assert tokens == 1

    piece_setup =[('B', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat'), ('empty', 'No one')], 'tokens' : []}),# Cats
                    ('C', {'soldiers' : {'cat': 1, 'bird' : 2, 'alliance' : 0}, 'buildings': [('sawmill', 'cat'),('empty', 'No one')], 'tokens' : []}), # Birds
                    ('D', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []}), # Birds
                    ('E', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []}), # Birds
                    ('F', {'soldiers' : {'cat': 2, 'bird' : 0, 'alliance' : 0}, 'buildings': [('empty', 'No one')], 'tokens' : []}), # Cats
                    ('G', {'soldiers' : {'cat': 2, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat'), ('empty', 'No one')], 'tokens' : []})] # Cats
    
    i=0
    for key in sorted(list(map.places.keys())):
        if i >= len(piece_setup):
            break
        if map.places[key].name == piece_setup[i][0]:
            map.places[key].update_pieces(**piece_setup[i][1])
            i += 1

    map.update_owners()
    cat_birdsong_wood(map)
    tokens = marquise.get_wood_tokens_to_build(map, map.places['A'])
    assert tokens == 3

    tokens = marquise.get_wood_tokens_to_build(map, map.places['K'])
    assert tokens == 1

    tokens = marquise.get_wood_tokens_to_build(map, map.places['G'])
    assert tokens == 1


def test_marquise_get_build_options():
    map = build_regular_forest()

    marquise = Marquise()
    build_options = marquise.get_build_options(map)
    assert build_options == {'sawmill': {'where': [], 'cost': 9},
                              'workshop': {'where': [], 'cost': 9},
                                'recruiter': {'where': [], 'cost': 9}}
    
    cat_birdsong_wood(map)
    build_options = marquise.get_build_options(map)
    assert build_options == {'sawmill': {'where': ['B', 'C', 'E', 'G', 'H', 'I', 'J', 'K'], 'cost': 1},
                              'workshop': {'where': ['B', 'C', 'E', 'G', 'H', 'I', 'J', 'K'], 'cost': 1},
                                'recruiter': {'where': ['B', 'C', 'E', 'G', 'H', 'I', 'J', 'K'], 'cost': 1}}
    
    piece_setup =[('B', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat'), ('empty', 'No one')], 'tokens' : []}),# Cats
                ('C', {'soldiers' : {'cat': 1, 'bird' : 3, 'alliance' : 0}, 'buildings': [('sawmill', 'cat'),('recruiter', 'cat')], 'tokens' : []}), # Birds
                ('D', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []}), # Birds
                ('E', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []}), # Birds
                ('F', {'soldiers' : {'cat': 2, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat')], 'tokens' : []}), # Cats
                ('G', {'soldiers' : {'cat': 2, 'bird' : 0, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []})] # Cats

    i=0
    for key in sorted(list(map.places.keys())):
        if i >= len(piece_setup):
            break
        if map.places[key].name == piece_setup[i][0]:
            map.places[key].update_pieces(**piece_setup[i][1])
            i += 1
    map.update_owners()
    cat_birdsong_wood(map)
    build_options = marquise.get_build_options(map)
    assert build_options == {'sawmill': {'where': ['B'], 'cost': 3},
                            'workshop': {'where': ['B', 'G', 'H', 'I', 'J', 'K'], 'cost': 0},
                            'recruiter': {'where': ['B', 'G', 'H', 'I', 'J', 'K'], 'cost': 1}}

def test_marquise_overwork():
    map = build_regular_forest()
    marquise = Marquise()

    common_deck = Deck(empty=True)
    common_deck.add_card(Card(*total_common_card_info[27])) # 2x fox
    common_deck.add_card(Card(*total_common_card_info[28]))
    common_deck.add_card(Card(*total_common_card_info[53])) # 1x bird

    marquise.deck.add_card(common_deck.draw_card())
    marquise.deck.add_card(common_deck.draw_card())
    marquise.deck.add_card(common_deck.draw_card())

    overworks = marquise.get_overwork(map)
    assert overworks == [OverworkDTO('A', 27, 'fox'), OverworkDTO('A', 28, 'fox'), OverworkDTO('A', 53, 'bird'),]

    piece_setup =[('B', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat'), ('empty', 'No one')], 'tokens' : []}),# Cats
            ('C', {'soldiers' : {'cat': 1, 'bird' : 3, 'alliance' : 0}, 'buildings': [('sawmill', 'cat'),('recruiter', 'cat')], 'tokens' : []}), # Birds
            ('D', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []}), # Birds
            ('E', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []}), # Birds
            ('F', {'soldiers' : {'cat': 2, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat')], 'tokens' : []}), # Cats
            ('G', {'soldiers' : {'cat': 2, 'bird' : 0, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []})] # Cats
    
    i=0
    for key in sorted(list(map.places.keys())):
        if i >= len(piece_setup):
            break
        if map.places[key].name == piece_setup[i][0]:
            map.places[key].update_pieces(**piece_setup[i][1])
            i += 1

    map.update_owners()
    overworks = marquise.get_overwork(map)
    assert overworks == [OverworkDTO('A', 27, 'fox'), OverworkDTO('A', 28, 'fox'), OverworkDTO('A', 53, 'bird'), OverworkDTO('B', 53, 'bird'), OverworkDTO('F', 53, 'bird'),]

def test_eyrie_get_decree_options():
    map = build_regular_forest()
    eyrie = Eyrie()

    # Give Eyrie some cards
    common_deck = Deck(empty=True)
    common_deck.add_card(Card(*total_common_card_info[27])) # 2x fox
    common_deck.add_card(Card(*total_common_card_info[28]))
    common_deck.add_card(Card(*total_common_card_info[53])) # 1x bird

    eyrie.deck.add_card(common_deck.draw_card())
    eyrie.deck.add_card(common_deck.draw_card())
    eyrie.deck.add_card(common_deck.draw_card())

    decree_options = eyrie.get_decree_options()

    assert len(decree_options) == 4

    # Check if the decree options include the correct cards with the right suits
    assert decree_options ==  {
            "recruit": [(27, 'fox'), (28, 'fox'), (53, 'bird')],
            "move": [(27, 'fox'), (28, 'fox'), (53, 'bird')],
            "battle": [(27, 'fox'), (28, 'fox'), (53, 'bird')],
            "build": [(27, 'fox'), (28, 'fox'), (53, 'bird')],
        }