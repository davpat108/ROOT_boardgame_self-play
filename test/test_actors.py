from map import build_regular_forest, Map
from actors import Marquise, Vagabond, Eyrie, Alliance, Item
from deck import Card, Deck, QuestCard, QuestDeck
from dtos import Battle_DTO, MoveDTO, OverworkDTO, Battle_DTO
from actions import cat_birdsong_wood
from configs import total_common_card_info, vagabond_quest_card_info

def test_discard_down_to_five():
    marquise = Marquise()
    common_deck = Deck(empty=True)
    common_deck.add_card(Card(*total_common_card_info[0])) # rabbit
    common_deck.add_card(Card(*total_common_card_info[1]))
    common_deck.add_card(Card(*total_common_card_info[2]))
    common_deck.add_card(Card(*total_common_card_info[27])) # 2x fox
    common_deck.add_card(Card(*total_common_card_info[28]))
    common_deck.add_card(Card(*total_common_card_info[53])) # 1x bird

    marquise.deck.add_card(common_deck.draw_card())
    marquise.deck.add_card(common_deck.draw_card())
    marquise.deck.add_card(common_deck.draw_card())
    marquise.deck.add_card(common_deck.draw_card())
    marquise.deck.add_card(common_deck.draw_card())
    marquise.deck.add_card(common_deck.draw_card())

    options = marquise.discard_down_to_five_options()
    assert options == [[0], [1], [2], [27], [28], [53]]

    common_deck.add_card(Card(*total_common_card_info[52]))
    marquise.deck.add_card(common_deck.draw_card())
    options = marquise.discard_down_to_five_options()
    print(options)
    assert len(options) == 21



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
    assert battle_options == [Battle_DTO('A', "bird"), Battle_DTO('A', "alliance")]


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
    assert move_options == [MoveDTO('A', 'B', 1),
                             MoveDTO('A', 'C', 1),
                             MoveDTO('B', 'A', 1),
                              MoveDTO('B', 'D', 1),
                                 MoveDTO('C', 'A', 1),
                                     MoveDTO('D', 'B', 1),
                                     MoveDTO('D', 'B', 2)]
    
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
    assert build_options == {'sawmill': {'where': ['B', 'C', 'E', 'F', 'G', 'H', 'I', 'J', 'K'], 'cost': 1},
                              'workshop': {'where': ['B', 'C', 'E', 'F', 'G', 'H', 'I', 'J', 'K'], 'cost': 1},
                                'recruiter': {'where': ['B', 'C', 'E', 'F', 'G', 'H', 'I', 'J', 'K'], 'cost': 1}}
    
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
    
    
def test_resolves():
    map = build_regular_forest()
    eyrie = Eyrie()
    vagabond = Vagabond()
    map.places['L'].update_pieces(vagabond_is_here = True) # This creates 2 vagabonds but its ok for now
    
    # Give Eyrie some cards
    common_deck = Deck(empty=True)
    common_deck.add_card(Card(*total_common_card_info[0])) # rabbit
    common_deck.add_card(Card(*total_common_card_info[27])) # 2x fox
    common_deck.add_card(Card(*total_common_card_info[28]))
    common_deck.add_card(Card(*total_common_card_info[53])) # 1x bird

    eyrie.deck.add_card(common_deck.draw_card())
    eyrie.deck.add_card(common_deck.draw_card())
    eyrie.deck.add_card(common_deck.draw_card())
    eyrie.deck.add_card(common_deck.draw_card())

    decree_options = eyrie.get_decree_options()
    eyrie.decree = decree_options # Not how your supposed to do it, but it works for testing
    move_options = eyrie.get_resolve_move(map)
    assert move_options[0] == MoveDTO('L', 'H', 1, 0)
    assert move_options[-1] == MoveDTO('L', 'K', 6, 53)

    recruit_options = eyrie.get_resolve_recruit(map)
    assert recruit_options == [('L', 0), ('L', 53)]

    battle_option = eyrie.get_resolve_battle(map, vagabond)
    assert battle_option == [Battle_DTO('L', 'vagabond', 0), Battle_DTO('L', 'vagabond', 53)]

    map.places['I'].update_pieces(soldiers = {'cat' : 0, 'bird' : 4, 'alliance' : 0})
    map.places['A'].update_pieces(buildings = [('empty', 'No one')], soldiers = {'cat' : 0, 'bird' : 4, 'alliance' : 0})
    map.update_owners()
    build_option = eyrie.get_resolve_building(map)
    assert build_option == [('I', 27),('I', 28),('I', 53)]


