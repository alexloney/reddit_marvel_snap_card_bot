import unittest
import sys

sys.path.append('../snap_bot')
sys.path.append('snap_bot')
from database import Card

class TestCommentParser(unittest.TestCase):
    def test_card_text_generation(self):
        """
        Test that a card string output is the exact expected string output for
        displaying
        """
        card = Card('Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine')
        card.format_ability_from_html()

        card_text = str(card)
        expected_card_text = r'**\[[Wolverine](https://marvelsnap.pro/cards/wolverine)\]** **Cost:** 2 **Power:** 2  **Ability:** When this is discarded or destroyed, regenerate it with +2 Power at a random location.' + '\n\n'

        self.assertEqual(expected_card_text, card_text)
    
    def test_card_text_generation_html(self):
        """
        Test that a card string output with HTML contents is the exact string
        output for displaying
        """
        card = Card('Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, cast a spell. <i>(The spell changes each turn.)</i>', True, 'https://marvelsnap.pro/cards/nicominoru')
        card.format_ability_from_html()

        card_text = str(card)
        expected_card_text = r'**\[[Nico Minoru](https://marvelsnap.pro/cards/nicominoru)\]** **Cost:** 1 **Power:** 2  **Ability:** **On Reveal:** After you play your next card, cast a spell. *(The spell changes each turn.)*' + '\n\n'

        self.assertEqual(expected_card_text, card_text)
        
    def test_card_text_generation(self):
        """
        Test that a card makred as unreleased includes the appropriate tag
        """
        card = Card('Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', False, 'https://marvelsnap.pro/cards/wolverine')
        card.format_ability_from_html()

        card_text = str(card)
        expected_card_text = r'**\[[Wolverine](https://marvelsnap.pro/cards/wolverine)\]** (Unreleased) **Cost:** 2 **Power:** 2  **Ability:** When this is discarded or destroyed, regenerate it with +2 Power at a random location.' + '\n\n'

        self.assertEqual(expected_card_text, card_text)

if __name__ == '__main__':
    unittest.main()