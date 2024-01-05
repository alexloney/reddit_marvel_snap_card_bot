from . import Entry

class Location(Entry):
    def __init__(self, name, ability, rarity, released, url):
        super().__init__(name, ability, released, url)
        self.rarity = rarity
    
    def __str__(self):
        """
        Format a location response in a nice way that may be used on Reddit
        """
        response = ''

        if self.url is not None:
            response += '**\[[' + self.name + '](' + self.url + ')\]** '
        else:
            response += '**\[' + self.name + '\]** '
        if self.released == '0':
            response += '(Unreleased) '
        response += '**Location:** Rarity ' + self.rarity + '  '
        response += 'Description:** ' + self.ability
        response += '\n\n'

        return response