
def stand_and_deliver(game, taker, victim):
    if not victim:
        return
    victim.deck.shuffle_deck()
    taker.deck.add_card(victim.deck.draw_card())
    victim.victory_points += 1
    game.check_victory_points()
       
def swap_discarded_dominance_card(game, actor, card_id1, card_id2):
    actor.deck.add_card(game.dominance_discard_deck.get_the_card(card_id1))
    game.discard_deck.add_card(actor.deck.get_the_card(card_id2))
       
def field_hospital(game, wounded_soldiers, card_ID):
    logging.debug(f"Cat used field_hospital saving {wounded_soldiers} soldiers ")
    not_none_if_keep = [place.name if 'keep' in place.tokens else None for place in game.map.places.values()]
    keep_position  = next(item for item in not_none_if_keep if item is not None)
    game.map.places[keep_position].soldiers['cat'] += wounded_soldiers
    if total_common_card_info[card_ID][2] == "dominance":
        game.dominance_discard_deck.add_card(game.marquise.deck.get_the_card(card_ID))
    else:
        game.discard_deck.add_card(game.marquise.deck.get_the_card(card_ID))
           
def better_burrow_bank(game, actor, other):
    actor.deck.add_card(game.deck.draw_card())
    if len(game.deck.cards) <= 0: # DECK ONE LINER
        game.deck = copy(game.discard_deck)
        game.deck.shuffle_deck()
        game.discard_deck = Deck(empty=True)
    other.deck.add_card(game.deck.draw_card())
       
def tax_collection(game, actor, placename):
    game.map.places[placename].soldiers[actor.name] -= 1
    actor.deck.add_card(game.deck.draw_card())
    game.map.places[placename].update_owner()
    if len(game.deck.cards) <= 0: # DECK ONE LINER
        game.deck = copy(game.discard_deck)
        game.deck.shuffle_deck()
        game.discard_deck = Deck(empty=True)
           
def activate_royal_claim(game, actor):
    for place in game.map.places.values():
        if place.owner == actor.name:
            actor.victory_points += 1
    game.check_victory_points()
    actor.royal_claim = False
    game.discard_deck.add_card(actor.persistent_effect_deck.get_the_card(53))
       
def cat_birdsong_wood(game):
    for key in list(game.map.places.keys()):
        for building_slot in game.map.places[key].building_slots:
            if building_slot[0] == "sawmill" and game.map.count_on_map(('token', 'wood')) < 8:
                game.map.places[key].update_pieces(tokens = game.map.places[key].tokens + ["wood"])  
                   
def add_card_to_decree(game, action, card_ID, card_suit):
    game.eyrie.decree[action].append((card_ID, card_suit))
    if game.eyrie.decree_deck.add_card(game.eyrie.deck.get_the_card(card_ID)) is not None:
        raise ValueError("Eyrie tried to add wrong card to decree deck")
       
def place_roost_if_zero_roost(game, place_name):
    try:
        game.map.places[place_name].building_slots[game.map.places[place_name].building_slots.index(('empty', 'No one'))] = ('roost', 'bird')
        game.map.places[place_name].soldiers['bird'] += 3
        game.map.places[place_name].update_owner()
    except ValueError:
        raise ValueError("Error in get_no_roosts_left_options")
       
def cat_use_bird_card_to_gain_move(game, cardID):
    if total_common_card_info[cardID][2] == "dominance":
        game.dominance_discard_deck.add_card(game.marquise.deck.get_the_card(cardID))
    else:
        game.discard_deck.add_card(game.marquise.deck.get_the_card(cardID))
           
# Alliance
def revolt(game, place, card_ID1, card_ID2, soldiers_to_gain):
    # Clear all buildings
    victory_points = 0
    victory_points += place.clear_buildings()
    victory_points += place.clear_tokens(exception_faction = "alliance")
    wounded_cat_soldiers = place.clear_soldiers(exception_faction="alliance")
    # Add a base for the alliance
    place.add_building('base', 'alliance')
    # If the vagabond is present, damage 3 vagabond items
    if place.vagabond_is_here:
        for item in game.vagabond.items_to_damage[:3]:
            logging.debug(f"Revolt damaged vagabonds {item}")
            game.vagabond.damage_item(item)
    if total_common_card_info[card_ID1][2] == "dominance":
        game.dominance_discard_deck.add_card(game.alliance.supporter_deck.get_the_card(card_ID1))
    else:
        game.discard_deck.add_card(game.alliance.supporter_deck.get_the_card(card_ID1))
    if total_common_card_info[card_ID2][2] == "dominance":
        game.dominance_discard_deck.add_card(game.alliance.supporter_deck.get_the_card(card_ID2))
    else:
        game.discard_deck.add_card(game.alliance.supporter_deck.get_the_card(card_ID2))
    for _ in range(soldiers_to_gain):
        if sum([place.soldiers["alliance"] for place in game.map.places.values()]) + game.alliance.total_officers >= 10:
            break
        place.soldiers["alliance"] += 1
    if sum([place.soldiers["alliance"] for place in game.map.places.values()]) + game.alliance.total_officers <= 10:
        game.alliance.total_officers += 1
    place.update_owner()
    game.alliance.victory_points += victory_points
    game.check_victory_points()
    return wounded_cat_soldiers
   
