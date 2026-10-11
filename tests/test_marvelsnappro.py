import json
import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from catalog import Card, MarvelSnapPro
from catalog.marvelsnappro import card_from_record, is_game_mode, location_from_record, apply_patch, CARDS_URL, LOCATIONS_URL

NOW = 1790000000
PAST = NOW - 86400
FUTURE = NOW + 86400
NEVER = 2147483647


def record(def_id, source='None', is_token='0', series=None, variants=(), connected=()):
    """
    A marvelsnap.pro card record with only the fields the bot reads
    """
    return {
        'CardDefId': def_id,
        'name': def_id,
        'cost': '1',
        'power': '1',
        'description': 'ability',
        'source': source,
        'is_Token': is_token,
        'connected_cards': json.dumps(list(connected)),
        'SeriesStartDates': json.dumps([{'Data': 'Series5', 'StartDate': d} for d in series]) if series else 'null',
        'variants': [{'id': 'base', 'released': '1', 'ReleaseDate': '0'}] + \
            [{'id': '%02d' % i, 'released': r, 'ReleaseDate': str(d)} for i, (r, d) in enumerate(variants, 1)],
    }


def card(rec):
    return card_from_record(rec['CardDefId'].lower(), rec, NOW)


class TestCardFromRecord(unittest.TestCase):
    def test_card_in_a_pool_is_released(self):
        c = card(record('Hulk', source='Starter Card'))

        self.assertTrue(c.released)
        self.assertFalse(c.is_token)
        self.assertFalse(c.game_mode)
        self.assertEqual('https://marvelsnap.pro/cards/hulk', c.url)

    def test_card_whose_series_has_started_is_released(self):
        """
        e.g. Entropic Havok: out in an event before reaching a pool
        """
        c = card(record('EntropicHavok', series=[PAST, FUTURE]))

        self.assertTrue(c.released)
        self.assertFalse(c.is_token)

    def test_card_scheduled_for_a_future_series_is_unreleased(self):
        c = card(record('ArthurPendragon', series=[FUTURE], variants=[('0', FUTURE)]))

        self.assertFalse(c.released)
        self.assertFalse(c.is_token)

    def test_card_with_only_unreleased_art_is_unreleased(self):
        """
        e.g. Firestar: no series, and every variant is dated "never"
        """
        c = card(record('Firestar', variants=[('0', NEVER), ('0', NEVER)]))

        self.assertFalse(c.released)
        self.assertFalse(c.is_token)

    def test_unflagged_card_with_no_release_is_a_token(self):
        """
        e.g. BannerHulk, the Hulk Bruce Banner turns into, which upstream
        doesn't flag as a Token. Its released art doesn't make it Unreleased.
        """
        c = card(record('BannerHulk', variants=[('0', PAST)], connected=['BruceBanner']))

        self.assertTrue(c.released)
        self.assertTrue(c.is_token)

    def test_flagged_token_is_a_released_token(self):
        c = card(record('MindStone', is_token='1'))

        self.assertTrue(c.released)
        self.assertTrue(c.is_token)

    def test_game_mode_card_is_unreleased_and_not_a_token(self):
        c = card(record('HulkAvengers', connected=['Hulk']))

        self.assertFalse(c.released)
        self.assertFalse(c.is_token)
        self.assertTrue(c.game_mode)

    def test_game_mode_suffixes(self):
        for def_id in ['HulkAvengers', 'CyclopsXMen', 'DraxGuardiansOfTheGalaxy',
                       'GhostThunderbolts', 'AgonyWebSlingers', 'MagnetoBrotherhoodOfMutants',
                       'HulkChampion', 'Skill01HulkChampion', 'CyclopsDoomsday', 'DoubleOnRevealAugment']:
            self.assertTrue(is_game_mode(def_id), def_id)

        for def_id in ['Hulk', 'BannerHulk', 'ScarletSpiderClone', 'KhonshuWaxing', 'GambitAndShangChi']:
            self.assertFalse(is_game_mode(def_id), def_id)


