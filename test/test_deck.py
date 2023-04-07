from deck import Deck, Card, QuestCard, QuestDeck
from item import Item

def test_deck_init():
    deck = Deck()
    assert len(deck.cards) == 54

    deck = Deck(empty=True)
    assert len(deck.cards) == 0

def test_draw_card():
    deck = Deck()
    card_IDs = []

    while True:
        card = deck.draw_card()
        if card == "Deck Empty":
            break
        card_IDs.append(card.ID)
        # Check if no duplicates
        assert len(card_IDs) == len(set(card_IDs))

def test_get_the_card():
    deck = Deck()

    card = deck.get_the_card(ID=3)
    assert len(deck.cards) == 53
    assert card.ID == 3
    assert card.card_suit == "rabbit"
    assert card.craft == Item("money")
    assert card.craft_cost == 2
    assert card.craft_suit == "rabbit"

    card = deck.get_the_card(ID=88)
    assert len(deck.cards) == 53
    assert card == "Card not in the deck"

    while True:
        card = deck.draw_card()
        if card == "Deck Empty":
            break
        assert card.ID != 3

def test_add_card():
    deck = Deck(empty=True)

    discarded_card = Card(*[53, "bird", "royal_claim", 4, "anything"])
    deck.add_card(discarded_card)
    assert len(deck.cards) == 1

    card = deck.draw_card()
    assert card == discarded_card

def test_questdeck_init():
    deck = QuestDeck()
    assert len(deck.cards) == 15

    deck = QuestDeck(empty=True)
    assert len(deck.cards) == 0

def test_draw_questcard():
    deck = QuestDeck()
    card_IDs = []

    while True:
        card = deck.draw_card()
        if card == "Deck Empty":
            break
        card_IDs.append(card.ID)
        # Check if no duplicates
        assert len(card_IDs) == len(set(card_IDs))


def test_add_questcard():
    deck = QuestDeck(empty=True)

    discarded_card = QuestCard(*[14, "sword", "sword", "mouse"])
    deck.add_card(discarded_card)
    assert len(deck.cards) == 1

    card = deck.draw_card()
    assert card == discarded_card