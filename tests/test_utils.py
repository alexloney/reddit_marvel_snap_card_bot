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
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False)
        ]

        result = utils.remove_duplicate_cards(cards)
        expected_result = [
            Card('Odin', 'Odin', '6', '8', 'On Reveal: Activate the On Reveal abilities of your other cards here.', True, 'https://marvelsnap.pro/cards/odin', False, '[]', False),
            Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False)
        ]

        self.assertEqual(expected_result, result)

if __name__ == '__main__':
    unittest.main()