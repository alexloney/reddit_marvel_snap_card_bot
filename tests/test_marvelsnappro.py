import json
import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from database.marvelsnappro import card_from_record, is_game_mode

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


if __name__ == '__main__':
    unittest.main()
