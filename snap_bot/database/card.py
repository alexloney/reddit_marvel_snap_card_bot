from . import Entry

class Card(Entry):
    def __init__(self, name: str, cost: int, power: int, ability: str, released: bool, url: str):
        super().__init__(name, ability, released, url)
        self.cost = cost
        self.power = power
        self.formatted_ability = ''

    def __str__(self):
        """
        Combone the fields in this class into a single output that may be
        displayed with correct formatting
        """
        template = r'**\[[{name}]({url})\]** {status}**Cost:** {cost} **Power:** {power}  \n**Ability:** {ability}\n\n'
        template = template.replace(r'\n', '\n')

        return template.format(
            name = self.name,
            url = self.url,
            status = ('(Unreleased) ' if not self.released else ''),
            cost = self.cost,
            power = self.power,
            ability = self.formatted_ability)

    def __eq__(self, other):
        """
        Equality operator for compairing cards
        """
        return self.name == other.name and \
               self.cost == other.cost and \
               self.power == other.power and \
               self.ability == other.ability and \
               self.released == other.released and \
               self.url == other.url