import sys
sys.path.append('.')
from item import Item
from configs import total_common_card_info
from deck import Deck, Card
from dtos import MoveDTO, CraftDTO, OverworkDTO
from game import Game
from actors import Vagabond, Alliance, Marquise, Eyrie


def test_movement_slip():
    game = Game()

    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])


    game.slip(game.map.places['D'], card_to_give_if_no_sympathy)
    game.map.check_vagabond()
    assert game.map.places['D'].vagabond_is_here == True
    assert len(game.vagabond.deck.cards) == 5

    game.map.places['C'].update_pieces(tokens = ['sympathy'])
    game.slip(game.map.places['C'], card_to_give_if_no_sympathy)
    game.map.check_vagabond()
    assert game.map.places['C'].vagabond_is_here == True
    assert len(game.vagabond.deck.cards) == 4
    assert len(game.alliance.supporter_deck.cards) == 5

    game.slip(game.map.places['M'], card_to_give_if_no_sympathy)
    assert game.map.places['M'].vagabond_is_here == True

    game.vagabond = Vagabond(game.map)
    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])
    game.map.move_vagabond('C')
    move_action = MoveDTO(start = 'C', end = 'D', how_many = 0, who = 'vagabond')
    game.move(move_action, card_to_give_if_no_sympathy)
    assert game.map.places['D'].vagabond_is_here == True
    assert len(game.vagabond.deck.cards) == 1
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].exhausted == True

    game.vagabond.refresh_item(Item('boot'))
    move_action = MoveDTO(start = 'D', end = 'C', how_many = 0, who = 'vagabond')
    game.move(move_action, card_to_give_if_no_sympathy)
    assert game.map.places['C'].vagabond_is_here == True
    assert len(game.vagabond.deck.cards) == 0
    assert len(game.alliance.supporter_deck.cards) == 6

    move_action = MoveDTO(start = 'C', end = 'H', how_many = 1, who = 'cat')
    game.move(move_action, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['C'].soldiers['cat'] == 0 

    move_action = MoveDTO(start = 'L', end = 'I', how_many = 6, who = 'bird')
    game.move(move_action, card_to_give_if_no_sympathy)    
    assert game.map.places['I'].soldiers['bird'] == 6
    assert game.map.places['L'].soldiers['bird'] == 0

    game.vagabond.repair_and_refresh_all()
    game.map.move_vagabond('I')
    game.vagabond.relations['bird'] = "friendly"
    move_action = MoveDTO(start = 'I', end = 'L', how_many = 0, who = 'vagabond', vagabond_allies=(6, 'bird'))
    game.move(move_action, card_to_give_if_no_sympathy)
    assert game.map.places['L'].soldiers['bird'] == 6
    assert game.map.places['I'].soldiers['bird'] == 0
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].exhausted == True

    game.vagabond.repair_and_refresh_all()
    game.map.move_vagabond('I')
    game.vagabond.relations['bird'] = "hostile"
    game.vagabond.add_item(Item('boot'))
    move_action = MoveDTO(start = 'I', end = 'L', how_many = 0, who = 'vagabond')
    game.move(move_action, card_to_give_if_no_sympathy)
    for item in game.vagabond.satchel:
        if item.name == 'boot':
            assert item.exhausted == True



