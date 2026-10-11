import re

import Levenshtein

from . import Card
from . import Match

# Words of an Entry's name shorter than this are not matched on their own
MINIMUM_SPLIT_MATCH_LENGTH = 3


def _normalize(text: str):
    """
    Lowercase a string and strip special characters so that names compare by
    their letters and digits only.
    """
    return re.sub(r'\W+', '', text.lower())


def _distance(a: str, b: str):
    """
    The edit (Levenshtein) distance between two normalized strings. 0 means
    they are identical, larger values are further apart.
    """
    return Levenshtein.distance(_normalize(a), _normalize(b))


def _best_word_distance(name: str, query: str):
    """
    The closest distance between the query and either the whole name or any
    single word of the name.
    """
    best = _distance(name, query)
    for word in re.split('[^a-zA-Z0-9]+', name):
        if len(word) >= MINIMUM_SPLIT_MATCH_LENGTH:
            best = min(best, _distance(word, query))
    return best


class Catalog:
    """
    All of the Entries the bot knows about and how Tags resolve to them.

    `source` is the seam to the upstream card data: anything with a `fetch()`
    returning `(cards, locations)`. Call `refresh()` to load or reload them.
    """
    def __init__(self, source, max_fuzzy_distance: int = 2, exact_match_threshold: int = 3):
        self.source = source
        self.max_fuzzy_distance = max_fuzzy_distance
        self.exact_match_threshold = exact_match_threshold
        self.entries = []

    def refresh(self):
        """
        Reload the Entries from the source. The new Entries are fully built
        before they replace the old ones, so a failed refresh raises and leaves
        the existing Catalog untouched.
        """
        cards, locations = self.source.fetch()
        self.entries = list(cards) + list(locations)

    def _search(self, query: str):
        """
        Find the Entries whose name is the closest match to the query.

        An Entry whose whole name matches exactly wins outright, so [[Death]]
        does not also return "Altar of Death". Otherwise every Entry tied for
        the closest match on its whole name or any single word of it is
        returned. Unless that match is exact, a query this short is rejected,
        to prevent a single letter like 'm' from matching "Gym" in "Maxwells
        Gym", and a longer query must be within the maximum fuzzy distance.
        """
        candidates = [e for e in self.entries if e.searchable]

        exact = [e for e in candidates if _distance(e.name, query) == 0]
        if exact:
            return exact

        scored = [(_best_word_distance(e.name, query), e) for e in candidates]
        if not scored:
            return []

        best = min(score for score, _ in scored)
        if best != 0:
            if len(query) <= self.exact_match_threshold:
                return []
            if best > self.max_fuzzy_distance:
                return []

        return [e for score, e in scored if score == best]

    def _find_by_def_id(self, def_id: str):
        """
        Look up an Entry by its exact def_id instead of a fuzzy name match
        """
        for entry in self.entries:
            if entry.def_id == def_id and entry.matchable:
                return entry
        return None

    def _base_card_for(self, entry):
        """
        If the Entry is a Token, return the Base Card that creates it, or the
        Token itself if no Base Card can be found. Any other Entry is returned
        unchanged.
        """
        if not isinstance(entry, Card) or not entry.is_token:
            return entry

        for def_id in entry.connected_cards:
            card = self._find_by_def_id(def_id)
            if isinstance(card, Card) and not card.is_token and not card.game_mode:
                return card

        # Nico links to her spells BUT her spells do not link back to her, so
        # when the forward lookup finds nothing, search for any Base Card that
        # lists this Token.
        for card in self.entries:
            if isinstance(card, Card) and not card.is_token and not card.game_mode \
                    and entry.def_id in card.connected_cards:
                return card

        return entry

    def _tokens_of(self, entry):
        """
        The Tokens listed by a Base Card, in the order the Card lists them. A
        game mode Card stands alone: it has no Tokens and is no Card's Token.
        """
        if not isinstance(entry, Card) or entry.is_token or entry.game_mode:
            return []

        tokens = []
        for def_id in entry.connected_cards:
            token = self._find_by_def_id(def_id)
            if token is None or token.def_id == entry.def_id:
                # Upstream data sometimes has a card list itself as connected
                continue
            if isinstance(token, Card) and token.game_mode:
                continue
            tokens.append(token)
        return tokens

    def resolve(self, tags):
        """
        Turn the Tags of a Request into the Matches that make up its Reply.

        Each Tag is fuzzy matched; a matched Token is replaced by its Base Card
        and a Base Card carries the Tokens of its Card Family. A Base Card or
        Location matched by several Tags (directly or through its Tokens) is
        returned once, though a Token may appear under more than one Base Card.
        """
        matches = []
        seen = set()
        for tag in tags:
            for entry in self._search(tag):
                head = self._base_card_for(entry)
                if head.def_id in seen:
                    continue
                seen.add(head.def_id)
                matches.append(Match(head, self._tokens_of(head)))
        return matches
