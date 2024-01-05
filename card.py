from entry import Entry

class Card(Entry):
    def __init__(self, name, cost, power, ability, released, url):
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