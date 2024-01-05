from . import Entry

class Location(Entry):
    def __init__(self, name:str, ability:str, rarity:str, released:bool, url:str):
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
        if self.released == False:
            response += '(Unreleased) '
        response += '**Location:** Rarity ' + self.rarity + '  \n'
        response += '**Description:** ' + self.ability
        response += '\n\n'

        return response

    def __eq__(self, other):
        """
        Equality operator for comparing locations
        """
        return self.name == other.name and \
               self.ability == other.ability and \
               self.rarity == other.rarity and \
               self.released == other.released and \
               self.url == other.url