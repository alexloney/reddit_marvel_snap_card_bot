from . import Lookup

class Entry(Lookup):
    def __init__(self, name, ability, released, url):
        self.name = name
        self.ability = ability
        self.released = released
        self.url = url
        self.formatted_ability = self.ability

    def test_distance(self, search):
        """
        Given a search term, normalize it and test it against the normalized
        search term for this card to return a distance between the two terms
        """
        return self.test_close_normalized(self.name, search)
    
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
        self.formatted_ability = self.ability.replace('<b>', '**').replace('</b>', '**').replace('<i>', '*').replace('</i>', '*')