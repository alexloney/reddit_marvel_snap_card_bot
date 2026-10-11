class Match:
    """
    One matched Entry for a Reply. For a Card this is the Base Card followed by
    the Tokens of its Card Family; for a Location, or a Token with no Base Card,
    the Entry stands alone.
    """
    def __init__(self, entry, tokens=()):
        self.entry = entry
        self.tokens = list(tokens)

    def __str__(self):
        text = str(self.entry)
        for token in self.tokens:
            text += '* ' + str(token)
        return text

    def plain_text(self):
        text = self.entry.plain_text()
        for token in self.tokens:
            text += '- ' + token.plain_text()
        return text