def spread_sympathy(game, place_name, card_ids):
    game.map.places[place_name].update_pieces(tokens = game.map.places[place_name].tokens + ['sympathy'])
    for cardID in card_ids:
        if total_common_card_info[cardID][2] == "dominance":
            game.dominance_discard_deck.add_card(game.alliance.supporter_deck.get_the_card(cardID))
        else:
            game.discard_deck.add_card(game.alliance.supporter_deck.get_the_card(cardID))
    victory_points = sympathy_VPs[game.map.count_on_map(what_to_look_for=('token', 'sympathy'), per_suit = False)-1]
    game.alliance.victory_points += victory_points
    game.check_victory_points()
       
def slip(game, placename, card_to_give_if_sympathy):
    if 'sympathy' in game.map.places[placename].tokens:
        if not card_to_give_if_sympathy and len(game.vagabond.deck.cards) > 0:
            options = game.alliance.take_card_from_a_player_options(game.vagabond)
            card_id = alliance_choose_card(options)
            game.alliance.supporter_deck.add_card(game.vagabond.deck.get_the_card(card_id))
        if not card_to_give_if_sympathy and len(game.vagabond.deck.cards) == 0:
            game.alliance.supporter_deck.add_card(game.deck.draw_card())
            if len(game.deck.cards) <= 0:
                game.deck = copy(game.discard_deck)
                game.deck.shuffle_deck()
                game.discard_deck = Deck(empty=True)
        else:
            game.alliance.supporter_deck.add_card(game.vagabond.deck.get_the_card(card_to_give_if_sympathy))
    game.map.move_vagabond(placename)
       
