import json

from . import Entry

class Card(Entry):
    def __init__(self, def_id: str, name: str, cost: int, power: int, ability: str, released: bool, url: str, is_token: bool, connected_cards, summoned: bool):
        super().__init__(def_id, name, ability, released, url)
        self.cost = cost
        self.power = power
        self.is_token = is_token
        self.connected_cards = json.loads(connected_cards)
        self.formatted_ability = ''
        self.summoned = summoned
        self.searchable = True
        self.matchable = True

    def to_constructor_string(self):
        """
        Useful for debugging or writing test cases, this outputs a card in a
        format that may be copied and pasted to create a constructor for it.
        It's not perfect as it doesn't account for spaces in the JSON and quotes
        in the abilities, but overall it's fine for what I need.
        """
        template = r"Card('{def_id}', '{name}', '{cost}', '{power}', '{ability}', {released}, {url}, {is_token}, '{connected_cards}', {summoned})"

        return template.format(
            def_id = self.def_id,
            name = self.name,
            cost = self.cost,
            power = self.power,
            ability = self.ability,
            released = ('True' if self.released else 'False'),
            url = ("'" + self.url + "'" if self.url is not None else 'None'),
            is_token = ('True' if self.is_token else 'False'),
            connected_cards = json.dumps(self.connected_cards),
            summoned = ('True' if self.summoned else 'False'))

    def __str__(self):
        """
        Combone the fields in this class into a single output that may be
        displayed with correct formatting
        """
        template = ''

        if self.summoned:
            template += r'* '
        
        if self.url is not None:
            template += r'**\[[{name}]({url})\]** '
        else:
            template += r'**\[{name}\]** '

        template += r'{status}**Cost:** {cost} **Power:** {power}  \n**Ability:** {ability}\n\n'
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
               self.is_token == other.is_token and \
               self.connected_cards == other.connected_cards and \
               self.url == other.url