def discard_down_to_five_supporters_options(actor, map):
    if map.count_on_map(("building", "base")) == 0:
        if len(actor.supporter_deck.cards) <= 5:
            return
        card_IDs = []
        for card in actor.supporter_deck.cards:
            card_IDs.append(card.ID)
        return card_IDs
    return

def get_revolt_options(actor, map):
    revolt_options = []
    # Iterate through the map to find suitable clearings for a revolt
    for key in sorted(list(map.places.keys())):
        place = map.places[key]
        if "sympathy" in place.tokens and not "keep" in place.tokens:
            suit = place.suit
            has_base = actor.base_search(map, place.suit)
            if not has_base:
                soldiers_to_gain = map.count_on_map(("token", "sympathy"), per_suit=True)[suit]
                matching_cards = [card for card in actor.supporter_deck.cards if card.card_suit == suit or card.card_suit == "bird"]
                card_combinations = actor.get_card_combinations(matching_cards, 2)
                for combination in card_combinations:
                    revolt_options.append((place, combination[0].ID, combination[1].ID, soldiers_to_gain))
    return revolt_options

def get_card_combinations(actor, cards, num_cards):
    if num_cards == 0:
        return [[]]
    if not cards:
        return []
    card = cards[0]
    remaining_cards = cards[1:]
    with_card = [[card] + combination for combination in actor.get_card_combinations(remaining_cards, num_cards - 1)]
    without_card = actor.get_card_combinations(remaining_cards, num_cards)
    
    return with_card + without_card

def get_spread_sympathy_options(actor, map):
    spread_sympathy_options = []
    sympathies_on_map = map.count_on_map(("token", "sympathy"))
    if sympathies_on_map > 9:
        return spread_sympathy_options
    
    if sympathies_on_map == 0:
        cost = 0
        for key in sorted(list(map.places.keys())):
            place = map.places[key]
            if "keep" not in place.tokens and place.forest == False:
                matching_cards = [card for card in actor.supporter_deck.cards if card.card_suit == place.suit or card.card_suit == "bird"]
                other_faction_soldiers = sum(soldiers for faction, soldiers in place.soldiers.items() if faction != "alliance")
                if other_faction_soldiers >= 3:
                    cost += 1
                card_combinations = actor.get_card_combinations(matching_cards, cost)
                for combination in card_combinations:
                    card_ids = [card.ID for card in combination]
                    spread_sympathy_options.append((place.name, card_ids))
    else:
        sympathy_clearings = [place for place in map.places.values() if "sympathy" in place.tokens]
        adjacent_clearings = set()
        for clearing in sympathy_clearings:
            for neighbor in clearing.neighbors:
                adjacent_clearings.update(neighbor[0])
        for clearing_name in adjacent_clearings:
            target_clearing = map.places[clearing_name]
            if "sympathy" not in target_clearing.tokens and "keep" not in target_clearing.tokens and target_clearing.forest == False:
                clearing_suit = target_clearing.suit
                matching_cards = [card for card in actor.supporter_deck.cards if card.card_suit == clearing_suit or card.card_suit == "bird"]
                if sympathies_on_map <= 2:
                    cost = 1
                elif sympathies_on_map <= 5:
                    cost = 2
                else:
                    cost = 3
                other_faction_soldiers = sum(soldiers for faction, soldiers in target_clearing.soldiers.items() if faction != "alliance")
                if other_faction_soldiers >= 3:
                    cost += 1
                card_combinations = actor.get_card_combinations(matching_cards, cost)
                for combination in card_combinations:
                    card_ids = [card.ID for card in combination]
                    spread_sympathy_options.append((target_clearing.name, card_ids))
    return spread_sympathy_options

def get_options_craft(actor, map):
    craft_options = []
    for card in actor.deck.cards:
        if card.craft in Immediate_non_item_effects or card.craft in map.craftables or card.craft in persistent_effects:
            if card.craft_suit == "ambush":
                pass
            elif card.craft_suit == "anything":
                if sum(actor.craft_activations.values()) >= card.craft_cost:
                    craft_options.append(CraftDTO(card))
            elif card.craft_suit == "all":
                if actor.craft_activations["fox"] >= 1 and actor.craft_activations["rabbit"] >= 1 and actor.craft_activations["mouse"] >= 1:
                    craft_options.append(CraftDTO(card))
            elif card.craft_suit == "dominance" and actor.victory_points >= 10 and actor.win_condition == "points":
                craft_options.append(CraftDTO(card))
            elif card.craft_suit != "dominance" and card.craft_suit != "all" and card.craft_suit != "anything" and actor.craft_activations[card.craft_suit] >= card.craft_cost:
               craft_options.append(CraftDTO(card))
    return craft_options