def get_battle_damages(game, attacker, defender, dice_rolls, place_name, armorers: list[bool, bool] = False, sappers:bool = False, brutal_tactics:bool=False, card_ID=None):
    """
    :param attacker: str
    :param defender: str
    :param dice_rolls: list, 2 0-3 nums descending order
    """
    # So vagabond cant attack its own soldiers with its own soldiers
    if attacker == "vagabond":
        if game.vagabond.relations[defender] == "friendly":
            game.vagabond.allied_soldiers = game.remove_soldiers_from_vagabond_items(game.vagabond.allied_soldiers, defender)
            game.vagabond.items_to_damage = game.remove_soldiers_from_vagabond_items(game.vagabond.items_to_damage, defender)
    dmg_attacker = 0
    dmg_defender = 0
    # Regular battle
    if attacker != 'vagabond' and defender != 'vagabond':
        if defender != 'alliance':
            dmg_attacker += min(dice_rolls[0], game.map.places[place_name].soldiers[attacker])
            dmg_defender += min(dice_rolls[1], game.map.places[place_name].soldiers[defender])
        elif defender == 'alliance':
            dmg_attacker += min(dice_rolls[1], game.map.places[place_name].soldiers[attacker])
            dmg_defender += min(dice_rolls[0], game.map.places[place_name].soldiers[defender])
    elif defender == 'vagabond':
            dmg_attacker += min(dice_rolls[0], game.map.places[place_name].soldiers[attacker])
            dmg_defender += min(dice_rolls[1], len(list(item for item in game.vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(game.vagabond.allied_soldiers))
    elif attacker == 'vagabond':
        if defender != 'alliance':
            dmg_attacker += min(dice_rolls[0], len(list(item for item in game.vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(game.vagabond.allied_soldiers))
            dmg_defender += min(dice_rolls[1], game.map.places[place_name].soldiers[defender])
        elif defender == 'alliance':
            dmg_attacker += min(dice_rolls[1], len(list(item for item in game.vagabond.satchel if item.name == "sword" and not item.damaged)) +  len(game.vagabond.allied_soldiers))
            dmg_defender += min(dice_rolls[0], game.map.places[place_name].soldiers[defender])
    if armorers[0]:
        for actor in [game.eyrie, game.vagabond, game.marquise, game.alliance]:
            if actor.name == attacker:
                actor.armorers = False
                game.discard_deck.add_card(actor.persistent_effect_deck.get_a_card_like_it("armorers"))
        dmg_defender = 0
    if armorers[1]:
        for actor in [game.eyrie, game.vagabond, game.marquise, game.alliance]:
            if actor.name == defender:
                actor.armorers = False
                game.discard_deck.add_card(actor.persistent_effect_deck.get_a_card_like_it("armorers"))
        dmg_attacker = 0        
    # No defender
    if  defender != 'vagabond' and game.map.places[place_name].soldiers[defender] == 0:
        dmg_attacker = min(dmg_attacker, 1)
    if sappers:
        for actor in [game.eyrie, game.vagabond, game.marquise, game.alliance]:
            if actor.name == defender:
                actor.sappers = False
                game.discard_deck.add_card(actor.persistent_effect_deck.get_a_card_like_it("sappers"))
        dmg_defender += 1
    if brutal_tactics:
        dmg_attacker += 1
    for actor in [game.eyrie, game.vagabond, game.marquise, game.alliance]:
        # OWL
        if attacker == 'bird' and actor.name == 'bird' and actor.leader == 'Commander':
            dmg_attacker += 1
        if brutal_tactics and actor.name == defender:
            actor.victory_points += 1
    if card_ID:
        game.eyrie.remove_from_temp_decree(card_ID, 'battle')
    game.check_victory_points()
    logging.debug(f"Battle damages: attacker {dmg_attacker}, defender {dmg_defender}")
    return dmg_attacker, dmg_defender
   
   
def resolve_battle(game, place, attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces=None, defender_chosen_pieces=None, card_to_give_if_sympathy=None):
    """
    :param place: Map
    :param attacker: str
    :param defender: str
    :param dmg_attacker int dmges from get battle damages
    :param dmg_defender int 
    :param attacker_chosen_pieces: if more dmg than soldiers, what buildings to destroy (owner chooses)
    :param defender_chosen_pieces: if more dmg than soldiers, what buildings to destroy (owner chooses)
    :param card_to_give_if_sympathy: if sympathy is removed, what card to give to alliance
    :return: wounded cat soldiers if there's any, None if no cat is present
    """ 
    if attacker != "vagabond" and place.soldiers[attacker] == 0:
        logging.debug("No attacker because no soldiers")
        return
    
    # So vagabond cant attack its allies with its allies
    if attacker == "vagabond":
        if game.vagabond.relations[defender] == "friendly":
            game.vagabond.allied_soldiers = game.remove_soldiers_from_vagabond_items(game.vagabond.allied_soldiers, defender)
            game.vagabond.items_to_damage = game.remove_soldiers_from_vagabond_items(game.vagabond.items_to_damage, defender)
    total_lost_soldiers_attacker = 0 # For field hospital
    total_lost_soldiers_defender = 0 # For field hospital
    victory_points_attacker = 0
    victory_points_defender = 0
    sympathy_killed = False
    # Process attacker's damage
    if defender == "vagabond":
        logging.debug(f"Vagabond getting {game.vagabond.items_to_damage[:dmg_attacker]} damaged")
        for item in game.vagabond.items_to_damage[:dmg_attacker]:
            game.vagabond.damage_item(item)
    else:
        # If attacker dealt more damage than defender's soldiers, remove additional pieces
        extra_dmg_attacker = max(dmg_attacker - place.soldiers[defender], 0)
        # Accounting for the killed soldiers
        if attacker == "vagabond": 
            logging.debug(f"vagabond is getting {dmg_attacker-extra_dmg_attacker} points")
            victory_points_attacker += dmg_attacker-extra_dmg_attacker
        # If a defender soldier dies while set relations to hostile
        if attacker == "vagabond" and dmg_attacker-extra_dmg_attacker > 0 and game.vagabond.relations[defender] != "hostile":
            logging.debug(f"vagabond became hostile with {defender}")
            game.vagabond.relations[defender] = "hostile"
            victory_points_attacker-=1 # THAT one soldier doesn't count as VP
            logging.debug(f"vagabond is getting getting 1 less points due to the first soldier was killed without being hostile points")
        if extra_dmg_attacker <=0:
            logging.debug(f"{defender} lost {dmg_attacker} soldiers")
            total_lost_soldiers_defender = dmg_attacker
            place.soldiers[defender] -= dmg_attacker
        else:
            logging.debug(f"{defender} lost {place.soldiers[defender]} soldiers")
            total_lost_soldiers_defender = place.soldiers[defender]
            place.soldiers[defender] = 0
            for piece in defender_chosen_pieces[:extra_dmg_attacker]:
                if piece[1] == "building":
                    place.remove_building(piece[0])
                    logging.debug(f"{defender} lost a {piece[0]}")
                    victory_points_attacker += 1
                    if attacker == "vagabond" and game.vagabond.relations[defender] == "hostile":
                        victory_points_attacker += 1
                    if piece[0] == 'base':
                        game.alliance.losing_a_base(place_suit=place.suit, discard_deck=game.discard_deck)
                    if piece[0] == 'sawmill' or piece[0] == 'workshop' or piece[0] == 'recruiter':
                        logging.debug(f"Marquise lost {buildings_list_marquise[piece[0]]['VictoryPoints'][game.map.count_on_map(('building', piece[0]))]} VPs, as it lost a {piece[0]}")
                        game.marquise.victory_points -= buildings_list_marquise[piece[0]]["VictoryPoints"][game.map.count_on_map(("building", piece[0]))] # +1 because we already removed the building
                elif piece[1] == "token":
                    logging.debug(f"{defender} lost {piece[0]}")
                    place.tokens.remove(piece[0])
                    victory_points_attacker += 1
                    if attacker == "vagabond" and game.vagabond.relations[defender] == "hostile":
                        victory_points_attacker += 1
                    if piece[0] == "sympathy":
                        sympathy_killed = True
                        game.alliance.victory_points -= sympathy_VPs[game.map.count_on_map(("token", "sympathy"))]
    # Process defender's damage
    if attacker == "vagabond":
        items = 0
        soldiers = 0
        for item in game.vagabond.items_to_damage[:dmg_defender]:
            game.vagabond.damage_item(item, place)
            if isinstance(item, Item):
                items += 1
            else:
                soldiers += 1
        if soldiers > items:
            game.vagabond.relations[item] = "hostile"
    else:
        # If defender dealt more damage than attacker's soldiers, remove additional pieces
        extra_dmg_defender = max(dmg_defender - place.soldiers[attacker], 0)
        if defender == "vagabond" and dmg_defender-extra_dmg_defender > 0:
            game.vagabond.relations[attacker] = "hostile"
        if extra_dmg_defender <=0:
            place.soldiers[attacker] -= dmg_defender
            total_lost_soldiers_attacker = dmg_defender
            logging.debug(f"{attacker} lost {dmg_defender} soldiers")
        else:
            total_lost_soldiers_attacker = place.soldiers[attacker]
            logging.debug(f"{attacker} lost {place.soldiers[attacker]} soldiers")
            place.soldiers[attacker] = 0
            for piece in attacker_chosen_pieces[:extra_dmg_defender]:
                if piece[1] == "building":
                    logging.debug(f"{attacker} lost a {piece[0]}")
                    place.remove_building(piece[0])
                    victory_points_defender += 1
                    if piece[0] == 'sawmill' or piece[0] == 'workshop' or piece[0] == 'recruiter':
                        logging.debug(f"Marquise lost {buildings_list_marquise[piece[0]]['VictoryPoints'][game.map.count_on_map(('building', piece[0]))]} VPs, as it lost a {piece[0]}")
                        game.marquise.victory_points -= buildings_list_marquise[piece[0]]["VictoryPoints"][game.map.count_on_map(("building", piece[0]))] # +1 because we already removed the building
                elif piece[1] == "token":
                    logging.debug(f"{attacker} lost {piece[0]}")
                    place.tokens.remove(piece[0])
                    victory_points_defender += 1
                    if piece[0] == "sympathy":
                        sympathy_killed = True
                        game.alliance.victory_points -= sympathy_VPs[game.map.count_on_map(("token", "sympathy"))]
    for actor in [game.eyrie, game.vagabond, game.marquise, game.alliance]:
        if actor.name == attacker:
            actor.victory_points += victory_points_attacker
            if actor.name != "alliance":
                if sympathy_killed and card_to_give_if_sympathy:
                    logging.debug(f"alliance is getting {card_to_give_if_sympathy}")
                    game.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy))
                if sympathy_killed and not card_to_give_if_sympathy:
                    if len(actor.deck.cards) == 0:
                        logging.debug(f"alliance drew a card from the deck")
                        game.alliance.supporter_deck.add_card(game.deck.draw_card())
                    else:
                        logging.debug(f"alliance choose a card")
                        options = game.alliance.take_card_from_a_player_options(game.vagabond)
                        card_id = alliance_choose_card(options)
                        game.alliance.supporter_deck.add_card(game.vagabond.deck.get_the_card(card_id))
        elif actor.name == defender:
            actor.victory_points += victory_points_defender
            if actor.name != "alliance":
                if sympathy_killed and card_to_give_if_sympathy:
                    game.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy))
                if sympathy_killed and not card_to_give_if_sympathy:
                    if len(actor.deck.cards) == 0:
                        game.alliance.supporter_deck.add_card(game.deck.draw_card())
                    else:  
                        options = game.alliance.take_card_from_a_player_options(game.vagabond)
                        card_id = alliance_choose_card(options)
                        game.alliance.supporter_deck.add_card(game.vagabond.deck.get_the_card(card_id))
    place.update_owner()
    if len(game.deck.cards) <=0:
        game.deck = copy(game.discard_deck)
        game.deck.shuffle_deck()
        game.discard_deck = Deck(empty=True)
    game.check_victory_points()
    if attacker == "cat":
        return total_lost_soldiers_attacker
    if defender == "cat":
        return total_lost_soldiers_defender
       
       
