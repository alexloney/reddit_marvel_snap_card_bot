import os
import unittest
import sys

sys.path.append('../../snap_bot')
sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from catalog import Catalog, MarvelSnapPro
from catalog import Location


def ids(match):
    return [match.entry.def_id] + [t.def_id for t in match.tokens]


@unittest.skipUnless(os.environ.get('LIVE_TESTS') == '1', 'set LIVE_TESTS=1 to run tests against marvelsnap.pro')
class TestLiveCatalog(unittest.TestCase):
    """
    Live tests against the marvelsnap.pro catalog. They assert on identity and
    structure rather than card text so they keep passing as cards are rebalanced.
    The rules of Card Families themselves are covered offline in test_resolve.
    Run with LIVE_TESTS=1.
    """
    @classmethod
    def setUpClass(self):
        self.catalog = Catalog(MarvelSnapPro())
        self.catalog.refresh()

    def nico_family(self):
        return ['NicoMinoru'] + ['Spell0%dNicoMinoru' % i for i in range(1, 8)]

    def test_exact_search_multicard(self):
        """
        A card with many summons resolves to one Match listing all of them
        """
        matches = self.catalog.resolve(['Nico Minoru'])

        self.assertEqual([self.nico_family()], [ids(m) for m in matches])

    def test_fuzzy_search_multicard(self):
        """
        A search with a character missing still resolves to the same family
        """
        matches = self.catalog.resolve(['ico Minoru'])

        self.assertEqual([self.nico_family()], [ids(m) for m in matches])

    def test_match_nico_duplication(self):
        """
        Nico's Spells all share her name and link to each other, so a partial
        search must not duplicate the family
        """
        matches = self.catalog.resolve(['nico'])

        self.assertEqual([self.nico_family()], [ids(m) for m in matches])

    def test_location_search(self):
        matches = self.catalog.resolve(['Altar of Death'])

        self.assertEqual([['AltarOfDeath']], [ids(m) for m in matches])
        self.assertIsInstance(matches[0].entry, Location)

    def test_short_search_not_found(self):
        """
        A search that is too short must not fuzzy match, e.g. "m" to "Mobius"
        """
        self.assertEqual([], self.catalog.resolve(['m']))

    def test_partial_name_search(self):
        matches = self.catalog.resolve(['Mobius'])

        self.assertEqual([['MobiusMMobius']], [ids(m) for m in matches])

    def test_exact_and_split_match(self):
        """
        An exact match such as [[Death]] wins over a split match such as
        "Altar of Death", which only contains the word
        """
        matches = self.catalog.resolve(['Death'])

        self.assertEqual([['Death']], [ids(m) for m in matches])


if __name__ == '__main__':
    unittest.main()