def test_eyrie_no_roosts_left():
    map = build_regular_forest()
    eyrie = Eyrie()

    options = eyrie.get_no_roosts_left_options(map)
    assert options == []

    bird_base = {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('empty', 'No one')], 'tokens' : []}
    map.places['L'].update_pieces(**bird_base)
    options = eyrie.get_no_roosts_left_options(map)
    assert sorted(options) == sorted(['B', 'C', 'E','F', 'G', 'H', 'I', 'J', 'K', 'L'])

    empty_clearing = {'soldiers' : {'cat': 0, 'bird' : 0, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []}
    map.places['K'].update_pieces(**empty_clearing)
    options = eyrie.get_no_roosts_left_options(map)
    assert sorted(options) == sorted(['K'])


def test_eyrie_get_options_craft():
    map = build_regular_forest()
    eyrie = Eyrie()
    #give marquise a card that can be crafted
    eyrie.deck.add_card(Card(*[11, "rabbit", "boot", 1, "rabbit"]))
    #give marquise a card that can be crafted but not enough resources
    eyrie.deck.add_card(Card(*[12, "rabbit", "root_tea", 1, "mouse"]))
    eyrie.deck.add_card(Card(*[5, "rabbit", "ambush", 0, "ambush"]))
    
    craft_options = eyrie.get_options_craft(map)
    assert [craft_option.item for craft_option in craft_options] == ["boot"]
    eyrie.get_ambushes()
    assert eyrie.ambush == {
            "rabbit": 1,
            "mouse": 0,
            "fox": 0,
            "bird": 0,
        }
    

def test_alliance_revolt_options():
    map = build_regular_forest()
    alliance = Alliance()

    # Give Alliance some cards
    common_deck = Deck(empty=True)
    common_deck.add_card(Card(*total_common_card_info[0])) # rabbit
    common_deck.add_card(Card(*total_common_card_info[27])) # 2x fox
    common_deck.add_card(Card(*total_common_card_info[28]))
    common_deck.add_card(Card(*total_common_card_info[53])) # 1x bird

    alliance.supporter_deck.add_card(common_deck.draw_card())
    alliance.supporter_deck.add_card(common_deck.draw_card())
    alliance.supporter_deck.add_card(common_deck.draw_card())
    alliance.supporter_deck.add_card(common_deck.draw_card())

    map.places['I'].update_pieces(tokens = ['sympathy'])
    revolt_options = alliance.get_revolt_options(map)

    assert revolt_options == [('I', 27, 28), ('I', 27, 53), ('I', 28, 53)]

    map.places['G'].update_pieces(buildings = [('base', 'alliance'),('ruin', 'No one')], tokens = ['sympathy'])

    revolt_options = alliance.get_revolt_options(map)
    assert revolt_options == []

def test_alliance_spread_options():
    map = build_regular_forest()
    alliance = Alliance()

    # Give Alliance some cards
    common_deck = Deck(empty=True)
    common_deck.add_card(Card(*total_common_card_info[0])) # rabbit
    common_deck.add_card(Card(*total_common_card_info[27])) # 2x fox
    common_deck.add_card(Card(*total_common_card_info[28]))
    common_deck.add_card(Card(*total_common_card_info[53])) # 1x bird

    alliance.supporter_deck.add_card(common_deck.draw_card())
    alliance.supporter_deck.add_card(common_deck.draw_card())
    alliance.supporter_deck.add_card(common_deck.draw_card())
    alliance.supporter_deck.add_card(common_deck.draw_card())

    options = alliance.get_spread_sympathy_options(map)
    assert options == [('B', []), ('C', []), ('D', []), ('E', []), ('F', []), ('G', []), ('H', []), ('I', []), ('J', []), ('K', []), ('L', [0]), ('L', [53])]

    map.places['I'].update_pieces(tokens = ['sympathy'])
    options = alliance.get_spread_sympathy_options(map)
    options.sort(key=lambda x: x[0])
    res = [('C', [53]), ('H', [53]), ('L', [0, 53])]
    res.sort(key=lambda x: x[0])
    assert options == res


    map.places['H'].update_pieces(tokens = ['sympathy'])
    map.places['I'].update_pieces(tokens = ['sympathy'])
    map.places['L'].update_pieces(tokens = ['sympathy'])
    options = alliance.get_spread_sympathy_options(map)
    options.sort(key=lambda x: x[1][0])
    res = [('G', [27,28]), ('G', [27,53]), ('G', [28,53])]
    res.sort(key=lambda x: x[1][0])
    assert options == res

    # Quick check supporter discard
    common_deck.add_card(Card(*total_common_card_info[21]))
    common_deck.add_card(Card(*total_common_card_info[22]))
    alliance.supporter_deck.add_card(common_deck.draw_card())
    alliance.supporter_deck.add_card(common_deck.draw_card())

    options = alliance.discard_down_to_five_supporters_options(map)
    assert sorted(options) == sorted([[0], [21], [22], [27], [28], [53]])

    map.places['B'].update_pieces(buildings = [('base', 'alliance'),('sawmill', 'cat')])
    options = alliance.discard_down_to_five_supporters_options(map)
    assert options == None


def test_alliance_get_options_craft():
    map = build_regular_forest()
    alliance = Alliance()
    #give allaince a card that can be crafted
    alliance.deck.add_card(Card(*[11, "rabbit", "boot", 1, "rabbit"]))
    #give allaince a card that can be crafted but not enough resources
    alliance.deck.add_card(Card(*[12, "rabbit", "root_tea", 1, "mouse"]))
    alliance.deck.add_card(Card(*[5, "rabbit", "ambush", 0, "ambush"]))
    
    map.places['D'].update_pieces(tokens = ['sympathy'])
    craft_options = alliance.get_options_craft(map)
    assert [craft_option.item for craft_option in craft_options] == ["boot"]
    alliance.get_ambushes()
    assert alliance.ambush == {
            "rabbit": 1,
            "mouse": 0,
            "fox": 0,
            "bird": 0,
        }
    
def test_alliance_get_options_train():
    map = build_regular_forest()
    alliance = Alliance()

    common_deck = Deck(empty=True)
    common_deck.add_card(Card(*total_common_card_info[0])) # rabbit
    common_deck.add_card(Card(*total_common_card_info[27])) # 2x fox
    common_deck.add_card(Card(*total_common_card_info[28]))
    common_deck.add_card(Card(*total_common_card_info[53])) # 1x bird

    alliance.deck.add_card(common_deck.draw_card())
    alliance.deck.add_card(common_deck.draw_card())
    alliance.deck.add_card(common_deck.draw_card())
    alliance.deck.add_card(common_deck.draw_card())
    
    map.places['D'].update_pieces(tokens = ['sympathy'], buildings = [('base', 'alliance'), ('ruin', 'No one')])
    train_options = alliance.get_train_options(map)
    assert train_options== [0, 53]

def test_alliance_get_options_battle_recruit_and_organize():
    map = build_regular_forest()
    alliance = Alliance()
    vagabond = Vagabond()
    alliance.total_officers = 1
    alliance.refresh_officers()
    map.places['D'].update_pieces(tokens = ['sympathy'], buildings = [('base', 'alliance'), ('ruin', 'No one')], soldiers = {'cat': 1, 'bird' : 1, 'alliance' : 1})
    map.update_owners()
    battles = alliance.get_battles(map, vagabond)

    assert battles == [Battle_DTO('D', 'cat'), Battle_DTO('D', 'bird')]

    organize = alliance.get_recruits(map)
    assert organize == ['D']

    map.places['K'].update_pieces(soldiers = {'cat': 1, 'bird' : 1, 'alliance' : 1})
    map.update_owners()
    organize = alliance.get_organize_options(map)
    assert organize == ['K']


def test_alliance_move():
    clearing_num = 4
    suits = ["fox", "rabbit", "mouse", "fox"]
    building_slots = [1, 1, 1, 1]
    vagabond_index = 1
    ruin_indeces = [3]
    paths = ['AB', 'AC', 'BD', 'CD']
    map = Map(4, clearing_num=clearing_num, building_slots=building_slots, suits=suits, vagabond_index=vagabond_index, ruin_indeces=ruin_indeces, paths=paths)
    piece_setup = [('A', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 1}, 'buildings': [('base', 'alliance')], 'tokens' : ['keep']}), # Allanace
                       ('B', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 1}, 'buildings': [('base', 'alliance')], 'tokens' : []}), # Allanace
                       ('C', {'soldiers' : {'cat': 0, 'bird' : 2, 'alliance' : 1}, 'buildings': [('empty', 'No one')], 'tokens' : []}), # Birds
                       ('D', {'soldiers' : {'cat': 0, 'bird' : 2, 'alliance' : 2}, 'buildings': [('empty', 'No one')], 'tokens' : []})] # Birds
    i = 0
    for key in sorted(list(map.places.keys())):
        if map.places[key].name == piece_setup[i][0]:
            map.places[key].update_pieces(**piece_setup[i][1])
            i += 1

    map.update_owners()
    alliance = Alliance()
    alliance.total_officers = 1
    alliance.refresh_officers()
    move_options = alliance.get_moves(map)
    assert move_options == [MoveDTO('A', 'B', 1),
                             MoveDTO('A', 'C', 1),
                             MoveDTO('B', 'A', 1),
                              MoveDTO('B', 'D', 1),
                                 MoveDTO('C', 'A', 1),
                                     MoveDTO('D', 'B', 1),
                                     MoveDTO('D', 'B', 2)]
    

