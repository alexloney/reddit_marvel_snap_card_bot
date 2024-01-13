import re

from . import Lookup

class Entry(Lookup):
    def __init__(self, def_id: str, name: str, ability: str, released: bool, url: str):
        self.def_id = def_id
        self.name = name
        self.ability = ability
        self.released = released
        self.url = url
        self.formatted_ability = self.ability
        self.minimum_split_match_length = 3

    def test_distance(self, search: str, base_str: str = None):
        """
        Given a search term, normalize it and test it against the normalized
        search term for this card to return a distance between the two terms
        """
        if base_str is not None:
            return self.test_close_normalized(base_str, search)
        return self.test_close_normalized(self.name, search)

    def test_distance_splits(self, search: str):
        """
        Given a search term, split the name on alphanumeric characters then
        return the best match from matching to the split strings.
        """

        best_result = self.test_distance(search)

        match = re.split('[^a-zA-Z0-0]+', self.name)
        if match:
            for group in match:
                if len(group) >= self.minimum_split_match_length:
                    next_result = self.test_distance(search, group)
                    if next_result < best_result:
                        best_result = next_result

        return best_result

    def format_ability_text(self):
        """
        For use when using marvelsnap.io as the source, converting the output
        into a pretty print output for display on Reddit
        """
        self.formatted_ability = str.replace('On Reveal:', '**On Reveal:**').replace('Ongoing:', '**Ongoing:**')
    
    def format_ability_from_html(self):
        """
        For use when using marvelsnap.pro as the source, converting the output
        into a pretty print output for display on Reddit
        """
        self.formatted_ability = self.ability.replace('<b>', '**').replace('</b>', '**').replace('<i>', '*').replace('</i>', '*').replace('</color>', '')
        self.formatted_ability = re.sub(r'<color=[^>]+>', '', self.formatted_ability)