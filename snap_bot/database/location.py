from . import Entry

class Location(Entry):
    def __init__(self, def_id: str, name:str, ability:str, rarity:str, released:bool, url:str):
        super().__init__(def_id, name, ability, released, url)
        self.rarity = rarity
    
    def __str__(self):
        """
        Format a location response in a nice way that may be used on Reddit
        """
        template = r'**\[[{name}]({url})\]** {status}**Location:** Rarity {rarity}  \n**Description:** {ability}\n\n'
        template = template.replace(r'\n', '\n')

        return template.format(
            name = self.name,
            url = self.url,
            status = ('(Unreleased) ' if not self.released else ''),
            rarity = self.rarity,
            ability = self.ability)

    def __eq__(self, other):
        """
        Equality operator for comparing locations
        """
        return self.name == other.name and \
               self.ability == other.ability and \
               self.rarity == other.rarity and \
               self.released == other.released and \
               self.url == other.url