def move(game, move_action, card_to_give_if_sympathy):
    if move_action.who != 'vagabond':
        game.map.places[move_action.start].soldiers[move_action.who] -= move_action.how_many
        game.map.places[move_action.end].soldiers[move_action.who] += move_action.how_many
    if move_action.who != 'alliance' and game.map.places[move_action.end].tokens.count("sympathy") > 0:
        for actor in [game.eyrie, game.vagabond, game.marquise]:
            if actor.name == move_action.who and card_to_give_if_sympathy:
                game.alliance.supporter_deck.add_card(actor.deck.get_the_card(card_to_give_if_sympathy))
            elif actor.name == move_action.who and not card_to_give_if_sympathy and len(actor.deck.cards) == 0:
                game.alliance.supporter_deck.add_card(game.deck.draw_card())
            elif actor.name == move_action.who and not card_to_give_if_sympathy and len(actor.deck.cards) > 0:
                options = game.alliance.take_card_from_a_player_options(game.vagabond)
                card_id = alliance_choose_card(options)
                game.alliance.supporter_deck.add_card(game.vagabond.deck.get_the_card(card_id))
    if len(game.deck.cards) <= 0:
        game.deck = copy(game.discard_deck)
        game.deck.shuffle_deck()
        game.discard_deck = Deck(empty=True)
    if move_action.who == 'vagabond':
        game.map.move_vagabond(move_action.end)
        boot_cost = 2 if game.vagabond.relations[game.map.places[move_action.end].owner] == 'hostile' else 1
        for _ in range(boot_cost):
            game.vagabond.exhaust_item(Item('boot'))
        if move_action.vagabond_allies[0]:
            game.map.places[move_action.start].soldiers[move_action.vagabond_allies[1]] -= move_action.vagabond_allies[0]
            game.map.places[move_action.end].soldiers[move_action.vagabond_allies[1]] += move_action.vagabond_allies[0]
    if move_action.who == 'alliance':
        for actor in [game.eyrie, game.vagabond, game.marquise]:
            if actor.name == move_action.who:
                actor.current_officers -= 1
    if move_action.who == "bird":
        game.eyrie.remove_from_temp_decree(move_action.card_ID, 'move')
    game.map.update_owners()
       
       
