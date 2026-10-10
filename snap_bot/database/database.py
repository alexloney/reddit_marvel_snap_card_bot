import requests
import json
import time
from .patches import patches
from .marvelsnappro import card_from_record
from wells.utils import retry

from . import Card
from . import Location
from . import Match

class Database:
    def __init__(self, max_fuzzy_distance: int = 2, exact_match_threshold: int = 3):
        self.cards = []
        self.locations = []
        self.max_fuzzy_distance = max_fuzzy_distance
        self.exact_match_threshold = exact_match_threshold

    @retry(times=3, interval=[1, 5, 10])
    def download_url(self, url: str):
        """
        Given a URL, download the contents from it and return the response. If
        the download fails for any reason, this will retry up to 3 times before
        finally considering it a failure.
        """
        with requests.Session() as session:
            response = session.get(url)

            if not response.ok:
                response.raise_for_status()
        
        return response

    def patch_card(self, card):
        if card.def_id in patches:
            if 'searchable' in patches[card.def_id]:
                card.searchable = patches[card.def_id]['searchable']
            if 'matchable' in patches[card.def_id]:
                card.matchable = patches[card.def_id]['matchable']
            if 'name' in patches[card.def_id]:
                card.name = patches[card.def_id]['name']
            if 'url' in patches[card.def_id]:
                card.url = patches[card.def_id]['url']
            if 'is_Token' in patches[card.def_id]:
                card.is_token = patches[card.def_id]['is_Token']
            if 'connected_cards' in patches[card.def_id]:
                card.connected_cards = json.loads(patches[card.def_id]['connected_cards'])

    def update_card_database_marvelsnappro(self):
        """
        Use the marvelsnap.pro website as an API source to pull card information.
        Pull the cards and store them in a local lookup table.
        """
        api_url = 'https://static2.marvelsnap.pro/snap/do.php?cmd=getcards'
        api_location_url = 'https://static2.marvelsnap.pro/snap/do.php?cmd=getlocations'

        data = self.download_url(api_url)
        jdata = data.json()

        self.cards = []
        self.locations = []
        now = time.time()
        for card in jdata:
            self.cards.append(card_from_record(card, jdata[card], now))
            self.patch_card(self.cards[-1])
            self.cards[-1].format_ability_from_html()

        data = self.download_url(api_location_url)
        jdata = data.json()

        for location in jdata:
            def_id = jdata[location]['CardDefId']
            name = jdata[location]['name']
            ability = jdata[location]['description']
            rarity = jdata[location]['rarity']
            released_text = jdata[location]['released']
            url = 'https://marvelsnap.pro/cards/' + location

            released = True
            if released_text == '0':
                released = False

            self.locations.append(Location(def_id, name, ability, rarity, released, url))

    def update_card_database(self):
        """
        Update the internal database of cards by querying the appropriate API.
        Originally I intended to be able to swap out APIs or detect if one is
        down and automatically update to a different API. However, I have found
        that marvelsnap.pro appears to provide a much more comprehensive card
        catalog and details than that of marvelsnap.io.

        If you wish to enhance this with new APIs, you could add them here along
        with logic for when each one should be used.
        """
        self.update_card_database_marvelsnappro()
    
    def _search(self, query: str):
        """
        Thus function will loop through all cards located in our lookup and find
        the clostest match to the search term. It will then loop through all
        possible summons and locate the closest possible match and if a better
        match is found, it'll take the base card(s) that can summon it and will
        place them in our result set.

        For example, if the search is [[Soul Stone]], it will (probably) not find
        a matching regular card, but the Soul Stone card that can be summoned
        by Thanos would be located. It would then include Thanos instead of
        Soul Stone. Now this may seem a little counter-intuitive at first, but
        Thanos as a base card will later pull in all the summons, so the output
        that the user will eventually see is Thanos, followed by all stones.
        """
        best_match_score = 9999
        best_match = []

        for card in self.cards:
            if not card.searchable:
                continue

            next_base_score = card.test_distance(query)
            if next_base_score < best_match_score:
                best_match_score = next_base_score
                best_match = [card]
            elif next_base_score == best_match_score:
                best_match.append(card)

        for location in self.locations:
            # if not location.searchable:
            #     continue
            
            next_base_score = location.test_distance(query)
            if next_base_score < best_match_score:
                best_match_score = next_base_score
                best_match = [location]
            elif next_base_score == best_match_score:
                best_match.append(location)

        if best_match_score != 0:

            for card in self.cards:
                if not card.searchable:
                    continue
                
                next_split_score = card.test_distance_splits(query)
                if next_split_score < best_match_score:
                    best_match_score = next_split_score
                    best_match = [card]
                elif next_split_score == best_match_score:
                    if card not in best_match:
                        best_match.append(card)

            for location in self.locations:
                # if not location.searchable:
                #     continue
                
                next_split_score = location.test_distance_splits(query)
                if next_split_score < best_match_score:
                    best_match_score = next_split_score
                    best_match = [location]
                elif next_split_score == best_match_score:
                    if location not in best_match:
                        best_match.append(location)

        # Consolidate the resulting searches together and return the output.
        # We have a few cases here:
        #  1. If the query string is too small, we want for it to have found
        #     an exact match. This is to prevent a single letter like 'm' from
        #     matching to "Gym" in "Maxwells Gym", for example
        #  2. Next, we will check the score to our minimum fuzzy match score
        #     required. If the score is equal to or better than the minimum
        #     allowed, return it.
        #  3. Finally, if the match is not good enough for the above, we will
        #     return no result.

        # Check to see if our best match is within the threshold for matches,
        # if so we will output it. If it is not, we will return an empty response
        if len(query) <= self.exact_match_threshold and best_match_score != 0:
            return []
        
        if best_match_score <= self.max_fuzzy_distance:
            return best_match
        
        return []

    def _find_by_def_id(self, query: str):
        """
        Look up an Entry by its exact def_id instead of a fuzzy name match
        """

        # Always check cards first, so that the base card will be at the top of
        # the response
        for card in self.cards:
            if card.def_id == query and card.matchable:
                return card
        
        for card in self.locations:
            if card.def_id == query:
                return card
        
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
            if card is not None and not card.is_token and not card.game_mode:
                return card

        # Nico links to her spells BUT her spells do not link back to her, so
        # when the forward lookup finds nothing, search for any Base Card that
        # lists this Token.
        for card in self.cards:
            if not card.is_token and not card.game_mode and entry.def_id in card.connected_cards:
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
            # Upstream data sometimes has a card list itself as connected
            if token is not None and token.def_id != entry.def_id and                     not (isinstance(token, Card) and token.game_mode):
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
