import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from database import Location

class TestCommentParser(unittest.TestCase):
    def test_card_text_generation(self):
        """
        Test that a location generates the exact expected output text
        """
        location = Location('AltarOfDeath', 'Altar of Death', 'After you play a card here, destroy it to get +2 Energy next turn.', 'Rare', True, 'https://marvelsnap.pro/cards/altarofdeath')
        location_text = str(location)
        
        expected_location_text = r'**\[[Altar of Death](https://marvelsnap.pro/cards/altarofdeath)\]** **Location:** Rarity Rare' + '  \n' + r'**Description:** After you play a card here, destroy it to get +2 Energy next turn.' + '\n\n'

        self.assertEqual(expected_location_text, location_text)

    def test_card_text_generation(self):
        """
        Test that a card that is unreleased includes the appropriate tag
        """
        location = Location('AltarOfDeath', 'Altar of Death', 'After you play a card here, destroy it to get +2 Energy next turn.', 'Rare', False, 'https://marvelsnap.pro/cards/altarofdeath')
        location_text = str(location)
        
        expected_location_text = r'**\[[Altar of Death](https://marvelsnap.pro/cards/altarofdeath)\]** (Unreleased) **Location:** Rarity Rare' + '  \n' + r'**Description:** After you play a card here, destroy it to get +2 Energy next turn.' + '\n\n'

        self.assertEqual(expected_location_text, location_text)

if __name__ == '__main__':
    unittest.main()