def craft(game, actor, costs: CraftDTO):
    wounded_cat_soldiers = None
    if costs.card.craft == "ambush":
        raise ValueError("Ambush is not a craftable card")
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
        game.map.craftables.remove(costs.card.craft)
        if actor.name == "bird" and actor.leader!= "Builder":
            actor.victory_points += 1
        else:
            actor.victory_points += costs.card.craft.crafting_reward()
        game.check_victory_points()
        game.discard_deck.add_card(actor.deck.get_the_card(costs.card.ID))
    elif costs.card.craft in persistent_effects:
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
        actor.persistent_effect_deck.add_card(actor.deck.get_the_card(costs.card.ID))
    # special effects
    elif costs.card.craft == "favor":
            wounded_cat_soldiers = game.favor(actor, costs.card.craft_suit)
            game.discard_deck.add_card(actor.deck.get_the_card(costs.card.ID))
    elif costs.card.craft == "dominance":
            game.dominance(actor, costs.card.card_suit)
            actor.deck.get_the_card(costs.card.ID) # remove from the game
    if wounded_cat_soldiers:
        return wounded_cat_soldiers
       
def favor(game, actor, suit):
    victory_points = 0
    for place in game.map.places.values():
        if place.suit == suit:
            wounded_cats = place.clear_soldiers(exception_faction=actor.name)
            victory_points += place.clear_buildings(exception_faction=actor.name)
            victory_points += place.clear_tokens(exception_faction=actor.name)
            if ('base', 'alliance') in place.building_slots and actor.name != "alliance":
                game.alliance.losing_a_base(place_suit=place.suit, discard_deck=game.discard_deck)
            if actor.name != "vagabond" and place.vagabond_is_here:
                for item in game.vagabond.items_to_damage[:3]:
                    game.vagabond.damage_item(item)
    actor.victory_points += victory_points
    game.check_victory_points()
    game.map.update_owners()
    return wounded_cats
   
   
