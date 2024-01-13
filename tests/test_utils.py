import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
import utils
from database import Card

class TestCommentParser(unittest.TestCase):
    def test_duplicate_removal(self):
        """
        Providing a list of cards with duplicates in them, verify that all
        duplicates have been removed from the list of cards.
        """
        cards = [
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]'),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]'),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]'),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]'),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]')
        ]

        result = utils.remove_duplicate_cards(cards)
        expected_result = [
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]'),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]')
        ]

        self.assertEqual(len(expected_result), len(result))
        for i in range(0, len(result)):
            self.assertEqual(expected_result[i], result[i])

if __name__ == '__main__':
    unittest.main()