from map import build_regular_forest
from utils import cat_birdsong_wood

def test_birdsong_wood():
    map = build_regular_forest()

    woods = 0
    for key in list(map.places.keys()):
        for token in map.places[key].tokens:
            if token == "wood":
                woods += 1
    assert woods == 0

    cat_birdsong_wood(map)
    for key in list(map.places.keys()):
        for token in map.places[key].tokens:
            if token == "wood":
                woods += 1
    assert woods == 1
