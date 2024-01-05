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
        response += '**Location:** Rarity ' + self.rarity + '  '
        response += 'Description:** ' + self.ability
        response += '\n\n'

        return response