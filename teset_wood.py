from map import build_regular_forest
from utils import cat_birdsong_wood
from actors import Marquise

def test_marquise_get_connected_wood_tokens():
    map = build_regular_forest()
    cat_birdsong_wood(map)

    marquise = Marquise()
    tokens = marquise.get_wood_tokens_to_build(map, map.places['A'])
    
    assert tokens == 1

    piece_setup = [ ('B', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat'), ('empty', 'No one')], 'tokens' : []}), # Cats
                    ('C', {'soldiers' : {'cat': 1, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'),('empty', 'No one')], 'tokens' : []}), # Birds
                    ('D', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []}), # Birds
                    ('E', {'soldiers' : {'cat': 2, 'bird' : 2, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one')], 'tokens' : []})] # Birds
    
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
    for key in sorted(list(map.places.keys())):
        print(map.places[key].name, map.places[key].owner)


    tokens = marquise.get_wood_tokens_to_build(map, map.places['K'])
    assert tokens == 0
    



test_marquise_get_connected_wood_tokens()