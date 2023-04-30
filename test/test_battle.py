import sys
sys.path.append('.')
from item import Item
from configs import total_common_card_info
from deck import Deck, Card
from dtos import MoveDTO, CraftDTO, OverworkDTO
from game import Game
from actors import Vagabond, Alliance, Marquise, Eyrie

def test_resolve_battle():
    # Setup
    game = Game(debug=True)

    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    # CAT VS BIRD more bird, roost dead
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]


    # CAT VS BIRD BIRD AMBUSH
    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']
    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    game.eyrie.deck.add_card(game.deck.get_the_card(48))
    options_defender = game.eyrie.get_ambush_options(game.map.places['H'])
    if options_defender[1]:
        options_attacker = game.marquise.get_ambush_options(game.map.places['H'])
        game.ambush(placename = 'H', attacker=game.marquise, defender=game.eyrie, bird_or_suit_defender=options_defender[1], bird_or_suit_attacker=options_attacker[0])
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert game.eyrie.deck.get_the_card(48) == "Card not in the deck"

    # CAT VS BIRD BIRD AMBUSH, CAT SCOUTING PARTY
    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.marquise.scouting_party = True
    
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']
    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    game.eyrie.deck.add_card(game.deck.get_the_card(25))
    options_defender = game.eyrie.get_ambush_options(game.map.places['H'])
    if options_defender[1]:
        options_attacker = game.marquise.get_ambush_options(game.map.places['H'])
        game.ambush(placename = 'H', attacker=game.marquise, defender=game.eyrie, bird_or_suit_defender=options_defender[1], bird_or_suit_attacker=options_attacker[0])
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]
    assert game.eyrie.deck.get_the_card(25) == "Card not in the deck"

    # CAT VS BIRD BIRD AMBUSH, CAT COUNTER AMBUSH
    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.marquise.scouting_party = False
    
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']
    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    game.eyrie.deck.add_card(game.discard_deck.get_the_card(25))
    game.marquise.deck.add_card(game.deck.get_the_card(49))
    options_defender = game.eyrie.get_ambush_options(game.map.places['H'])
    if options_defender[1]:
        options_attacker = game.marquise.get_ambush_options(game.map.places['H'])
        game.ambush(placename = 'H', attacker=game.marquise, defender=game.eyrie, bird_or_suit_defender=options_defender[1], bird_or_suit_attacker=options_attacker[1])
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]
    assert game.eyrie.deck.get_the_card(25) == "Card not in the deck"
    assert game.marquise.deck.get_the_card(49) == "Card not in the deck"

    # BIRDS VS CAT more cat
    defender_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker_piece_lose_priorities = ['roost']
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    attacker = 'bird'
    defender = 'cat'

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]

    # LOTS OF BIRDS + OWL BONUS VS 2 CATS
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    defender_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker_piece_lose_priorities = ['roost']
    attacker = 'bird'
    defender = 'cat'
    game.eyrie.change_role('Commander')
    dice_rolls = [3, 3]
    
    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 1
    assert game.map.places['H'].building_slots == [('empty', 'No one'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in game.map.places['H'].tokens

    # CATS VS BIRDS + OWL BONUS (shouldn't apply)
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']
    attacker = 'cat'
    defender = 'bird'
    dice_rolls = [3, 3]

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)    
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 1
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in game.map.places['H'].tokens
    assert dmg_defender == 3

    # VAGABOND attacker VS CATS
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.map.move_vagabond('H')
    attacker_piece_lose_priorities = []
    defender_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker = 'vagabond'
    defender = 'cat'
    dice_rolls = [3, 3]
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('money'))
    game.vagabond.items_to_damage = [Item('money'), Item('sack'), Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('sword')]

    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in game.map.places['H'].tokens
    assert sorted(game.vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == True


    # VAGABOND defender VS CATS
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    defender_piece_lose_priorities = []
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker = 'cat'
    defender = 'vagabond'
    dice_rolls = [3, 3]
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('money'))
    game.vagabond.items_to_damage = [Item('money'), Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('sword')]

    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in game.map.places['H'].tokens
    assert sorted(game.vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == True
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].damaged == True


    # VAGABOND attacker VS alliance
    game.map.places['H'].update_pieces(soldiers ={'cat': 0, 'bird': 0, 'alliance': 1}, buildings = [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')], tokens = ['sympathy'])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    attacker_piece_lose_priorities = []
    defender_piece_lose_priorities = ['sympathy','base']
    attacker = 'vagabond'
    defender = 'alliance'
    dice_rolls = [3, 0]
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('money'))
    game.vagabond.items_to_damage = [Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('money'), Item('sword'), Item('sword'), Item('sword')]
    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = 17

    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['alliance'] == 1
    assert game.map.places['H'].building_slots == [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')]
    assert 'sympathy' in game.map.places['H'].tokens
    assert sorted(game.vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].damaged == True

    # GET SYMPATHY penalty
    game.map.places['H'].update_pieces(soldiers ={'cat': 0, 'bird': 0, 'alliance': 1}, buildings = [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')], tokens = ['sympathy'])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.alliance.supporter_deck = Deck(empty=True)
    game.map.move_vagabond('H')
    defender_piece_lose_priorities = []
    attacker_piece_lose_priorities = ['sympathy','base']
    attacker = 'alliance'
    defender = 'vagabond'
    dice_rolls = [3, 3]
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('money'))
    game.vagabond.items_to_damage = [Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('money'), Item('sword'), Item('sword'), Item('sword')]
    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = 17

    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['alliance'] == 0
    assert game.map.places['H'].building_slots == [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')]
    assert 'sympathy' not in game.map.places['H'].tokens
    assert sorted(game.vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].damaged == True
    assert len(game.vagabond.deck.cards) == 0
    assert game.alliance.supporter_deck.cards[0] == Card(*total_common_card_info[17])

    # VAGABOND attacker vs cat with bird allies turns hostile
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')], tokens = [])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    defender_piece_lose_priorities = []
    attacker_piece_lose_priorities = []
    attacker = 'vagabond'
    defender = 'cat'
    dice_rolls = [3, 3]
    game.vagabond.relations['bird'] = "friendly"
    game.vagabond.allied_soldiers = ['bird', 'bird', 'bird']
    game.vagabond.items_to_damage = ['bird', 'bird',  Item('torch'), Item('sword')]

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 1
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].damaged == False
    assert game.vagabond.relations['bird'] == "hostile"

    # VAGABOND attacker vs cat with bird allies doesn't turn hostile
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')], tokens = [])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    defender_piece_lose_priorities = []
    attacker_piece_lose_priorities = []
    attacker = 'vagabond'
    defender = 'cat'
    dice_rolls = [3, 3]
    game.vagabond.relations['bird'] = "friendly"
    game.vagabond.allied_soldiers = ['bird', 'bird', 'bird']
    game.vagabond.items_to_damage = ['bird',  Item('torch'), 'bird', Item('sword')]

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['bird'] == 2
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].damaged == True
    assert game.vagabond.relations['bird'] == "friendly"

    # VAGABOND attacker vs cat with bird allies doesn't turn hostile
    game.map.places['H'].update_pieces(soldiers ={'cat': 0, 'bird': 3, 'alliance': 0}, buildings = [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')], tokens = [])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    defender_piece_lose_priorities = []
    attacker_piece_lose_priorities = []
    attacker = 'vagabond'
    defender = 'bird'
    dice_rolls = [3, 3]
    game.vagabond.relations['bird'] = "friendly"
    game.vagabond.allied_soldiers = ['bird', 'bird', 'bird']
    game.vagabond.items_to_damage = ['bird',  Item('torch'), 'bird', Item('sword'), Item('boot')]

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 2
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].damaged == True
    assert game.vagabond.relations['bird'] == "hostile"

    # ARMOERS CAT VS BIRD
    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    # CAT VS BIRD more bird, roost dead
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.marquise.armorers = True
    game.marquise.persistent_effect_deck.add_card(Card(*total_common_card_info[50]))
    
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [True, False]) #armoeres index 0 attac 1 def
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 3
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]
    assert game.marquise.armorers == False

    #  CAT VS BIRD ARMORERS
    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    # CAT VS BIRD more bird, roost dead
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.eyrie.armorers = True
    game.eyrie.persistent_effect_deck.add_card(Card(*total_common_card_info[50]))
    
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, True]) #armoeres index 0 attac 1 def
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['H'].soldiers['bird'] == 1
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert game.eyrie.armorers == False

    # BRUTAL CAT VS BIRD
    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    # CAT VS BIRD more bird, roost dead
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 2, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.marquise.brutal_tactics = True
    
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False], brutal_tactics=True) #armoeres index 0 attac 1 def
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]
    assert game.marquise.brutal_tactics == True


    # CAT VS BIRD sappers
    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    # CAT VS BIRD more bird, roost dead
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.eyrie.sappers = True
    game.eyrie.persistent_effect_deck.add_card(Card(*total_common_card_info[41]))
    
    attacker_piece_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_piece_lose_priorities = ['roost']

    attacker_chosen_pieces = game.priority_to_list(attacker_piece_lose_priorities, 'H', attacker)
    defender_chosen_pieces = game.priority_to_list(defender_piece_lose_priorities, 'H', defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False], sappers=True) #armoeres index 0 attac 1 def
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 1
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]
    assert game.eyrie.sappers == False