def dominance(game, user, suit):
    if user == "vagabond":
        min_points = 100
        min_point_actorname = None
        for actor in [game.eyrie, game.marquise, game.alliance]:
            if actor != "vagabond" and actor.win_condition != "coalition_major":
                if actor.victory_points < min_points:
                    min_points = actor.victory_points
                    min_point_actorname = actor.name
        for actor in [game.eyrie, game.marquise, game.alliance]:
            if actor.name == min_point_actorname:
                actor.win_condition = "coalition_major"
        user.win_condition = "coalition_minor"
    else:
        user.win_condition = suit
           
           
def ambush(game, placename, attacker, defender, bird_or_suit_defender, bird_or_suit_attacker):
    if isinstance(defender, str):
        defender_conv = {
            "cat": game.marquise,
            "bird": game.eyrie,
            "alliance": game.alliance,
            "vagabond": game.vagabond
        }
        defender = defender_conv[defender]
    if isinstance(attacker, str):
        attacker_conv = {
            "cat": game.marquise,
            "bird": game.eyrie,
            "alliance": game.alliance,
            "vagabond": game.vagabond
        }
        attacker = attacker_conv[attacker]
    if bird_or_suit_defender == "suit":
        for card in defender.deck.cards:
            if card.craft == "ambush" and card.card_suit ==  game.map.places[placename].suit:
                game.discard_deck.add_card(defender.deck.get_the_card(card.ID))
    if bird_or_suit_defender == "bird":
        for card in defender.deck.cards:
            if card.craft == "ambush" and card.card_suit == "bird":
                game.discard_deck.add_card(defender.deck.get_the_card(card.ID))
    if bird_or_suit_attacker or attacker.scouting_party:
        if not attacker.scouting_party and bird_or_suit_attacker == "suit":
            for card in attacker.deck.cards:
                if card.craft == "ambush" and card.card_suit ==  game.map.places[placename].suit:
                    game.discard_deck.add_card(attacker.deck.get_the_card(card.ID))
        if not attacker.scouting_party and bird_or_suit_attacker == "bird":
            for card in attacker.deck.cards:
                if card.craft == "ambush" and card.card_suit == "bird":
                    game.discard_deck.add_card(attacker.deck.get_the_card(card.ID))
        return
 
    if attacker.name == "vagabond":
        for item in game.vagabond.items_to_damage[:2]:
            game.vagabond.damage_item(item)
    else:
        game.map.places[placename].soldiers[attacker.name] -= 2 
        game.map.places[placename].soldiers[attacker.name] = max(game.map.places[placename].soldiers[attacker.name], 0)
    game.map.places[placename].update_owner()
       
       
def build(game, place, actor, building, cost = 0, card_ID=None):
    if actor.name == "bird":
        actor.remove_from_temp_decree(card_ID, "build")
    if actor.name == "cat": #Choosing which woods to remove is too much work for now
        i = cost
        for _ in range(i):
            for place in game.map.places.values():
                if not i:
                    break
                if "wood" in place.tokens and place.owner == 'cat':
                    place.tokens.remove("wood")
                    i -= 1
            if not i:
                break
        actor.victory_points += buildings_list_marquise[building]["VictoryPoints"][game.map.count_on_map(("building", building))]
    for i in range(len(place.building_slots)):
        if place.building_slots[i] == ("empty", "No one"):
            place.building_slots[i] = (building, actor.name)
            break
    place.update_owner()
    game.check_victory_points()
       
       
