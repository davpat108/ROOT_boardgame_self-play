def cat_birdsong_wood(map):
    for key in list(map.places.keys()):
        for building_slot in map.places[key].building_slots:
            if building_slot[0] == "sawmill":
                map.places[key].update_pieces(tokens = map.places[key].tokens + ["wood"])