def test_vagabond():
    map = build_regular_forest()
    alliance = Alliance()
    eyrie = Eyrie()
    marquise = Marquise()
    vagabond = Vagabond()
    # SLIP and MOVE
    slip_options = vagabond.get_slip_options(map)
    slip_options = sorted(slip_options, key= lambda x: (x.start, x.end))
    assert slip_options == sorted([MoveDTO('O', 'C', 0), MoveDTO('O', 'D', 0), MoveDTO('O', 'G', 0), MoveDTO('O', 'H', 0), MoveDTO('O', 'I', 0)], key= lambda x: (x.start, x.end))

    move_options = vagabond.get_moves(map)
    assert move_options == sorted([MoveDTO('O', 'C', 0), MoveDTO('O', 'D', 0), MoveDTO('O', 'G', 0), MoveDTO('O', 'H', 0), MoveDTO('O', 'I', 0)], key= lambda x: (x.start, x.end))

    vagabond.damage_item(Item('boot'))
    move_options = vagabond.get_moves(map)
    move_options = sorted(move_options, key= lambda x: (x.start, x.end))
    assert move_options == []


    map.move_vagabond('C')
    slip_options = vagabond.get_slip_options(map)
    slip_options =sorted(slip_options, key= lambda x: (x.start, x.end))
    assert slip_options == sorted([MoveDTO('C', 'B', 0), MoveDTO('C', 'D', 0), MoveDTO('C', 'I', 0), MoveDTO('C', 'M', 0), MoveDTO('C', 'O', 0)], key= lambda x: (x.start, x.end))

    # REPAIR
    vagabond.repair_item(Item('boot'))
    move_options = vagabond.get_moves(map)
    move_options = sorted(move_options, key= lambda x: (x.start, x.end))
    assert move_options == sorted([MoveDTO('C', 'B', 0), MoveDTO('C', 'D', 0), MoveDTO('C', 'I', 0)], key= lambda x: (x.start, x.end))

    # REFRESH
    vagabond.exhaust_item(Item('boot'))
    vagabond.exhaust_item(Item('sword'))
    refresh_options = vagabond.get_refresh_options()
    assert refresh_options == [(Item('sword'), Item('boot'))]

    # BATTLE
    vagabond.refresh_item(refresh_options[0][0])
    vagabond.refresh_item(refresh_options[0][1])

    map.places['C'].update_pieces(soldiers = {'cat': 1, 'bird' : 1, 'alliance' : 1})
    battle_options = vagabond.get_battle_options(map)
    assert battle_options == [Battle_DTO('C', 'cat'), Battle_DTO('C', 'bird'), Battle_DTO('C', 'alliance')]

    vagabond.exhaust_item(Item('sword'))
    battle_options = vagabond.get_battle_options(map)
    assert battle_options == []
    # REPAIR
    vagabond.damage_item(Item('boot'))
    vagabond.damage_item(Item('sword'))

    repair_options = vagabond.get_repair_options()
    assert repair_options == []

    vagabond.add_item(Item('hammer'))
    repair_options = sorted(vagabond.get_repair_options(), key= lambda x: x.name)
    assert repair_options == sorted([Item('boot'), Item('sword')], key= lambda x: x.name)
    
    # QUEST
    vagabond.add_item(Item('crossbow'))
    vagabond.quest_deck.add_card(QuestCard(*vagabond_quest_card_info[10])) # 2 mouse 1 fox
    vagabond.quest_deck.add_card(QuestCard(*vagabond_quest_card_info[11]))
    vagabond.quest_deck.add_card(QuestCard(*vagabond_quest_card_info[0]))

    quest_options = vagabond.get_quest_options(map)
    assert quest_options == [10]
    vagabond.repair_item(Item('sword'))
    vagabond.refresh_item(Item('sword'))
    quest_options = vagabond.get_quest_options(map)
    assert quest_options == [10, 11]

    vagabond.exhaust_item(Item('torch'))
    vagabond.exhaust_item(Item('sword'))
    quest_options = vagabond.get_quest_options(map)
    assert quest_options == []

    #THIEVING
    vagabond.repair_and_refresh_all()
    thief_options = vagabond.get_thief_ability(map)
    assert thief_options == ['cat', 'bird', 'alliance']

    vagabond.exhaust_item(Item('torch'))
    thief_options = vagabond.get_thief_ability(map)
    assert thief_options == []

    # RUIN
    vagabond.repair_and_refresh_all()
    ruin_option = vagabond.get_ruin_explore_options(map)
    assert ruin_option == False

    map.move_vagabond('D')
    ruin_option = vagabond.get_ruin_explore_options(map)
    assert ruin_option == True

    map.places['D'].building_slots[0] = ('empty', 'No one')
    map.places['D'].building_slots[1] = ('empty', 'No one') # RUIN cleared
    ruin_option = vagabond.get_ruin_explore_options(map)
    assert ruin_option == False

    # STRIKE
    vagabond.repair_and_refresh_all()
    strike_options = vagabond.get_strike_options(map)
    assert strike_options == [('D', 'cat', 'soldier')]

    map.move_vagabond('A')
    strike_options = vagabond.get_strike_options(map)
    assert strike_options == [('A', 'cat', 'soldier')]

    map.places['A'].update_pieces(soldiers = {'cat': 0, 'bird' : 0, 'alliance' : 0})
    strike_options = vagabond.get_strike_options(map)
    strike_options = sorted(strike_options, key= lambda x: (x[0], x[1], x[2]))
    assert strike_options == sorted([('A', 'cat', 'keep'), ('A', 'cat', 'sawmill')], key= lambda x: (x[0], x[1], x[2]))

    map.places['A'].update_pieces(tokens = ['sympathy', 'keep'])
    strike_options = vagabond.get_strike_options(map)
    strike_options = sorted(strike_options, key= lambda x: (x[0], x[1], x[2]))
    assert strike_options == sorted([('A', 'cat', 'keep'), ('A', 'cat', 'sawmill'), ('A', 'alliance', 'sympathy')], key= lambda x: (x[0], x[1], x[2]))

    vagabond.exhaust_item(Item('crossbow'))
    strike_options = vagabond.get_strike_options(map)
    assert strike_options == []

    # AID

    common_deck = Deck(empty=True)
    common_deck.add_card(Card(*total_common_card_info[0])) # rabbit
    common_deck.add_card(Card(*total_common_card_info[27])) # 2x fox
    common_deck.add_card(Card(*total_common_card_info[28]))
    common_deck.add_card(Card(*total_common_card_info[53])) # 1x bird

    vagabond.deck.add_card(common_deck.draw_card())
    vagabond.deck.add_card(common_deck.draw_card())
    vagabond.deck.add_card(common_deck.draw_card())
    vagabond.deck.add_card(common_deck.draw_card())

    vagabond.repair_and_refresh_all()
    vagabond.relations['cat'] = 'very good'
    aid_options = vagabond.get_aid_options(map, [marquise, eyrie, alliance]) # alliance, cat
    aid_options = sorted(aid_options, key= lambda x: (x[0], x[1]))
    assert aid_options == sorted([('alliance', [27], None), ('alliance', [28], None), ('alliance', [53], None), ('cat', [27, 28, 53],  None)], key= lambda x: (x[0], x[1]))

    marquise.items = [Item('sword'), Item('sword'), Item('sword')]
    aid_options = vagabond.get_aid_options(map, [marquise, eyrie, alliance]) # alliance, cat
    aid_options = sorted(aid_options, key= lambda x: (x[0], x[1]))
    assert aid_options == sorted([('alliance', [27], None), ('alliance', [28], None), ('alliance', [53], None), ( 'cat', [27, 28, 53],  'sword')], key= lambda x: (x[0], x[1]))

    alliance.items = [Item('sword'), Item('crossbow')]
    aid_options = vagabond.get_aid_options(map, [marquise, eyrie, alliance]) # alliance, cat
    aid_options = sorted(aid_options, key= lambda x: (x[0], x[1], x[2]))
    assert aid_options == sorted([('alliance', [27], 'sword'), ('alliance', [28], 'sword'), ('alliance', [53], 'sword'), ('alliance', [27], 'crossbow'), ('alliance', [28], 'crossbow'), ('alliance', [53], 'crossbow'), ('cat', [27, 28, 53],  'sword')], key= lambda x: (x[0], x[1], x[2]))

    vagabond.deck.draw_card()
    vagabond.deck.draw_card()
    vagabond.deck.draw_card()
    vagabond.deck.draw_card()

    aid_options = vagabond.get_aid_options(map, [marquise, eyrie, alliance]) # alliance, cat
    aid_options = sorted(aid_options, key= lambda x: (x[0], x[1], x[2]))
    assert aid_options == []

    # DMG otpions