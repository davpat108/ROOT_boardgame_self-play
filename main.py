
from deck import Deck, QuestDeck
from map import build_regular_forest
from actors import Marquise, Eerie, Alliance, Vagabond
from utils import cat_birdsong_wood

if __name__ == "__main__":
    map = build_regular_forest()
    common_deck = Deck()
    discard_deck = Deck(empty=True)

    quest_deck = QuestDeck()
    discard_quest_deck = QuestDeck(empty=True)

    margquise = Marquise()
    eerie = Eerie()
    alliance = Alliance()
    vagabond = Vagabond(role = "Thief")

    # Deal initial 3 cards, + supporter cards for alliance
    for i in range(3):
        margquise.deck.add_card(common_deck.draw_card())
        eerie.deck.add_card(common_deck.draw_card())
        alliance.deck.add_card(common_deck.draw_card())
        alliance.supporter_deck.add_card(common_deck.draw_card())
        vagabond.deck.add_card(common_deck.draw_card())
        vagabond.quest_deck.add_card(quest_deck.draw_card())


    winner = "No one"
    while winner == "No one":
        # Marquise
        cat_birdsong_wood(map)
        