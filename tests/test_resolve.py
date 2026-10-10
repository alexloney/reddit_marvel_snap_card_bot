import json
import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from database import Database
from database import Card
from database import Location


def card(def_id, name=None, is_token=False, connected=(), released=True):
    return Card(def_id, name or def_id, '1', '1', 'ability', released, 'https://example.test/' + def_id, is_token, json.dumps(list(connected)))


def catalog(*entries):
    database = Database()
    database.cards = [e for e in entries if isinstance(e, Card)]
    database.locations = [e for e in entries if isinstance(e, Location)]
    return database


def ids(match):
    return [match.entry.def_id] + [t.def_id for t in match.tokens]


class TestResolve(unittest.TestCase):
    def test_base_card_lists_its_tokens(self):
        database = catalog(
            card('Thanos', connected=['MindStone', 'SoulStone']),
            card('MindStone', 'Mind Stone', True, ['Thanos']),
            card('SoulStone', 'Soul Stone', True, ['Thanos']))

        matches = database.resolve(['Thanos'])

        self.assertEqual([['Thanos', 'MindStone', 'SoulStone']], [ids(m) for m in matches])

    def test_token_tag_resolves_to_base_card_family(self):
        database = catalog(
            card('Thanos', connected=['MindStone', 'SoulStone']),
            card('MindStone', 'Mind Stone', True, ['Thanos']),
            card('SoulStone', 'Soul Stone', True, ['Thanos']))

        matches = database.resolve(['Soul Stone'])

        self.assertEqual([['Thanos', 'MindStone', 'SoulStone']], [ids(m) for m in matches])

    def test_token_found_only_by_reverse_link(self):
        """
        Nico links to her Spells but the Spells do not link back to her, so a
        Spell Tag must find the Base Card by scanning for who lists it.
        """
        database = catalog(
            card('NicoMinoru', 'Nico Minoru', connected=['Spell01', 'Spell02']),
            card('Spell01', 'Nico Minoru', True, ['Spell02']),
            card('Spell02', 'Nico Minoru', True, ['Spell01']))

        matches = database.resolve(['Nico Minoru'])

        self.assertEqual([['NicoMinoru', 'Spell01', 'Spell02']], [ids(m) for m in matches])

    def test_same_family_from_two_tags_is_one_match(self):
        database = catalog(
            card('Thanos', connected=['MindStone']),
            card('MindStone', 'Mind Stone', True, ['Thanos']))

        matches = database.resolve(['Thanos', 'Mind Stone', 'thanos'])

        self.assertEqual([['Thanos', 'MindStone']], [ids(m) for m in matches])

    def test_unresolvable_token_stands_alone(self):
        database = catalog(card('Orphan', 'Orphan Token', True, []))

        matches = database.resolve(['Orphan Token'])

        self.assertEqual([['Orphan']], [ids(m) for m in matches])

    def test_location_has_no_tokens(self):
        database = catalog(
            Location('AltarOfDeath', 'Altar of Death', 'desc', 'Rare', True, 'https://example.test/altar'))

        matches = database.resolve(['Altar of Death'])

        self.assertEqual([['AltarOfDeath']], [ids(m) for m in matches])
        self.assertIsInstance(matches[0].entry, Location)

    def test_token_shared_by_two_base_cards_appears_under_both(self):
        database = catalog(
            card('Alpha', connected=['Shared']),
            card('Beta', connected=['Shared']),
            card('Shared', 'Shared Token', True, ['Alpha']))

        matches = database.resolve(['Alpha', 'Beta'])

        self.assertEqual([['Alpha', 'Shared'], ['Beta', 'Shared']], [ids(m) for m in matches])

    def test_unmatched_tag_returns_nothing(self):
        database = catalog(card('Wolverine'))

        self.assertEqual([], database.resolve(['Zzzzzzzzzz']))

    def test_card_listing_itself_is_not_its_own_token(self):
        database = catalog(
            card('BlackKnight', 'Black Knight', connected=['EbonyBlade', 'BlackKnight']),
            card('EbonyBlade', 'Ebony Blade', True, ['BlackKnight']))

        matches = database.resolve(['Ebony Blade'])

        self.assertEqual([['BlackKnight', 'EbonyBlade']], [ids(m) for m in matches])

    def test_unmatchable_token_is_not_listed(self):
        database = catalog(
            card('SpiderMan', 'Spider-Man', connected=['UncleBen']),
            card('UncleBen', 'Uncle Ben', True, ['SpiderMan']))
        database.cards[1].matchable = False

        matches = database.resolve(['Spider-Man'])

        self.assertEqual([['SpiderMan']], [ids(m) for m in matches])

    def test_match_renders_tokens_with_prefix(self):
        database = catalog(
            card('Thanos', connected=['MindStone']),
            card('MindStone', 'Mind Stone', True, ['Thanos']))

        text = ''.join(str(m) for m in database.resolve(['Thanos']))

        self.assertTrue(text.startswith('**'))
        self.assertIn('\n\n* **', text)
        self.assertLess(text.index('Thanos'), text.index('Mind Stone'))


if __name__ == '__main__':
    unittest.main()
