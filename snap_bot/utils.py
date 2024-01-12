from database import Card

def remove_duplicate_cards(cards):
    unique_cards = []
    [unique_cards.append(x) for x in cards if x not in unique_cards]
    return unique_cards
