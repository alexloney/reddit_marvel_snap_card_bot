import json

from . import Card

# Cards built for a special game mode (team-ups, Champions, Doomsday, Augments) are
# real, playable cards but can't be put in a deck, and upstream gives no flag
# for them: they look just like Tokens, with no source and a link to the
# regular card they are based on (e.g. HulkAvengers <-> Hulk). The only reliable
# marker is the CardDefId, which is the base card's id plus the mode's suffix:
#
#   HulkAvengers, CyclopsXMen, DraxGuardiansOfTheGalaxy, GhostThunderbolts,
#   AgonyWebSlingers, MagnetoBrotherhoodOfMutants, HulkChampion,
#   Skill01HulkChampion, CyclopsDoomsday, DoubleOnRevealAugment
#
# For now these are labelled Unreleased. The same check could later give them a
# label of their own (e.g. "Game Mode") once Replies need to tell them apart.
GAME_MODE_SUFFIXES = (
    'Avengers',
    'XMen',
    'GuardiansOfTheGalaxy',
    'Thunderbolts',
    'WebSlingers',
    'BrotherhoodOfMutants',
    'Champion',
    'Doomsday',
    'Augment',
)


def is_game_mode(def_id: str):
    return def_id.endswith(GAME_MODE_SUFFIXES)


def _in_pool_or_series(record, now):
    """
    A card is released once it is in a collection pool, or once any of the
    series it is scheduled for has started.
    """
    if record['source'] != 'None':
        return True
    return any(series['StartDate'] <= now for series in _series(record))


def _scheduled(record, now):
    """
    A card that isn't released yet but is planned to be: it is scheduled for a
    series, or has art variants that are all still to come (e.g. Firestar,
    whose variants are all dated "never").
    """
    if _series(record):
        return True

    variants = [v for v in record.get('variants') or [] if v['id'] != 'base']
    return bool(variants) and \
        all(v['released'] != '1' for v in variants) and \
        all(int(v['ReleaseDate']) > now for v in variants)


def _series(record):
    return json.loads(record.get('SeriesStartDates') or 'null') or []


def card_from_record(key: str, record, now: float):
    """
    Build a Card from a marvelsnap.pro card record.

    Upstream has no released flag and only flags some Tokens, so both are
    inferred. A card in a pool or a started series is a released Card; one
    scheduled for later is Unreleased. Anything else that isn't a game mode
    card is never drawn from a deck, so it is a Token: either a summon upstream
    didn't flag (e.g. Pig) or a Transformed Card (e.g. BannerHulk, the Hulk that
    Bruce Banner turns into).
    """
    def_id = record['CardDefId']
    game_mode = is_game_mode(def_id)

    if record['is_Token'] == '1':
        released, is_token = True, True
    elif game_mode:
        released, is_token = False, False
    elif _in_pool_or_series(record, now):
        released, is_token = True, False
    elif _scheduled(record, now):
        released, is_token = False, False
    else:
        released, is_token = True, True

    card = Card(
        def_id = def_id,
        name = record['name'],
        cost = record['cost'],
        power = record['power'],
        ability = record['description'],
        released = released,
        url = 'https://marvelsnap.pro/cards/' + key,
        is_token = is_token,
        connected_cards = record['connected_cards'])
    card.game_mode = game_mode
    return card
