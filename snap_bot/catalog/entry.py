import re

class Entry:
    def __init__(self, def_id: str, name: str, ability: str, released: bool, url: str):
        self.def_id = def_id
        self.name = name
        self.ability = ability
        self.released = released
        self.url = url
        self.formatted_ability = self.ability
        self.searchable = True
        self.matchable = True

    def format_ability_text(self):
        """
        For use when using marvelsnap.io as the source, converting the output
        into a pretty print output for display on Reddit
        """
        self.formatted_ability = self.ability.replace('On Reveal:', '**On Reveal:**').replace('Ongoing:', '**Ongoing:**')
    
    def format_ability_from_html(self):
        """
        For use when using marvelsnap.pro as the source, converting the output
        into a pretty print output for display on Reddit
        """
        self.formatted_ability = self.ability.replace('<b>', '**').replace('</b>', '**').replace('<i>', '*').replace('</i>', '*').replace('</color>', '')
        self.formatted_ability = re.sub(r'<color=[^>]+>', '', self.formatted_ability)

    def plain_ability(self):
        """
        The ability with any HTML markup removed, for use in plain text where
        no formatting can be shown
        """
        return re.sub(r'<[^>]+>', '', self.ability)