import json
import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from database import Database
from database import Card
from database import Location


def card(def_id, name=None, is_token=False, connected=(), released=True, game_mode=False):
    c = Card(def_id, name or def_id, '1', '1', 'ability', released, 'https://example.test/' + def_id, is_token, json.dumps(list(connected)))
    c.game_mode = game_mode
    return c


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

    def test_transformed_card_sharing_a_name_resolves_to_its_base_card(self):
        """
        Bruce Banner turns into a Hulk that shares its name with the real Hulk,
        so [[Hulk]] shows Bruce Banner's family and then Hulk on its own.
        """
        database = catalog(
            card('BannerHulk', 'Hulk', True, ['BruceBanner', 'BannerHulk']),
            card('BruceBanner', 'Bruce Banner', connected=['BannerHulk', 'BruceBanner']),
            card('Hulk', 'Hulk'))

        matches = database.resolve(['Hulk'])

        self.assertEqual([['BruceBanner', 'BannerHulk'], ['Hulk']], [ids(m) for m in matches])

    def test_game_mode_card_is_not_in_the_family_it_links_to(self):
        database = catalog(
            card('Hulk', 'Hulk', connected=['HulkAvengers']),
            card('HulkAvengers', 'Hulk - Avengers', connected=['Hulk'], released=False, game_mode=True))

        self.assertEqual([['Hulk']], [ids(m) for m in database.resolve(['Hulk'])])
        self.assertEqual([['HulkAvengers']], [ids(m) for m in database.resolve(['Hulk - Avengers'])])

    def test_token_of_game_mode_card_does_not_resolve_to_it(self):
        """
        A Token linked to both a game mode Card and a regular Card belongs to
        the regular one, e.g. Mjolnir with Thor Champion and Thor.
        """
        database = catalog(
            card('ThorChampion', 'Thor Champion', connected=['Mjolnir'], released=False, game_mode=True),
            card('Thor', 'Thor', connected=['Mjolnir']),
            card('Mjolnir', 'Mjolnir', True, ['ThorChampion', 'Thor']))

        self.assertEqual([['Thor', 'Mjolnir']], [ids(m) for m in database.resolve(['Mjolnir'])])

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