def recruit_cat(game):
    for place in game.map.places.values():
        if ("recruiter", "cat") in place.building_slots and sum([place.soldiers["cat"] for place in game.map.places.values()]) < 25:
            place.soldiers["cat"] += 1
    game.map.update_owners()
       
       
def recruit(game, placename, actor, card_ID = None):
    if actor.name == "bird" and actor.leader == "Charismatic":
        game.map.places[placename].soldiers[actor.name] += 2
        game.map.places[placename].update_owner()   
    else:
        game.map.places[placename].soldiers[actor.name] += 1
        game.map.places[placename].update_owner()
    
    if actor.name == "bird":
        game.eyrie.remove_from_temp_decree(card_ID, 'recruit')
           
           
def overwork(game, placename, card_id):
    game.map.places[placename].tokens += ['wood']
    if total_common_card_info[card_id][2] == "dominance":
        game.dominance_discard_deck.add_card(game.marquise.deck.get_the_card(card_id))
    else:
        game.discard_deck.add_card(game.marquise.deck.get_the_card(card_id))
           
           
def eyrie_get_points(game):
    roosts = game.map.count_on_map(("building", "roost"))
    game.eyrie.victory_points += eyrie_roost_VPs[roosts-1]
    game.check_victory_points()
       
def bird_turmoil(game, new_commander):
    
    vp_loss = 0
    for decree_field in game.eyrie.decree.values():
        for value in decree_field:
            if value[1] == 'bird':
                vp_loss += 1
    game.eyrie.victory_points -= vp_loss
    game.eyrie.victory_points = max(game.eyrie.victory_points, 0)
    game.eyrie.change_role(new_commander)
    game.eyrie.setup_based_on_leader()
    # ALL cards to the discard_deck! Loyal viziers are not here.
    for card in game.eyrie.decree_deck.cards:
        if card.craft == "dominance":
            game.dominance_discard_deck.add_card(game.eyrie.decree_deck.get_the_card(card.ID)) 
        else:
            game.discard_deck.add_card(game.eyrie.decree_deck.get_the_card(card.ID))
       
def mobilize(game, card_ID):
    game.alliance.supporter_deck.add_card(game.alliance.deck.get_the_card(card_ID))
       
def train(game, card_ID):
    if total_common_card_info[card_ID][2] == "dominance":
        game.dominance_discard_deck.add_card(game.alliance.deck.get_the_card(card_ID))
    else:
        game.discard_deck.add_card(game.alliance.deck.get_the_card(card_ID))
    game.alliance.total_officers += 1
    
def organize(game, placename):
    symp_count = game.map.count_on_map(("token", "sympathy"), per_suit=False)
    game.map.places[placename].soldiers["alliance"] -= 1
    game.map.places[placename].tokens += ["sympathy"]
    game.alliance.victory_points += sympathy_VPs[symp_count]
    game.check_victory_points()
    
# Vagabond
def explore_ruin(game, placename):
    for i in range(len(game.map.places[placename].building_slots)):
        if game.map.places[placename].building_slots[i][0] == "ruin":
            game.vagabond.add_item(game.map.places[placename].building_slots[i][1])
            game.map.places[placename].building_slots[i] = ("empty", "No one")
            game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].exhausted = True
            game.vagabond.victory_points += 1
            game.check_victory_points()
            return
    raise ValueError("Try to explore but no ruin")

