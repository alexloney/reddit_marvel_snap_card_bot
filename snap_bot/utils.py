from database import Card

def remove_duplicate_cards(cards):
    """
    Search through the list of cards and remove all duplicate values
    """
    unique_cards = []
    [unique_cards.append(x) for x in cards if x not in unique_cards]
    return unique_cards

def resolve_tokens_to_base(database, cards):
    """
    Search through the list of cards and resolve all Tokens to their Base card
    based on the connected cards field
    """
    result = [x for x in cards]
    for i in range(0, len(result)):
        if isinstance(result[i], Card) and result[i].is_token and len(result[i].connected_cards) > 0:
            for j in range(0, len(result[i].connected_cards)):
                card = database.search_defid(result[i].connected_cards[j])
                if card is not None and not card.is_token:
                    result[i] = card
                    break
    return result

def insert_tokens_from_cards(database, cards):
    """
    Search through the list of cards and find all cards that have tokens, then
    insert their tokens into the array
    """
    final_cards = []
    for i in range(0, len(cards)):
        final_cards.append(cards[i])
        if isinstance(cards[i], Card) and not cards[i].is_token and len(cards[i].connected_cards) > 0:
            for j in range(0, len(cards[i].connected_cards)):
                card = database.search_defid(cards[i].connected_cards[j])
                if card is not None:
                    final_cards.append(card)
    return final_cards