def test_craft():
    game = Game()
    game.eyrie = Eyrie(game.map, 'Despot')
    game.marquise = Marquise(game.map)
    game.alliance = Alliance(game.map)
    game.vagabond = Vagabond(game.map)

    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])

    game.eyrie.deck.add_card(Card(*total_common_card_info[11]))
    game.eyrie.deck.add_card(Card(*total_common_card_info[13]))
    
    # regular item regular cat
    game.marquise.deck.add_card(Card(*total_common_card_info[23]))
    game.marquise.deck.add_card(Card(*total_common_card_info[3]))
    game.marquise.refresh_craft_activations(game.map)
    options = game.marquise.get_options_craft(game.map)
    game.craft(game.marquise, options[0])
    assert len(game.marquise.deck.cards) == 1
    assert len(game.discard_deck.cards) == 1
    assert len(game.marquise.items) == 1
    assert game.marquise.victory_points == 1

    # favor regular cat
    game.map.places['D'].update_pieces(buildings = [("workshop", "cat"), ("workshop", "cat")])
    game.map.places['F'].update_pieces(buildings = [("workshop", "cat")])
    game.marquise.refresh_craft_activations(game.map)
    game.map.move_vagabond('D')

    game.marquise.deck.add_card(Card(*total_common_card_info[4]))
    options = game.marquise.get_options_craft(game.map)
    game.craft(game.marquise,options[options.index(CraftDTO(Card(*total_common_card_info[4])))])
    assert game.map.places['L'].soldiers['bird'] == 0
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].damaged == True
    assert game.map.places['D'].soldiers['cat'] == 1

    # dominance persistents
    game.marquise.victory_points = 11
    game.marquise.deck.add_card(Card(*total_common_card_info[8]))
    options = game.marquise.get_options_craft(game.map)
    game.craft(game.marquise, options[options.index(CraftDTO(Card(*total_common_card_info[8])))])
    assert game.marquise.win_condition == "rabbit"

    # bird vps
    assert game.eyrie.victory_points == 0
    game.map.places['G'].update_pieces(buildings = [("roost", "bird"), ("ruin", "No one")])
    game.map.places['J'].update_pieces(buildings = [("roost", "bird"), ("ruin", "No one")])
    game.map.update_owners()
    game.eyrie.refresh_craft_activations(game.map)
    game.eyrie.deck.add_card(Card(*total_common_card_info[14]))
    options = game.eyrie.get_options_craft(game.map)
    game.craft(game.eyrie, options[options.index(CraftDTO(Card(*total_common_card_info[14])))])
    assert game.eyrie.victory_points == 1
    assert len(game.eyrie.deck.cards) == 2


    # Vagabond,
    assert game.vagabond.victory_points == 0
    game.vagabond.add_item(Item("hammer"))
    game.vagabond.add_item(Item("hammer"))
    game.vagabond.deck.add_card(Card(*total_common_card_info[3]))
    options = game.vagabond.get_options_craft(game.map)
    game.craft(game.vagabond, options[options.index(CraftDTO(Card(*total_common_card_info[3])))])
    assert game.vagabond.victory_points == 3
    assert Item("money") in game.vagabond.other_items


def test_bird_builder_craft():
    game = Game()
    game.eyrie = Eyrie(game.map, 'Builder')
    game.marquise = Marquise(game.map)
    game.alliance = Alliance(game.map)
    game.vagabond = Vagabond(game.map)

    game.eyrie.deck.add_card(Card(*total_common_card_info[11]))
    game.eyrie.deck.add_card(Card(*total_common_card_info[13]))
    

    assert game.eyrie.victory_points == 0
    game.map.places['G'].update_pieces(buildings = [("roost", "bird"), ("ruin", "No one")])
    game.map.places['J'].update_pieces(buildings = [("roost", "bird"), ("ruin", "No one")])
    game.map.update_owners()
    game.eyrie.refresh_craft_activations(game.map)
    game.eyrie.deck.add_card(Card(*total_common_card_info[14]))
    options = game.eyrie.get_options_craft(game.map)
    game.craft(game.eyrie, options[options.index(CraftDTO(Card(*total_common_card_info[14])))])
    assert game.eyrie.victory_points == 2
    assert len(game.eyrie.deck.cards) == 2


def test_build():
    game = Game()

    game.cat_birdsong_wood()

    options = game.marquise.get_build_options(game.map)
    options.sort(key=lambda x: (x[0], x[1]))
    game.build(place=options[0][0], building=options[0][1], actor=game.marquise, cost = options[0][2])
    assert game.marquise.victory_points == 1
    assert game.map.places['B'].building_slots == [('recruiter', 'cat'), ('empty', 'No one')]
    assert game.map.count_on_map(('token', "wood")) == 0


def test_recruit_and_add_to_resolve():
    game = Game()

    game.cat_birdsong_wood()

    options = game.marquise.get_can_recruit(game.map)
    if options:
        game.recruit_cat()
    assert game.map.places['E'].soldiers['cat'] == 2

    decree_options = game.eyrie.get_decree_options()
    game.add_card_to_decree(*decree_options[0])
    game.eyrie.refresh_temp_decree()

    options = game.eyrie.get_resolve_recruit(game.map)
    game.recruit(options[0][0], game.eyrie)
    assert game.map.places['L'].soldiers['bird'] == 7

    assert game.eyrie.victory_points == 0
    game.bird_turmoil("Charismatic")
    options = game.eyrie.get_resolve_recruit(game.map)
    game.recruit(options[0][0], game.eyrie)
    assert game.map.places['L'].soldiers['bird'] == 9
    assert game.eyrie.victory_points == 0
    assert sorted(game.eyrie.avaible_leaders) == sorted(["Builder", "Commander"])
    

