#!python

import praw
import json
import requests
from wells.utils import retry
import string
import re
import Levenshtein

class RedditConnect:
    def __init__(self, config_file):
        self.init_reddit(config_file)
    
    def init_reddit(self, config_file):
        with open(config_file) as f:
            config = json.load(f)
        
        self.reddit = praw.Reddit(
            client_id = config['client_id'],
            client_secret = config['client_secret'],
            username = config['username'],
            password = config['password'],
            user_agent = config['user_agent'])
    
    def get_hot_submissions(self):
        return self.reddit.subreddit('MarvelSnap').hot(limit=10)

class Lookup:
    def __init__(self):
        pass

    def normalize(self, data):
        """
        Normalize a string for better searching, this will convert the string to
        lowercase and remove special characters from it.
        """
        return re.sub(r'\W+', '', data.lower())
    
    def how_close(self, str1, str2):
        """
        Determine the levenshtein distance between two strings, this is effectively
        the "edit" distance between them, how many substitutions must be made to
        one string in order for it to become the second string. A value of 0
        indicates that the two strings are identical, larger values indicate
        that they are further apart.
        """
        return Levenshtein.distance(str1, str2)

    def test_close_normalized(self, str1, str2):
        """
        Test two strings, normalizing both before testing, then return the edit
        (e.g. Levenshtein) distance between the two strings.
        """
        return self.how_close(self.normalize(str1), self.normalize(str2))

class Entry(Lookup):
    def __init__(self, name, ability, released, url):
        self.name = name
        self.ability = ability
        self.released = released
        self.url = url
        self.formatted_ability = self.ability

    def test_distance(self, search):
        """
        Given a search term, normalize it and test it against the normalized
        search term for this card to return a distance between the two terms
        """
        return self.test_close_normalized(self.name, search)
    
    def format_ability_text(self):
        """
        For use when using marvelsnap.io as the source, converting the output
        into a pretty print output for display on Reddit
        """
        self.formatted_ability = str.replace('On Reveal:', '**On Reveal:**').replace('Ongoing:', '**Ongoing:**')
    
    def format_ability_from_html(self):
        """
        For use when using marvelsnap.pro as the source, converting the output
        into a pretty print output for display on Reddit
        """
        self.formatted_ability = self.ability.replace('<b>', '**').replace('</b>', '**').replace('<i>', '*').replace('</i>', '*')

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
            response += '**\[[' + self.name + '](' + self.url + ')]\]** '
        else:
            response += '**\[' + self.name + '\]** '
        if self.released == '0':
            response += '(Unreleased) '
        response += '**Cost:** ' + str(self.cost) + ' '
        response += '**Power:** ' + str(self.power) + '  '
        response += '**Ability:** ' + self.formatted_ability
        response += '\n\n'

        return response

class Location(Entry):
    def __init__(self, name, ability, rarity, released, url):
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
        if self.released == '0':
            response += '(Unreleased) '
        response += '**Location:** Rarity ' + self.rarity + '  '
        response += 'Description:** ' + self.ability
        response += '\n\n'

        return response

class Database:
    def __init__(self, max_fuzzy_distance=2):
        self.cards = []
        self.locations = []
        self.summons = []
        self.max_fuzzy_distance = max_fuzzy_distance

    @retry(times=3, interval=[1, 5, 10])
    def download_url(self, url):
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
            released = '1'
            if is_token == '0' and source == 'None':
                released = '0'

            # NOTE: this also contains a "connected_cards" field which will connect
            #       cards together. For instance, "Space Stone" lists "Thanos" as a
            #       connection. I am currently not using this as it appears to
            #       provide connections that may not be useful, like "Spider-Man"
            #       to "Uncle Ben" (which doesn't exist). However, in the future
            #       it may be useful to look into this connection and use it for
            #       printing additional cards.

            if is_token == '1':
                self.summons.append(Card(name, cost, power, ability, released, url))
                self.cards[-1].format_ability_from_html()
            else:
                self.cards.append(Card(name, cost, power, ability, released, url))
                self.cards[-1].format_ability_from_html()

        data = self.download_url(api_location_url)
        jdata = data.json()

        for location in jdata:
            name = jdata[location]['name']
            ability = jdata[location]['description']
            rarity = jdata[location]['rarity']
            released = jdata[location]['released']
            url = 'https://marvelsnap.pro/cards/' + location
        
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
    
    def search(self, query):
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
            next_match_score = card.test_distance(query)
            if next_match_score < best_match_score:
                best_match_score = next_match_score
                best_match = [card]
            elif next_match_score == best_match_score:
                best_match.append(card)
        
        # Next check the Summons so that the summon will be listed second after
        # the card
        for summon in self.summons:
            next_match_score = summon.test_distance(query)
            if next_match_score < best_match_score:
                best_match_score = next_match_score
                best_match = [summon]
            elif next_match_score == best_match_score:
                best_match.append(summon)
        
        for location in self.locations:
            next_match_score = location.test_distance(query)
            if next_match_score < best_match_score:
                best_match_score = next_match_score
                best_match = [location]
            elif next_match_score == best_match_score:
                best_match.append(location)

        # Check to see if our best match is within the threshold for matches,
        # if so we will output it. If it is not, we will return an empty response
        if best_match_score <= self.max_fuzzy_distance:
            return best_match
        return []


# ==============================================================================
# Below is test code for development, once this is ready for an initial release
# the below should be removed and replaced with an actual logical loop for 
# processing requests from Reddit and responding to them.
#
# I intend for each processing loop to also check the current date/time and at
# specific intervals it will update the internal card list. Possibly daily at 
# a certain time?
# ==============================================================================

# reddit_connect = RedditConnect('config.json')

# for submission in reddit_connect.get_hot_submissions():
#     print(submission.title)

database = Database(2)
database.update_card_database()

response = database.search('hercules')
if len(response) > 0:
    for card in response:
        print(card, end='')
    print('*Message generated by MarvelSnapCardBot2. Use syntax [[card_name]] to get a reply like this. Report any issues on [github](https://github.com/alexloney/RedditMarvelSnapCardBot)*')