class TestLocationFromRecord(unittest.TestCase):
    def location(self, released):
        return location_from_record('altarofdeath', {
            'CardDefId': 'AltarOfDeath',
            'name': 'Altar of Death',
            'description': 'Destroy it.',
            'rarity': 'Rare',
            'released': released})

    def test_location_fields(self):
        location = self.location('1')

        self.assertEqual('AltarOfDeath', location.def_id)
        self.assertEqual('Altar of Death', location.name)
        self.assertEqual('Rare', location.rarity)
        self.assertEqual('https://marvelsnap.pro/cards/altarofdeath', location.url)
        self.assertTrue(location.released)

    def test_unreleased_location(self):
        self.assertFalse(self.location('0').released)


class TestPatches(unittest.TestCase):
    def plain(self, def_id):
        return Card(def_id, def_id, '1', '1', 'ability', True, 'https://marvelsnap.pro/cards/x', False, '[]')

    def test_patch_replaces_named_fields(self):
        c = self.plain('EvolvedHulk')

        apply_patch(c)

        self.assertEqual('Evolved Hulk', c.name)
        self.assertIsNone(c.url)
        self.assertFalse(c.searchable)

    def test_patch_sets_connected_cards_as_a_list(self):
        c = self.plain('WidowsBite')

        apply_patch(c)

        self.assertEqual(['BlackWidow'], c.connected_cards)
        self.assertTrue(c.is_token)

    def test_card_without_a_patch_is_unchanged(self):
        c = self.plain('Hulk')

        apply_patch(c)

        self.assertEqual('Hulk', c.name)
        self.assertTrue(c.searchable)

    def test_unknown_patch_field_raises(self):
        with self.assertRaises(ValueError):
            apply_patch(self.plain('Hulk'), {'Hulk': {'is_Token': True}})


class TestFetch(unittest.TestCase):
    def source(self, cards, locations):
        def download(url):
            return {CARDS_URL: cards, LOCATIONS_URL: locations}[url]
        return MarvelSnapPro(download=download, clock=lambda: NOW)

    def test_fetch_maps_patches_and_formats_cards_and_locations(self):
        cards = {
            'hulk': record('Hulk', source='Starter Card'),
            'pig': record('Pig', is_token='1', connected=['SpiderHam']),
        }
        cards['hulk']['description'] = '<b>On Reveal:</b> Smash.'
        locations = {'altarofdeath': {
            'CardDefId': 'AltarOfDeath', 'name': 'Altar of Death',
            'description': 'Destroy it.', 'rarity': 'Rare', 'released': '1'}}

        fetched_cards, fetched_locations = self.source(cards, locations).fetch()

        self.assertEqual(['Hulk', 'Pig'], [c.def_id for c in fetched_cards])
        self.assertEqual('**On Reveal:** Smash.', fetched_cards[0].formatted_ability)
        self.assertTrue(fetched_cards[1].is_token)
        self.assertEqual(['AltarOfDeath'], [loc.def_id for loc in fetched_locations])

    def test_fetch_applies_patches(self):
        cards = {'evolvedhulk': record('EvolvedHulk', is_token='1')}

        fetched_cards, _ = self.source(cards, {}).fetch()

        self.assertEqual('Evolved Hulk', fetched_cards[0].name)
        self.assertFalse(fetched_cards[0].searchable)

    def test_fetch_uses_the_injected_clock(self):
        cards = {'arthur': record('Arthur', series=[NOW + 100])}

        fetched_cards, _ = self.source(cards, {}).fetch()

        self.assertFalse(fetched_cards[0].released)

    def test_fetch_fails_as_a_whole_if_locations_fail(self):
        def download(url):
            if url == LOCATIONS_URL:
                raise RuntimeError('down')
            return {'hulk': record('Hulk', source='Starter Card')}

        with self.assertRaises(RuntimeError):
            MarvelSnapPro(download=download, clock=lambda: NOW).fetch()


if __name__ == '__main__':
    unittest.main()