def test_overwork():
    game = Game()
    assert game.map.count_on_map(('token', 'wood')) == 0
    game.marquise.deck.add_card(Card(*total_common_card_info[49]))
    game.overwork(game.map.places['A'], 49)
    assert game.map.count_on_map(('token', 'wood')) == 1
    assert game.marquise.deck.get_the_card(49) == "Card not in the deck"


def test_revolt_sympathy():
    game = Game()
    options = game.alliance.get_spread_sympathy_options(game.map)
    options.sort(key=lambda x: (x[0], x[1]))
    assert options[0] == ("B", [])
    game.spread_sympathy(*options[0])
    assert game.map.places['B'].tokens == ["sympathy"]

    options = game.alliance.get_spread_sympathy_options(game.map)
    options.sort(key=lambda x: (x[0], x[1]))
    assert options[0] == ("C", [51])
    game.spread_sympathy(*options[0])
    assert game.map.places['C'].tokens == ["sympathy"]

    game.alliance.supporter_deck.add_card(Card(*total_common_card_info[15]))
    game.alliance.supporter_deck.add_card(Card(*total_common_card_info[16]))

    options = game.alliance.get_revolt_options(game.map)
    options.sort(key=lambda x: (x[0], x[1], x[2])) #place card1 card2 soldiers to gain
    assert options[0] == (game.map.places['C'], 15, 16, 1)

    game.revolt(*options[0])

    assert game.map.places['C'].soldiers['alliance'] == 1
    assert game.map.places['C'].tokens == ["sympathy"]
    assert game.alliance.supporter_deck.get_the_card(15) == "Card not in the deck"
    assert game.alliance.supporter_deck.get_the_card(16) == "Card not in the deck"
    assert game.map.places['C'].building_slots == [("base", "alliance"), ("empty", "No one")]
    assert game.discard_deck.get_the_card(15) == Card(*total_common_card_info[15])


def test_mobilize_train_organize():
    game = Game()

    options = game.alliance.get_mobilize_options()
    options.sort()
    game.mobilize(options[1])
    assert game.alliance.deck.get_the_card(29) == "Card not in the deck"


    game.map.places['L'].update_pieces(buildings = [("base", 'alliance')])

    assert len(game.alliance.deck.cards) == 3
    options = game.alliance.get_train_options(game.map)
    options.sort()
    game.train(options[0][0])
    assert game.alliance.deck.get_the_card(1) == "Card not in the deck"
    assert game.alliance.total_officers == 1

    game.map.places['D'].update_pieces(soldiers = {'cat': 1, 'bird': 1, 'alliance': 1})
    options = game.alliance.get_organize_options(game.map)
    options.sort()
    game.organize(options[0][0])
    assert game.map.places['D'].tokens == ['sympathy']
    assert game.map.places['D'].soldiers == {'cat': 1, 'bird': 1, 'alliance': 0}


    game.map.places['D'].update_pieces(soldiers = {'cat': 1, 'bird': 1, 'alliance': 1})
    options = game.alliance.get_organize_options(game.map)

    assert options == []