def get_mobilize_options(actor, map):
    return [card.ID for card in actor.deck.cards]

def get_train_options(actor, map):
    base_suits = set()
    train_options = []
    if sum([place.soldiers["alliance"] for place in map.places.values()]) + actor.total_officers >= 10:
        return train_options
    for place in map.places.values():
        if ("base", "alliance") in place.building_slots:
            base_suits.add(place.suit)
    for card in actor.deck.cards:
        if card.card_suit in base_suits or card.card_suit == "bird":
            train_options.append((card.ID, "train"))
    return list(set(train_options))

def get_battles(actor, map):
    battle_options = []
    for key in sorted(list(map.places.keys())):
        place = map.places[key]
        if place.soldiers['alliance'] > 0:
            if place.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in place.building_slots]or 'keep' in place.tokens or 'wood' in place.tokens:
                battle_options.append(Battle_DTO(place.name, "cat"))
            if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                battle_options.append(Battle_DTO(place.name, "bird"))
            if place.vagabond_is_here:
                battle_options.append(Battle_DTO(place.name, "vagabond"))
            if actor.armorers:
                if place.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in place.building_slots]or 'keep' in place.tokens or 'wood' in place.tokens:
                    battle_options.append(Battle_DTO(place.name, "cat", armorer_usage=True))
                if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                    battle_options.append(Battle_DTO(place.name, "bird", armorer_usage=True))
                if place.vagabond_is_here:
                    battle_options.append(Battle_DTO(place.name, "vagabond", armorer_usage=True))
            if actor.brutal_tactics:
                if place.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in place.building_slots]or 'keep' in place.tokens or 'wood' in place.tokens:
                    battle_options.append(Battle_DTO(place.name, "cat", brutal_tactics_usage=True))
                if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                    battle_options.append(Battle_DTO(place.name, "bird", brutal_tactics_usage=True))
                if place.vagabond_is_here:
                    battle_options.append(Battle_DTO(place.name, "vagabond", brutal_tactics_usage=True))
            if actor.armorers and actor.brutal_tactics:
                if place.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in place.building_slots]or 'keep' in place.tokens or 'wood' in place.tokens:
                    battle_options.append(Battle_DTO(place.name, "cat", armorer_usage=True, brutal_tactics_usage=True))
                if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                    battle_options.append(Battle_DTO(place.name, "bird", armorer_usage=True, brutal_tactics_usage=True))
                if place.vagabond_is_here:
                    battle_options.append(Battle_DTO(place.name, "vagabond", armorer_usage=True, brutal_tactics_usage=True))
    return battle_options

def get_moves(actor, map):
    "Returns a list of MoveDTO objects"
    moves = []
    for key in sorted(list(map.places.keys())): # sort places by key
        place = map.places[key]
        for i in range(place.soldiers['alliance']):
            for neighbor in place.neighbors:
                if place.owner == 'alliance' or map.places[neighbor[0]].owner == 'alliance':
                    if place.forest == False and map.places[neighbor[0]].forest == False:
                        moves.append(MoveDTO(place.name, map.places[neighbor[0]].name, how_many=i + 1, who='alliance'))
    return moves

def get_recruits(actor, map):
    recruit_options = []
    if sum([place.soldiers["alliance"] for place in map.places.values()]) + actor.total_officers >= 10:
        return []
    for place in map.places.values():
        if True in [slot[0]=='base' for slot in place.building_slots]:
            recruit_options.append((place.name, "recruit"))
    return recruit_options

def get_organize_options(actor, map):
    organize_options = []
    sympathies_on_map = map.count_on_map(("token", "sympathy"))
    if sympathies_on_map > 9:
        return organize_options
    
    for place in map.places.values():
        if place.soldiers['alliance']>0 and not 'sympathy' in place.tokens:
            organize_options.append((place.name, "organize"))
    return organize_options
