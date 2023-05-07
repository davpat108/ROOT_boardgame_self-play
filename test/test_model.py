import sys
sys.path.append('.')
from game import Game
from model import init_models_with_random_weights

def test_encoding_and_linear_model():
    game = Game(debug=True)
    # 0 - 3 CAT Birdsong daylight craft, daylight rest, evening
    # 4 - 7 BIRD Birdsong daylight craft, daylight rest evening
    # 8 - 11 ALLIANCE Birdsong revolt Birsond symp, daylight evening
    # 12 - 14 VAGABOND Birdsong daylight evening

    player_id = 0
    encoding = game.encode(gamestate=1, player_id=player_id)

    marquise_output_features = 240 #0
    eyrie_output_features = 239 #1
    alliance_output_features = 237 #2
    vagabond_output_features = 257 #3
    game_encoding_size = 910

    model = init_models_with_random_weights(marquise_output_features, eyrie_output_features, alliance_output_features, vagabond_output_features, game_encoding_size)
    output = model(encoding, player_id)
    print(output)



test_encoding_and_linear_model()