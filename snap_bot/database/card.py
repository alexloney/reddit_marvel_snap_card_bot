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
        response = ''

        if self.url is not None:
            response += '**\[[' + self.name + '](' + self.url + ')\]** '
        else:
            response += '**\[' + self.name + '\]** '
        if self.released == '0':
            response += '(Unreleased) '
        response += '**Cost:** ' + str(self.cost) + ' '
        response += '**Power:** ' + str(self.power) + '  '
        response += '**Ability:** ' + self.formatted_ability
        response += '\n\n'

        return response

    def __eq__(self, other):
        return self.name == other.name and \
               self.cost == other.cost and \
               self.power == other.power and \
               self.ability == other.ability and \
               self.released == other.released and \
               self.url == other.url