def aid(game, other_player, choosen_card_id, choosen_item, consequitive_aids):
    other_player.deck.add_card(game.vagabond.deck.get_the_card(choosen_card_id))
    if choosen_item is not None:
        other_player.items.remove(choosen_item)
        game.vagabond.add_item(choosen_item)
    
    if game.vagabond.relations[other_player.name] == "friendly":
        game.vagabond.victory_points += 2
        game.check_victory_points()
        return 0
    
    if game.vagabond.relations[other_player.name] == "hostile":
        raise ValueError("You can't aid a hostile player")
    if game.vagabond.relations[other_player.name] == "indifferent":
        game.vagabond.victory_points += 1
        game.check_victory_points()
        game.vagabond.relations[other_player.name] = "good"
        logging.debug(f"Vagabond relations with {other_player.name} is now good")
        return 0
    if game.vagabond.relations[other_player.name] == "good" and consequitive_aids == 1:
        game.vagabond.victory_points += 2
        game.check_victory_points()
        game.vagabond.relations[other_player.name] = "very good"
        logging.debug(f"Vagabond relations with {other_player.name} is now very good")
        return 0
    if game.vagabond.relations[other_player.name] == "very good" and consequitive_aids == 2:
        game.vagabond.victory_points += 2
        game.check_victory_points()
        game.vagabond.relations[other_player.name] = "friendly"
        logging.debug(f"Vagabond relations with {other_player.name} is now friendly")
        return 0
    return consequitive_aids + 1 # Reset at the end of every vagabond turn


def steal(game, other_player_name):
    for player in [game.marquise, game.alliance, game.eyrie]:
        if player.name == other_player_name:
            player.deck.shuffle_deck()
            game.vagabond.deck.add_card(player.deck.draw_card())
            player.deck.cards.sort(key=lambda x: x.ID)
    game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].exhausted = True
    
    
def complete_quest(game, quest_card_ID, draw_or_VP):
    game.discard_quest_deck.add_card(game.vagabond.quest_deck.get_the_card(quest_card_ID))
    if draw_or_VP == "draw":
        for i in range(2):
            game.vagabond.deck.add_card(game.deck.draw_card())
            if len(game.deck.cards) <=0:
                game.deck = game.discard_deck
                game.deck.shuffle_deck()
                game.discard_deck = Deck(empty=True)
    if draw_or_VP == "VP":
        game.vagabond.victory_points += sum([card.suit == vagabond_quest_card_info[quest_card_ID][-1] for card in game.discard_quest_deck.cards])
        game.check_victory_points()
    item1 = vagabond_quest_card_info[quest_card_ID][1]
    item2 = vagabond_quest_card_info[quest_card_ID][2]
    game.vagabond.exhaust_item(item1)
    game.vagabond.exhaust_item(item2)
    if len(game.quest_deck.cards) > 0:
        game.vagabond.quest_deck.add_card(game.quest_deck.draw_card())
        
def strike(game, placename, opponent, target, card_to_give_if_sympathy):
    game.vagabond.exhaust_item(Item("crossbow"))
    if target == "wood" or target == "keep" or target == "sympathy":
        game.map.places[placename].tokens.remove(target)
        game.vagabond.victory_points += 1
        game.check_victory_points()
        if target == "sympathy" and card_to_give_if_sympathy:
            game.alliance.supporter_deck.add_card(game.vagabond.deck.get_the_card(card_to_give_if_sympathy))
        if target == "sympathy" and not card_to_give_if_sympathy and len(game.vagabond.deck.cards) == 0:
            game.alliance.supporter_deck.add_card(game.deck.draw_card())
            if len(game.deck.cards) <= 0:
                game.deck = copy(game.discard_deck)
                game.deck.shuffle_deck()
                game.discard_deck = Deck(empty=True)
        if target == "sympathy" and not card_to_give_if_sympathy and len(game.vagabond.deck.cards) > 0:
            options = game.alliance.take_card_from_a_player_options(game.vagabond)
            card_id = alliance_choose_card(options)
            game.alliance.supporter_deck.add_card(game.vagabond.deck.get_the_card(card_id))
        if target == "sympathy":
            game.alliance.victory_points -= sympathy_VPs[game.map.count_on_map(("token", "sympathy"))]
    elif target == "soldier":
        game.map.places[placename].soldiers[opponent] -= 1
        game.vagabond.relations[opponent] = "hostile"
    else:
        for i in range(len(game.map.places[placename].building_slots)):
            if game.map.places[placename].building_slots[i][0] == target:
                game.map.places[placename].building_slots[i] = ("empty", "No one")
                game.vagabond.victory_points += 1
                game.check_victory_points()
                if target == 'sawmill' or target == 'workshop' or target == 'recruiter':
                    game.marquise.victory_points -= buildings_list_marquise[target]["VictoryPoints"][game.map.count_on_map(("building", target))+1] # +1 because we already removed the building
                if target == 'base':
                    game.alliance.losing_a_base(place_suit=game.map.places[placename].suit, discard_deck=game.discard_deck)
                break
    game.map.places[placename].update_owner()
    if opponent == 'cat' and target == "soldier":
        return 1 # Wounded cat soldier
    