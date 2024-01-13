import copy

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
        if isinstance(result[i], Card) and result[i].is_token:
            replaced = False
            if len(result[i].connected_cards) > 0:
                for j in range(0, len(result[i].connected_cards)):
                    card = database.search_defid(result[i].connected_cards[j])
                    if card is not None and not card.is_token:
                        result[i] = card
                        replaced = True
                        break

            # Unfortuantely, there is an issue with doing a lookup like the
            # above for Nico specifically. She links to her spells BUT her spells
            # do not link back to her. So if we do not find a match from the
            # above, we will do this the "hard way" and search each card
            # looking for a match back to the summon
            if not replaced:
                for card in database.cards:
                    if result[i].def_id in card.connected_cards:
                        result[i] = card
                        replaced = True
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
                    # Actual deepcopy here since we will be modifying the
                    # summoned value of this card and don't want to have that
                    # impact other existing cards.
                    final_cards.append(copy.deepcopy(card))
                    final_cards[-1].summoned = True
    return final_cards