def test_vagabond_explore_stuff():
    game = Game()
    #AID
    game.map.move_vagabond('L')
    options = game.vagabond.get_aid_options(game.map, (game.marquise, game.eyrie, game.alliance))
    options.sort(key=lambda x: x[0])
    conseq_aids = game.aid(*options[0], 0)
    assert conseq_aids == 0
    assert game.vagabond.victory_points == 1
    assert game.vagabond.deck.get_the_card(3) == "Card not in the deck"
    assert game.eyrie.deck.get_the_card(3) != "Card not in the deck"

    game.map.move_vagabond('N')
    options = game.vagabond.get_aid_options(game.map, (game.marquise, game.eyrie, game.alliance))
    assert options == []

    game.map.move_vagabond('A')
    game.marquise.items.append(Item("sword"))
    game.vagabond.relations[game.marquise.name] = "good"
    conseq_aids = 0
    options = game.vagabond.get_aid_options(game.map, (game.marquise, game.eyrie, game.alliance))
    conseq_aids = game.aid(*options[0], conseq_aids)
    assert conseq_aids == 1
    assert game.vagabond.victory_points == 1
    assert game.vagabond.deck.get_the_card(33) == "Card not in the deck"
    assert game.marquise.deck.get_the_card(33) != "Card not in the deck"
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item("sword"))] == Item("sword")


    game.marquise.items.append(Item("sword"))
    options = game.vagabond.get_aid_options(game.map, (game.marquise, game.eyrie, game.alliance))
    conseq_aids = game.aid(*options[0], conseq_aids)
    assert conseq_aids == 0
    assert game.vagabond.victory_points == 3
    assert game.vagabond.relations[game.marquise.name] == "very good"

    # EXPLORE
    game.map.move_vagabond('H')
    options = game.vagabond.get_ruin_explore_options(game.map)
    if options:
        game.explore_ruin(game.map.vagabond_position)
    assert game.vagabond.victory_points == 4
    assert ('ruin', Item("boot")) not in game.map.places['H'].building_slots
    assert game.vagabond.satchel.count(Item("boot")) == 2

    # QUEST
    assert len(game.vagabond.deck.cards) == 1
    assert len(game.marquise.deck.cards) == 4
    game.vagabond.refresh_item(Item("torch"))
    options = game.vagabond.get_thief_ability(game.map)
    game.steal(options[0])
    assert len(game.vagabond.deck.cards) == 2
    assert len(game.marquise.deck.cards) == 3
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item("torch"))].exhausted == True

    game.vagabond.refresh_item(Item("torch"))
    game.vagabond.add_item(Item("crossbow"))
    options = game.vagabond.get_quest_options(game.map)
    options.sort(key=lambda x: (x[0], x[1]))
    game.complete_quest(*options[1])
    assert game.vagabond.victory_points == 4
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item("torch"))].exhausted == True
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item("crossbow"))].exhausted == True
    assert len(game.vagabond.deck.cards) == 3

    # STRIKE
    game.vagabond.repair_and_refresh_all()
    game.vagabond.deck.add_card(Card(*total_common_card_info[22]))
    game.map.places['H'].update_pieces(tokens = ['sympathy', 'wood'])
    options = game.vagabond.get_strike_options(game.map)
    options.sort(key=lambda x: (x[1], x[2]))
    game.strike(*options[1], card_to_give_if_sympathy=22)
    assert game.vagabond.victory_points == 4
    assert game.map.places['H'].tokens == ['sympathy', 'wood']
    assert game.map.places['H'].soldiers == {'cat': 0, 'bird': 0, 'alliance': 0}
    game.strike(*options[0], card_to_give_if_sympathy=22) # Should not be used like this, but it's just a test
    assert game.vagabond.victory_points == 5
    assert game.map.places['H'].tokens == ['wood']
    assert game.alliance.supporter_deck.get_the_card(22) != "Card not in the deck"

def test_cards():

    #STAND AND DELIVER
    game = Game()
    game.marquise.stand_and_deliver = True
    options = game.marquise.stand_and_deliver_options([game.eyrie, game.alliance, game.vagabond])
    game.stand_and_deliver(taker=game.marquise, victim=options[1])
    assert len(game.marquise.deck.cards) == 4
    assert len(game.eyrie.deck.cards) == 3
    assert game.eyrie.victory_points == 1

    # SCOUTING PARTY and Ambush IN BATTLE TESTS

    # CODEBREAKERS and crafting persistants in general
    game.alliance.deck.add_card(game.deck.get_the_card(17))
    game.map.places['E'].update_pieces(tokens = ['sympathy'])
    game.alliance.refresh_craft_activations(game.map)
    options = game.alliance.get_options_craft(game.map)
    game.craft(game.alliance, options[0])
    assert game.alliance.codebreakers == True

    #Better_burrow_bank
    game.eyrie.better_burrow_bank = True
    options = game.eyrie.bbb_options([game.marquise, game.alliance, game.vagabond])
    options.sort(key=lambda x: x.name)
    assert options[0].name == "alliance"

    game.eyrie.tax_collector = True
    options = game.eyrie.get_tax_collector_options(game.map)
    assert options == [False, 'L']

    game.map.places['H'].update_pieces(buildings = [('workshop', 'cat'), ('workshop', 'cat'), ('workshop', 'cat')])
    game.marquise.deck.cards = []
    game.marquise.deck.add_card(Card(*total_common_card_info[53]))
    game.marquise.refresh_craft_activations(game.map)
    options = game.marquise.get_options_craft(game.map)
    game.craft(game.marquise, options[0])
    assert game.marquise.royal_claim == True
    assert game.marquise.deck.cards == []

test_craft()