import json
import time

import requests
from wells.utils import retry

from . import Card
from . import Location

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


def location_from_record(key: str, record):
    """
    Build a Location from a marvelsnap.pro location record.
    """
    return Location(
        def_id = record['CardDefId'],
        name = record['name'],
        ability = record['description'],
        rarity = record['rarity'],
        released = record['released'] != '0',
        url = 'https://marvelsnap.pro/cards/' + key)


# Local corrections to marvelsnap.pro's data, keyed by CardDefId. Fields are
# the names of the Card attributes they replace.
PATCHES = {
    'EvolvedAbomination': {'searchable': False, 'name': 'Evolved Abomination', 'url': None},
    'EvolvedCyclops': {'searchable': False, 'name': 'Evolved Cyclops', 'url': None},
    'EvolvedHulk': {'searchable': False, 'name': 'Evolved Hulk', 'url': None},
    'EvolvedMistyKnight': {'searchable': False, 'name': 'Evolved Misty Knight', 'url': None},
    'EvolvedShocker': {'searchable': False, 'name': 'Evolved Shocker', 'url': None},
    'EvolvedTheThing': {'searchable': False, 'name': 'Evolved The Thing', 'url': None},
    'EvolvedWasp': {'searchable': False, 'name': 'Evolved Wasp', 'url': None},
    'EbonyBlade': {'is_token': True},
    'MuramasaShard': {'is_token': True},
    'MysterioIllusion': {'is_token': True},
    'Stormbreaker': {'is_token': True},
    'Pig': {'is_token': True},
    'SnowguardBear': {'name': 'Snowguard Bear'},
    'SnowguardHawk': {'name': 'Snowguard Hawk'},
    'UncleBen': {'searchable': False, 'matchable': False},
    'WidowsBite': {'connected_cards': ['BlackWidow'], 'is_token': True},
}

PATCHABLE_FIELDS = ('searchable', 'matchable', 'name', 'url', 'is_token', 'connected_cards')


def apply_patch(card, patches=PATCHES):
    """
    Apply the Patch for this Card, if it has one. A Patch naming a field that
    cannot be patched is a mistake in the Patch, so it raises.
    """
    for field, value in patches.get(card.def_id, {}).items():
        if field not in PATCHABLE_FIELDS:
            raise ValueError('Patch for %s has unknown field %r' % (card.def_id, field))
        setattr(card, field, value)


CARDS_URL = 'https://static2.marvelsnap.pro/snap/do.php?cmd=getcards'
LOCATIONS_URL = 'https://static2.marvelsnap.pro/snap/do.php?cmd=getlocations'


@retry(times=3, interval=[1, 5, 10])
def download_json(url: str):
    """
    Download a URL and return its decoded JSON. If the download fails for any
    reason this retries up to 3 times before finally considering it a failure.
    """
    with requests.Session() as session:
        response = session.get(url)
        response.raise_for_status()
        return response.json()


class MarvelSnapPro:
    """
    A Catalog source backed by the marvelsnap.pro website. `download` and
    `clock` can be replaced to run without the network or the real time.
    """
    def __init__(self, download=download_json, clock=time.time):
        self.download = download
        self.clock = clock

    def fetch(self):
        """
        Download and build every Card and Location. Nothing is returned unless
        all of it succeeded.
        """
        now = self.clock()

        cards = []
        for key, record in self.download(CARDS_URL).items():
            card = card_from_record(key, record, now)
            apply_patch(card)
            card.format_ability_from_html()
            cards.append(card)

        locations = [location_from_record(key, record)
                     for key, record in self.download(LOCATIONS_URL).items()]

        return cards, locations
