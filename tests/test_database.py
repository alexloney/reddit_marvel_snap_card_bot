import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from database import Database
from database import Card
from database import Location
import utils

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.database = Database()
        self.database.update_card_database_marvelsnappro()
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_exact_search(self):
        result = self.database.search('wolverine')
        expected_results = [Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]')]
 
        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])
    
    def test_fuzzy_search_1(self):
        """
        Test a fuzzy search with 1 character different. Given the default operation
        of the Database class, this should be acceptable
        """
        result = self.database.search('wolerine')
        expected_results = [Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]')]
 
        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])

    def test_fuzzy_search_2(self):
        """
        Test a fuzzy search with 2 characters different. Given the default operation
        of the Database class, this should be acceptable
        """
        result = self.database.search('olerine')
        expected_results = [Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]')]
 
        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])

    def test_fuzzy_search_3(self):
        """
        Test a fuzzy search with 3 characters different. Given the default operation
        of the Database class, this should fail
        """
        result = self.database.search('lerine')
        expected_results = [Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]')]

        self.assertNotEqual(len(expected_results), len(result))

    def test_exact_search_multicard(self):
        """
        Test that a card returning multiple summons matches an expected search
        """
        result = self.database.search('Nico Minoru')
        expected_results = [
            Card('NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, cast a spell. <i>(The spell changes each turn.)</i>', True, 'https://marvelsnap.pro/cards/nicominoru', False, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell02NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, it becomes a Demon.', True, 'https://marvelsnap.pro/cards/spell01nicominoru', True, '["Demon", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell03NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, destroy it to draw two cards.', True, 'https://marvelsnap.pro/cards/spell02nicominoru', True, '["Spell01NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell04NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, move it one location to the right.', True, 'https://marvelsnap.pro/cards/spell03nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell05NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, give it +2 Power.', True, 'https://marvelsnap.pro/cards/spell04nicominoru', True, 	'["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell06NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, replace that card\'s location.', True, 'https://marvelsnap.pro/cards/spell05nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell07NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, add a copy of it to your hand.', True, 'https://marvelsnap.pro/cards/spell06nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell08NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, double this card\'s Power.', True, 'https://marvelsnap.pro/cards/spell07nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru"]')
            ]

        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])

    def test_fuzzy_search_multicard_1(self):
        """
        Test that a card returning multiple summons matches an expected search
        when a character differs in the search
        """
        result = self.database.search('ico Minoru')
        expected_results = [
            Card('NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, cast a spell. <i>(The spell changes each turn.)</i>', True, 'https://marvelsnap.pro/cards/nicominoru', False, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell02NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, it becomes a Demon.', True, 'https://marvelsnap.pro/cards/spell01nicominoru', True, '["Demon", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell03NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, destroy it to draw two cards.', True, 'https://marvelsnap.pro/cards/spell02nicominoru', True, '["Spell01NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell04NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, move it one location to the right.', True, 'https://marvelsnap.pro/cards/spell03nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell05NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, give it +2 Power.', True, 'https://marvelsnap.pro/cards/spell04nicominoru', True, 	'["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell06NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, replace that card\'s location.', True, 'https://marvelsnap.pro/cards/spell05nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell07NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, add a copy of it to your hand.', True, 'https://marvelsnap.pro/cards/spell06nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell07NicoMinoru"]'),
            Card('Spell08NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, double this card\'s Power.', True, 'https://marvelsnap.pro/cards/spell07nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru"]')
            ]

        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])

    def test_location_search(self):
        """
        Test to ensure that a location may be searched
        """
        result = self.database.search('Altar of Death')
        expected_results = [Location('AltarOfDeath', 'Altar of Death', 'After you play a card here, destroy it to get +2 Energy next turn.', 'Rare', True, 'https://marvelsnap.pro/cards/altarofdeath')]

        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])
    
    def test_card_partial_search(self):
        """
        Test that a card may be searched via a partial name, such that we
        do not need to supply the full name with spaces for it to be found
        """
        result = self.database.search('hope')
        expected_results = [Card('HopeSummers', 'Hope Summers', '3', '3', 'After you play a card here, you get +2 Energy next turn.', False, 'https://marvelsnap.pro/cards/hopesummers', False, '[]')]
        
        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])

    def test_card_partial_search_not_found(self):
        """
        Test that a card with too small of a search value will not be found.
        In this specific example, I'm searching for "M" and expecting it to
        NOT match to "Mobius M. Mobius"
        """
        result = self.database.search('m')
        expected_results = []

        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])

    def test_card_partial_search_not_found(self):
        """
        Test that we can find "Mobius" from the above search by specifying
        a partial of the name (e.g. "Mobius")
        """
        result = self.database.search('Mobius')
        expected_results = [Card('MobiusMMobius', 'Mobius M. Mobius', '3', '3', '<b>Ongoing:</b> Your Costs can\'t be increased. Your opponent\'s Costs can\'t be reduced.', True, 'https://marvelsnap.pro/cards/mobiusmmobius', False, '[]')]

        self.assertEqual(len(expected_results), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_results[i], result[i])

    def test_resolve_tokens(self):
        """
        Test that the resolve_tokens_to_base() function successfully resolves
        an array of tokens to the base cards that can summon them
        """
        cards = self.database.search('Soul Stone')
        result = utils.resolve_tokens_to_base(self.database, cards)

        expected_result = [
            Card('Thanos', 'Thanos', '6', '10', 'At the start of the game, shuffle the six Infinity Stones into your deck.', True, 'https://marvelsnap.pro/cards/thanos', False, '["SpaceStone", "RealityStone", "TimeStone", "MindStone", "PowerStone", "SoulStone"]')
        ]

        self.assertEqual(len(expected_result), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_result[i], result[i])

    def test_insert_tokens(self):
        """
        Test that we can go from a base card to have the tokens added to the
        array of cards.
        """
        cards = self.database.search('Thanos')
        result = utils.insert_tokens_from_cards(self.database, cards)

        expected_result = [
            Card('Thanos', 'Thanos', '6', '10', 'At the start of the game, shuffle the six Infinity Stones into your deck.', True, 'https://marvelsnap.pro/cards/thanos', False, '["SpaceStone", "RealityStone", "TimeStone", "MindStone", "PowerStone", "SoulStone"]'),
            Card('SpaceStone', 'Space Stone', '1', '1', '<b>On Reveal:</b> Next turn, you can move one card to this location. Draw a card.', True, 'https://marvelsnap.pro/cards/spacestone', True, '["Thanos"]'),
            Card('RealityStone', 'Reality Stone', '1', '1', '<b>On Reveal:</b> Transform this location into a new one. Draw a card.', True, 'https://marvelsnap.pro/cards/realitystone', True, '["Thanos"]'),
            Card('TimeStone', 'Time Stone', '1', '1', '<b>On Reveal:</b> Draw a card. Next turn, you get +1 Energy.', True, 'https://marvelsnap.pro/cards/timestone', True, '["Thanos"]'),
            Card('MindStone', 'Mind Stone', '1', '1', '<b>On Reveal:</b> Draw 2 1-Cost cards from your deck.', True, 'https://marvelsnap.pro/cards/mindstone', True, '["Thanos"]'),
            Card('PowerStone', 'Power Stone', '1', '3', '<b>Ongoing:</b> If you\'ve played all 6 stones, Thanos has +10 Power. <i>(wherever he is)</i>', True, 'https://marvelsnap.pro/cards/powerstone', True, '["Thanos"]'),
            Card('SoulStone', 'Soul Stone', '1', '1', '<b>Ongoing:</b> Enemy cards here have -1 Power.', True, 'https://marvelsnap.pro/cards/soulstone', True, '["Thanos"]')
        ]

        self.assertEqual(len(expected_result), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_result[i], result[i])
        

if __name__ == '__main__':
    unittest.main()