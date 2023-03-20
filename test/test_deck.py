from deck import Deck, Card

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
    assert card.suit == "rabbit"
    assert card.craft == "money"
    assert card.needed_crafts == 2
    assert card.what_crafts == "rabbit"

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