
#CAT EXCLUSIVE
def get_field_hospital_options(actor, map, placename=None,suit=None):
    if map.count_on_map(("token", "keep")) != 1:
        return [False]
    options = [False]
    if placename:
        for card in actor.deck.cards:
            if card.card_suit == map.places[placename].suit or card.card_suit == "bird":
                options.append(card.ID)
        return options
    if suit:
        for card in actor.deck.cards:
            if card.card_suit == suit or card.card_suit == "bird":
                options.append(card.ID)
        return options


def get_options_craft(actor, map):
    craft_options = []
    for card in actor.deck.cards:
        if card.craft in Immediate_non_item_effects or card.craft in map.craftables or card.craft in persistent_effects or card.craft == "dominance":
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
    
def get_battles(actor, map):
    battle_options = []
    for key in sorted(list(map.places.keys())):
        place = map.places[key]
        if place.soldiers['cat'] > 0:
            if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                battle_options.append(Battle_DTO(place.name, "bird"))
            if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                battle_options.append(Battle_DTO(place.name, "alliance"))
            if place.vagabond_is_here:
                battle_options.append(Battle_DTO(place.name, "vagabond"))
            if actor.armorers:
                if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                    battle_options.append(Battle_DTO(place.name, "bird", armorer_usage=True))
                if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                    battle_options.append(Battle_DTO(place.name, "alliance", armorer_usage=True))
                if place.vagabond_is_here:
                    battle_options.append(Battle_DTO(place.name, "vagabond", armorer_usage=True))
            if actor.brutal_tactics:
                if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                    battle_options.append(Battle_DTO(place.name, "bird", brutal_tactics_usage=True))
                if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                    battle_options.append(Battle_DTO(place.name, "alliance", brutal_tactics_usage=True))
                if place.vagabond_is_here:
                    battle_options.append(Battle_DTO(place.name, "vagabond", brutal_tactics_usage=True))
            if actor.brutal_tactics and actor.armorers:
                if place.soldiers['bird'] > 0 or True in [slot[0]=='roost' for slot in place.building_slots]:
                    battle_options.append(Battle_DTO(place.name, "bird", brutal_tactics_usage=True, armorer_usage=True))
                if place.soldiers['alliance'] > 0 or True in [slot[0]=='base' for slot in place.building_slots] or "sympathy" in place.tokens:
                    battle_options.append(Battle_DTO(place.name, "alliance", brutal_tactics_usage=True, armorer_usage=True))
                if place.vagabond_is_here:
                    battle_options.append(Battle_DTO(place.name, "vagabond", brutal_tactics_usage=True, armorer_usage=True))
    return battle_options
    
def get_moves(actor, map):
    "Returns a list of MoveDTO objects"
    moves = []
    for key in sorted(list(map.places.keys())): # sort places by key
        place = map.places[key]
        for i in range(place.soldiers['cat']):
            for neighbor in place.neighbors:
                if place.owner == 'cat' or map.places[neighbor[0]].owner == 'cat':
                    if place.forest == False and map.places[neighbor[0]].forest == False:
                        moves.append(MoveDTO(place.name, map.places[neighbor[0]].name, who='cat', how_many=i + 1))
    return moves    
    
def get_can_recruit(actor, map):
    if sum([place.soldiers["cat"] for place in map.places.values()]) >= 25:
        return (False, 'recruit')
    return [(map.count_on_map(("building", "recruiter")) > 0, 'recruit')]
    
def get_wood_tokens_to_build(actor, map, place):
    """
    Finds all 'wood' tokens that are connected to a Place object on the map through multiple cat-owned Places.
    """
    if place.owner != 'cat':
        return 0
    
    connected_places = map.get_connected_places(place, 'cat')
    
    # Find all wood tokens on the connected places
    woods = 0
    for p in connected_places:
        for token in p.tokens:
            if token == 'wood':
                woods += 1
    return woods
    
def get_build_options(actor, map):
    """
    Returns a dict of building options for the Marquise.
    """
    bulding_costs = [0, 1, 2, 3, 3, 4]
    building_options = []
    
    for building in ["sawmill", "workshop", "recruiter"]:
        count = map.count_on_map(("building", building))
        if count >= 6:
            continue
        cost = bulding_costs[count]
        for key in sorted(list(map.places.keys())):
            place = map.places[key]
            woods = actor.get_wood_tokens_to_build(map, place)
            if place.owner == 'cat' and True in [slot[0] == "empty" for slot in place.building_slots]:
                if not place.forest:
                    if woods >= cost:
                        building_options.append((place.name, building, cost))

    return building_options
    
def get_overwork(actor, map):
    """
    Returns a list of OverworkDTO objects.
    """
    overwork_clearings = []
    for key in sorted(list(map.places.keys())):
        place = map.places[key]
        for card in actor.deck.cards:
            if place.owner == 'cat':
                for slot in place.building_slots:
                    if slot[0] == 'sawmill' and (place.suit == card.card_suit or card.card_suit == 'bird'):
                        overwork_clearings.append(OverworkDTO(place.name, card.ID))
                        
    return overwork_clearings

def get_use_bird_card_to_gain_moves(actor):
    options = [False]
    for card in actor.deck.cards:
        if card.card_suit == 'bird':
            options.append(card.ID)
    return options
