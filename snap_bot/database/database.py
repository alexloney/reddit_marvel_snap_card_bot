import requests
from wells.utils import retry

from . import Card
from . import Location

class Database:
    def __init__(self, max_fuzzy_distance: int = 2, exact_match_threshold: int = 3):
        self.cards = []
        self.locations = []
        self.summons = []
        self.max_fuzzy_distance = max_fuzzy_distance
        self.exact_match_threshold = exact_match_threshold

    @retry(times=3, interval=[1, 5, 10])
    def download_url(self, url: str):
        """
        Given a URL, download the contents from it and return the response. If
        the download fails for any reason, this will retry up to 3 times before
        finally considering it a failure.
        """
        session = requests.Session()
        response = session.get(url)

        if not response.ok:
            raise requests.HTTPError(response)
        
        return response

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
        self.summons = []
        self.locations = []
        for card in jdata:
            name = jdata[card]['name']
            cost = jdata[card]['cost']
            power = jdata[card]['power']
            ability = jdata[card]['description']
            url = 'https://marvelsnap.pro/cards/' + card
            is_token = jdata[card]['is_Token']
            source = jdata[card]['source']

            # Cards do not appear to have a "released" flag, so I am inferring
            # that it is released by checking if it has a source and it is not
            # a token. This may need to be updated for a better way to determine
            released = True
            if is_token == '0' and source == 'None':
                released = False

            # NOTE: this also contains a "connected_cards" field which will connect
            #       cards together. For instance, "Space Stone" lists "Thanos" as a
            #       connection. I am currently not using this as it appears to
            #       provide connections that may not be useful, like "Spider-Man"
            #       to "Uncle Ben" (which doesn't exist). However, in the future
            #       it may be useful to look into this connection and use it for
            #       printing additional cards.

            if is_token == '1':
                self.summons.append(Card(name, cost, power, ability, released, url))
                self.summons[-1].format_ability_from_html()
            else:
                self.cards.append(Card(name, cost, power, ability, released, url))
                self.cards[-1].format_ability_from_html()

        data = self.download_url(api_location_url)
        jdata = data.json()

        for location in jdata:
            name = jdata[location]['name']
            ability = jdata[location]['description']
            rarity = jdata[location]['rarity']
            released_text = jdata[location]['released']
            url = 'https://marvelsnap.pro/cards/' + location

            released = True
            if released_text == '0':
                released = False

            self.locations.append(Location(name, ability, rarity, released, url))

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
    
    def search(self, query: str):
        """
        Loop through all cards and find the closest match, if multiple cards have
        the same closest match, fetch them all. This is to allow linked cards
        like Nico Minoru's spells to be connected together and output as one when
        Nico Minoru is found.
        """
        best_match_score = 99999
        best_match = []

        # Always check cards first, so that the base card will be at the top of
        # the response
        for card in self.cards:
            next_match_score = card.test_distance_splits(query)
            if next_match_score < best_match_score:
                best_match_score = next_match_score
                best_match = [card]
            elif next_match_score == best_match_score:
                best_match.append(card)
        
        # Next check the Summons so that the summon will be listed second after
        # the card
        for summon in self.summons:
            next_match_score = summon.test_distance_splits(query)
            if next_match_score < best_match_score:
                best_match_score = next_match_score
                best_match = [summon]
            elif next_match_score == best_match_score:
                best_match.append(summon)
        
        for location in self.locations:
            next_match_score = location.test_distance_splits(query)
            if next_match_score < best_match_score:
                best_match_score = next_match_score
                best_match = [location]
            elif next_match_score == best_match_score:
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
