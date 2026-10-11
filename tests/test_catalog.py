import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from catalog import Catalog
from catalog import Card
from catalog import Location
from support import StaticSource, build_catalog


def card(def_id, name=None):
    return Card(def_id, name or def_id, '1', '1', 'ability', True, 'https://example.test/' + def_id, False, '[]')


def found(catalog, query):
    return [m.entry.def_id for m in catalog.resolve([query])]


class TestMatching(unittest.TestCase):
    def test_exact_match(self):
        catalog = build_catalog(card('Wolverine'), card('Hulk'))

        self.assertEqual(['Wolverine'], found(catalog, 'wolverine'))

    def test_fuzzy_match_within_distance(self):
        catalog = build_catalog(card('Wolverine'))

        self.assertEqual(['Wolverine'], found(catalog, 'olerine'))

    def test_fuzzy_match_beyond_distance_is_rejected(self):
        catalog = build_catalog(card('Wolverine'))

        self.assertEqual([], found(catalog, 'lerine'))

    def test_distance_is_configurable(self):
        catalog = build_catalog(card('Wolverine'), max_fuzzy_distance=3)

        self.assertEqual(['Wolverine'], found(catalog, 'lerine'))

    def test_short_query_must_match_exactly(self):
        catalog = build_catalog(card('MobiusMMobius', 'Mobius M. Mobius'))

        self.assertEqual([], found(catalog, 'm'))

    def test_short_query_matching_a_whole_word_is_allowed(self):
        catalog = build_catalog(card('AntMan', 'Ant-Man'))

        self.assertEqual(['AntMan'], found(catalog, 'Man'))

    def test_partial_name_matches_a_word(self):
        catalog = build_catalog(card('MobiusMMobius', 'Mobius M. Mobius'))

        self.assertEqual(['MobiusMMobius'], found(catalog, 'Mobius'))

    def test_exact_whole_name_beats_word_match(self):
        catalog = build_catalog(
            card('Death'),
            Location('AltarOfDeath', 'Altar of Death', 'desc', 'Rare', True, 'https://example.test/altar'))

        self.assertEqual(['Death'], found(catalog, 'Death'))

    def test_word_match_returns_every_tied_entry(self):
        catalog = build_catalog(card('AntMan', 'Ant-Man'), card('IronMan', 'Iron Man'))

        self.assertEqual(['AntMan', 'IronMan'], found(catalog, 'Man'))

    def test_not_searchable_entry_is_skipped(self):
        hidden = card('EvolvedHulk', 'Evolved Hulk')
        hidden.searchable = False
        catalog = build_catalog(hidden)

        self.assertEqual([], found(catalog, 'Evolved Hulk'))

    def test_empty_catalog_matches_nothing(self):
        self.assertEqual([], found(build_catalog(), 'Hulk'))


class TestRefresh(unittest.TestCase):
    def test_refresh_replaces_entries(self):
        source = StaticSource(card('Wolverine'))
        catalog = Catalog(source)
        catalog.refresh()

        source.set(card('Hulk'))
        catalog.refresh()

        self.assertEqual([], found(catalog, 'Wolverine'))
        self.assertEqual(['Hulk'], found(catalog, 'Hulk'))

    def test_failed_refresh_keeps_existing_entries(self):
        source = StaticSource(card('Wolverine'))
        catalog = Catalog(source)
        catalog.refresh()

        source.set(card('Hulk'))
        source.fail = True
        with self.assertRaises(RuntimeError):
            catalog.refresh()

        self.assertEqual(['Wolverine'], found(catalog, 'Wolverine'))
        self.assertEqual([], found(catalog, 'Hulk'))

    def test_catalog_is_empty_before_first_refresh(self):
        self.assertEqual([], found(Catalog(StaticSource(card('Wolverine'))), 'Wolverine'))


if __name__ == '__main__':
    unittest.main()
