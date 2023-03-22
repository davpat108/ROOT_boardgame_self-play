from map import build_regular_forest

def test_clearing_owner():
    map = build_regular_forest()
    
    soldiers = {
        "cat" : 1,
        "bird" : 0,
        "alliance" : 1
    }
    map.places['H'].update_pieces([('empty', 'No one'), ('empty', 'No one'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    map.places['H'].update_owner()

    assert map.places['H'].owner == 'bird'

    soldiers = {
			"cat" : 2,
			"bird" : 0,
			"alliance" : 2
		}
    map.places['H'].update_pieces([('empty', 'No one'), ('empty', 'No one'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    map.places['H'].update_owner()
    assert map.places['H'].owner == 'No one'

    map.places['H'].update_pieces([('empty', 'No one'), ('Workshop', 'cat'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    map.places['H'].update_owner()
    assert map.places['H'].owner == 'cat'


def test_default_map():
    map = build_regular_forest()
    map.check_vagabond()

    cat_stuff = 0
    for key in sorted(list(map.places.keys())):
        cat_stuff+=map.places[key].soldiers['cat']
        for building in map.places[key].building_slots:
            if building[1] == "cat":
                cat_stuff+=1
        for token in map.places[key].tokens:
            if token[0] == "keep":
                cat_stuff+=1

    assert cat_stuff == 15