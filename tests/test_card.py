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
        card = Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', True, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False)
        card.format_ability_from_html()

        card_text = str(card)
        expected_card_text = r'**\[[Wolverine](https://marvelsnap.pro/cards/wolverine)\]** **Cost:** 2 **Power:** 2' + '  \n' + r'**Ability:** When this is discarded or destroyed, regenerate it with +2 Power at a random location.' + '\n\n'

        self.assertEqual(expected_card_text, card_text)
    
    def test_card_text_generation_html(self):
        """
        Test that a card string output with HTML contents is the exact string
        output for displaying
        """
        card = Card('NicoMinoru', 'Nico Minoru', '1', '2', '<b>On Reveal:</b> After you play your next card, cast a spell. <i>(The spell changes each turn.)</i>', True, 'https://marvelsnap.pro/cards/nicominoru', False, '[]', False)
        card.format_ability_from_html()

        card_text = str(card)
        expected_card_text = r'**\[[Nico Minoru](https://marvelsnap.pro/cards/nicominoru)\]** **Cost:** 1 **Power:** 2' + '  \n' + r'**Ability:** **On Reveal:** After you play your next card, cast a spell. *(The spell changes each turn.)*' + '\n\n'

        self.assertEqual(expected_card_text, card_text)
        
    def test_card_text_generation(self):
        """
        Test that a card marked as unreleased includes the appropriate tag
        """
        card = Card('Wolverine', 'Wolverine', '2', '2', 'When this is discarded or destroyed, regenerate it with +2 Power at a random location.', False, 'https://marvelsnap.pro/cards/wolverine', False, '[]', False)
        card.format_ability_from_html()

        card_text = str(card)
        expected_card_text = r'**\[[Wolverine](https://marvelsnap.pro/cards/wolverine)\]** (Unreleased) **Cost:** 2 **Power:** 2' + '  \n' + r'**Ability:** When this is discarded or destroyed, regenerate it with +2 Power at a random location.' + '\n\n'

        self.assertEqual(expected_card_text, card_text)
    
    def test_card_text_summon_generation(self):
        """
        Test that a summoned card produces the correct formatting
        """
        card = Card('MindStone', 'Mind Stone', '1', '1', '<b>On Reveal:</b> Draw 2 1-Cost cards from your deck.', True, 'https://marvelsnap.pro/cards/mindstone', True, '["Thanos"]', True)
        card.format_ability_from_html()

        card_text = str(card)
        expected_card_text = r'* **\[[Mind Stone](https://marvelsnap.pro/cards/mindstone)\]** **Cost:** 1 **Power:** 1' + '  \n' + r'**Ability:** **On Reveal:** Draw 2 1-Cost cards from your deck.' + '\n\n'

        self.assertEqual(expected_card_text, card_text)
    
    def test_card_text_evoled(self):
        """
        Test that an evolved card does not have the color HTML text
        """
        card = Card('Hulk', 'Hulk', '6', '12', '<color=#fad728>When you end a turn with unspent Energy, +2 Power. <i>(if in hand or in play)</i></color>', True, None, False, '[]', True)
        card.format_ability_from_html()

        card_text = str(card)
        expected_card_text = r'* **\[Hulk\]** **Cost:** 6 **Power:** 12' + '  \n' + r'**Ability:** When you end a turn with unspent Energy, +2 Power. *(if in hand or in play)*' + '\n\n'

        self.assertEqual(expected_card_text, card_text)

if __name__ == '__main__':
    unittest.main()