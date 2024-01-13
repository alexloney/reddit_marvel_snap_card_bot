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
        expected_results = [Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False)]
 
        self.assertEqual(expected_results, result)
    
    def test_fuzzy_search_1(self):
        """
        Test a fuzzy search with 1 character different. Given the default operation
        of the Database class, this should be acceptable
        """
        result = self.database.search('wolerine')
        expected_results = [Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False)]
 
        self.assertEqual(expected_results, result)

    def test_fuzzy_search_2(self):
        """
        Test a fuzzy search with 2 characters different. Given the default operation
        of the Database class, this should be acceptable
        """
        result = self.database.search('olerine')
        expected_results = [Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False)]
 
        self.assertEqual(expected_results, result)

    def test_fuzzy_search_3(self):
        """
        Test a fuzzy search with 3 characters different. Given the default operation
        of the Database class, this should fail
        """
        result = self.database.search('lerine')
        expected_results = [Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False)]

        self.assertNotEqual(len(expected_results), len(result))

    def test_exact_search_multicard(self):
        """
        Test that a card returning multiple summons matches an expected search
        """
        result = self.database.search('Nico Minoru')
        expected_results = [
            Card('NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, cast a spell. <i>(The spell changes each turn.)</i>', True, 'https://marvelsnap.pro/cards/nicominoru', False, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell02NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, it becomes a Demon.', True, 'https://marvelsnap.pro/cards/spell01nicominoru', True, '["Demon", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell03NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, destroy it to draw two cards.', True, 'https://marvelsnap.pro/cards/spell02nicominoru', True, '["Spell01NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell04NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, move it one location to the right.', True, 'https://marvelsnap.pro/cards/spell03nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell05NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, give it +2 Power.', True, 'https://marvelsnap.pro/cards/spell04nicominoru', True, 	'["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell06NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, replace that card\'s location.', True, 'https://marvelsnap.pro/cards/spell05nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell07NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, add a copy of it to your hand.', True, 'https://marvelsnap.pro/cards/spell06nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell08NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, double this card\'s Power.', True, 'https://marvelsnap.pro/cards/spell07nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru"]', False)
            ]

        self.assertEqual(expected_results, result)

    def test_fuzzy_search_multicard_1(self):
        """
        Test that a card returning multiple summons matches an expected search
        when a character differs in the search
        """
        result = self.database.search('ico Minoru')
        expected_results = [
            Card('NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, cast a spell. <i>(The spell changes each turn.)</i>', True, 'https://marvelsnap.pro/cards/nicominoru', False, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell02NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, it becomes a Demon.', True, 'https://marvelsnap.pro/cards/spell01nicominoru', True, '["Demon", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell03NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, destroy it to draw two cards.', True, 'https://marvelsnap.pro/cards/spell02nicominoru', True, '["Spell01NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell04NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, move it one location to the right.', True, 'https://marvelsnap.pro/cards/spell03nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell05NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, give it +2 Power.', True, 'https://marvelsnap.pro/cards/spell04nicominoru', True, 	'["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell06NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, replace that card\'s location.', True, 'https://marvelsnap.pro/cards/spell05nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell07NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, add a copy of it to your hand.', True, 'https://marvelsnap.pro/cards/spell06nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell08NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, double this card\'s Power.', True, 'https://marvelsnap.pro/cards/spell07nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru"]', False)
            ]

        self.assertEqual(expected_results, result)

    def test_location_search(self):
        """
        Test to ensure that a location may be searched
        """
        result = self.database.search('Altar of Death')
        expected_results = [Location('AltarOfDeath', 'Altar of Death', 'After you play a card here, destroy it to get +2 Energy next turn.', 'Rare', True, 'https://marvelsnap.pro/cards/altarofdeath')]

        self.assertEqual(expected_results, result)
    
    def test_card_partial_search(self):
        """
        Test that a card may be searched via a partial name, such that we
        do not need to supply the full name with spaces for it to be found
        """
        result = self.database.search('hope')
        expected_results = [Card('HopeSummers', 'Hope Summers', '3', '3', 'After you play a card here, you get +2 Energy next turn.', False, 'https://marvelsnap.pro/cards/hopesummers', False, '[]', False)]
        
        self.assertEqual(expected_results, result)

    def test_card_partial_search_not_found(self):
        """
        Test that a card with too small of a search value will not be found.
        In this specific example, I'm searching for "M" and expecting it to
        NOT match to "Mobius M. Mobius"
        """
        result = self.database.search('m')
        expected_results = []

        self.assertEqual(expected_results, result)

    def test_card_partial_search_not_found(self):
        """
        Test that we can find "Mobius" from the above search by specifying
        a partial of the name (e.g. "Mobius")
        """
        result = self.database.search('Mobius')
        expected_results = [Card('MobiusMMobius', 'Mobius M. Mobius', '3', '3', '<b>Ongoing:</b> Your Costs can\'t be increased. Your opponent\'s Costs can\'t be reduced.', True, 'https://marvelsnap.pro/cards/mobiusmmobius', False, '[]', False)]

        self.assertEqual(expected_results, result)

    def test_resolve_tokens(self):
        """
        Test that the resolve_tokens_to_base() function successfully resolves
        an array of tokens to the base cards that can summon them
        """
        cards = self.database.search('Soul Stone')
        result = utils.resolve_tokens_to_base(self.database, cards)

        expected_result = [
            Card('Thanos', 'Thanos', '6', '10', 'At the start of the game, shuffle the six Infinity Stones into your deck.', True, 'https://marvelsnap.pro/cards/thanos', False, '["SpaceStone", "RealityStone", "TimeStone", "MindStone", "PowerStone", "SoulStone"]', False)
        ]

        self.assertEqual(expected_result, result)

    def test_insert_tokens(self):
        """
        Test that we can go from a base card to have the tokens added to the
        array of cards.
        """
        cards = self.database.search('Thanos')
        result = utils.insert_tokens_from_cards(self.database, cards)

        expected_result = [
            Card('Thanos', 'Thanos', '6', '10', 'At the start of the game, shuffle the six Infinity Stones into your deck.', True, 'https://marvelsnap.pro/cards/thanos', False, '["SpaceStone", "RealityStone", "TimeStone", "MindStone", "PowerStone", "SoulStone"]', False),
            Card('SpaceStone', 'Space Stone', '1', '1', '<b>On Reveal:</b> Next turn, you can move one card to this location. Draw a card.', True, 'https://marvelsnap.pro/cards/spacestone', True, '["Thanos"]', True),
            Card('RealityStone', 'Reality Stone', '1', '1', '<b>On Reveal:</b> Transform this location into a new one. Draw a card.', True, 'https://marvelsnap.pro/cards/realitystone', True, '["Thanos"]', True),
            Card('TimeStone', 'Time Stone', '1', '1', '<b>On Reveal:</b> Draw a card. Next turn, you get +1 Energy.', True, 'https://marvelsnap.pro/cards/timestone', True, '["Thanos"]', True),
            Card('MindStone', 'Mind Stone', '1', '1', '<b>On Reveal:</b> Draw 2 1-Cost cards from your deck.', True, 'https://marvelsnap.pro/cards/mindstone', True, '["Thanos"]', True),
            Card('PowerStone', 'Power Stone', '1', '3', '<b>Ongoing:</b> If you\'ve played all 6 stones, Thanos has +10 Power. <i>(wherever he is)</i>', True, 'https://marvelsnap.pro/cards/powerstone', True, '["Thanos"]', True),
            Card('SoulStone', 'Soul Stone', '1', '1', '<b>Ongoing:</b> Enemy cards here have -1 Power.', True, 'https://marvelsnap.pro/cards/soulstone', True, '["Thanos"]', True)
        ]

        self.assertEqual(expected_result, result)
    
    def test_match_nico_duplication(self):
        """
        Verify that a card with many summons (Nico SPECIFICALLY) can correctly
        pull from the base card search, each of the summons.
        """
        cards = self.database.search('nico')
        cards = utils.remove_duplicate_cards(cards)
        cards = utils.resolve_tokens_to_base(self.database, cards)
        cards = utils.remove_duplicate_cards(cards)
        results = utils.insert_tokens_from_cards(self.database, cards)

        expected_results = [
            Card('NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, cast a spell. <i>(The spell changes each turn.)</i>', True, 'https://marvelsnap.pro/cards/nicominoru', False, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', False),
            Card('Spell02NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, it becomes a Demon.', True, 'https://marvelsnap.pro/cards/spell01nicominoru', True, '["Demon", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', True),
            Card('Spell03NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, destroy it to draw two cards.', True, 'https://marvelsnap.pro/cards/spell02nicominoru', True, '["Spell01NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', True),
            Card('Spell04NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, move it one location to the right.', True, 'https://marvelsnap.pro/cards/spell03nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', True),
            Card('Spell05NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, give it +2 Power.', True, 'https://marvelsnap.pro/cards/spell04nicominoru', True, 	'["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', True),
            Card('Spell06NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, replace that card\'s location.', True, 'https://marvelsnap.pro/cards/spell05nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell06NicoMinoru", "Spell07NicoMinoru"]', True),
            Card('Spell07NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, add a copy of it to your hand.', True, 'https://marvelsnap.pro/cards/spell06nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell07NicoMinoru"]', True),
            Card('Spell08NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, double this card\'s Power.', True, 'https://marvelsnap.pro/cards/spell07nicominoru', True, '["Spell01NicoMinoru", "Spell02NicoMinoru", "Spell03NicoMinoru", "Spell04NicoMinoru", "Spell05NicoMinoru", "Spell06NicoMinoru"]', True)
            ]
        
        self.assertEqual(expected_results, results)
    
    def test_not_searchable_card(self):
        """
        Verify that a card marked as not searchable is not searchable
        """
        cards = self.database.search('Abomination')

        expected_results = [
            Card('Abomination', 'Abomination', '5', '9', '<i>"Foolish rabble! You are beneath me!"</i>', True, 'https://marvelsnap.pro/cards/abomination', False, '[]', False)
        ]

        self.assertEqual(expected_results, cards)
    
    def test_search_evolved(self):
        """
        Test that a search for High Evo will return the evolved cards as well as
        the updated "Evolved" names to differentiate them from the standard
        non-evolved cards
        """
        cards = self.database.search('High Evolutionary')
        cards = utils.remove_duplicate_cards(cards)
        cards = utils.resolve_tokens_to_base(self.database, cards)
        cards = utils.remove_duplicate_cards(cards)
        results = utils.insert_tokens_from_cards(self.database, cards)

        expected_results = [
            Card('HighEvolutionary', 'High Evolutionary', '4', '4', 'At the start of the game, unlock the potential of your cards with no abilities.', True, 'https://marvelsnap.pro/cards/highevolutionary', False, '["EvolvedWasp","EvolvedMistyKnight","EvolvedShocker","EvolvedCyclops","EvolvedTheThing","EvolvedAbomination","EvolvedHulk"]', False),
            Card('EvolvedWasp', 'Evolved Wasp', '0', '1', '<color=#fad728><b>On Reveal:</b> Afflict an enemy card here with -1 Power.</color>', True, None, True, '[]', True),
            Card('EvolvedMistyKnight', 'Evolved Misty Knight', '1', '2', '<color=#fad728>When you end a turn with unspent Energy, give one of your other cards +1 Power.</color>', True, None, True, '[]', True),
            Card('EvolvedShocker', 'Evolved Shocker', '2', '3', '<color=#fad728><b>On Reveal:</b> Give the leftmost card in your hand -1 Cost.</color>', True, None, True, '[]', True),
            Card('EvolvedCyclops', 'Evolved Cyclops', '3', '4', '<color=#fad728>When you end a turn with unspent Energy, afflict 2 enemy cards here with -1 Power.</color>', True, None, True, '[]', True),
            Card('EvolvedTheThing', 'Evolved The Thing', '4', '6', '<color=#fad728><b>On Reveal:</b> Afflict 3 enemy cards here with -1 Power.</color>', True, None, True, '[]', True),
            Card('EvolvedAbomination', 'Evolved Abomination', '5', '9', '<color=#fad728>Costs 1 less for each enemy card in play that\'s afflicted with negative Power.</color>', True, None, True, '[]', True),
            Card('EvolvedHulk', 'Evolved Hulk', '6', '12', '<color=#fad728>When you end a turn with unspent Energy, +2 Power. <i>(if in hand or in play)</i></color>', True, None, True, '[]', True)
        ]

        self.assertEqual(expected_results, results)
    
    def test_ebony_order(self):
        """
        I discovered a bug where if you search for "Ebody Blade" or other similar
        cards, it will return return looking like that is the base card and the
        card that may summon it is the summon card. This tests to ensure that
        that situation does not occur.
        """

        cards = self.database.search('Ebony Blade')
        cards = utils.remove_duplicate_cards(cards)
        cards = utils.resolve_tokens_to_base(self.database, cards)
        cards = utils.remove_duplicate_cards(cards)
        results = utils.insert_tokens_from_cards(self.database, cards)

        expected_results = [
            Card('BlackKnight', 'Black Knight', '1', '2', 'After you discard a card, add the Ebony Blade to your hand with that card\'s Power. <i>(once per game)</i>', True, 'https://marvelsnap.pro/cards/blackknight', False, '["EbonyBlade"]', True),
            Card('EbonyBlade', 'Ebony Blade', '4', '0', '<b>Ongoing:</b> Can\'t be destroyed and its Power can\'t be reduced.', False, 'https://marvelsnap.pro/cards/ebonyblade', True, '["BlackKnight"]', False)
        ]

        self.assertEqual(expected_results, results)


if __name__ == '__main__':
    unittest.main()