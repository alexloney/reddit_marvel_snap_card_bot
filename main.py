#!python

import praw
import json
import requests
from wells.utils import retry
import re
import Levenshtein
import datetime
import time
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO)
logging.captureWarnings(True)

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

class Comment:
    def __init__(self, id, body, url):
        self.id = id
        self.body = body
        self.url = url

class RedditConnect:
    def __init__(self, subreddit, config_file):
        self.subreddit_name = subreddit
        self.username = ''
        self.init_reddit(config_file)

        self.seen_comments = []

    def get_my_username(self):
        """
        Get the username of the account running that is running. No need for an
        extra query here to Reddit since we know the username from the config
        file, so instead we will just use what we logged in with.
        """
        return self.username
    
    def init_reddit(self, config_file):
        """
        Initialize the Reddit connection, use the details stored in the config
        file to initiate a connection to Reddit
        """
        with open(config_file) as f:
            config = json.load(f)
        
        self.reddit = praw.Reddit(
            client_id = config['client_id'],
            client_secret = config['client_secret'],
            username = config['username'],
            password = config['password'],
            user_agent = config['user_agent'])

        self.subreddit = self.reddit.subreddit(self.subreddit_name)

        self.username = config['username']
    
    def get_comments_shallow(self):
        """
        Get a list of comments, these may repeat as it pulls the last 100 comments
        each time it runs, so when we query again, we may get comments we've
        already seen. Because of that, we are using a `seen_comments` variable
        to keep track of comments we have already seen to prevent sending those
        back up to the caller
        """
        comments = []
        count = 0
        for comment in self.subreddit.comments():
            count += 1
            if comment.id not in self.seen_comments:
                self.seen_comments.append(comment.id)
                comments.append(Comment(comment.id, comment.body, 'https://reddit.com' + comment.permalink))
        
        # To prevent this list from simply growing to an unmanagable size, we
        # will simply remove old entries when it has more than 150, since the
        # query above only returns the past 100, this should be fine.
        while len(self.seen_comments) > 150:
            self.seen_comments.pop(0)

        return comments
    
    def get_comment_reply_author_names(self, id):
        """
        Fetch the names of the authors for a given comment.
        """
        comment = self.reddit.comment(id)
        comment.refresh()
        authors = []
        for reply in comment.replies.list():
            authors.append(reply.author.name)

        return authors

    def add_reply(self, comment_id, reply_text):
        comment = self.reddit.comment(comment_id)
        comment.reply(reply_text)

class CommentParser:
    def __init__(self, comment):
        self.comment = comment
    
    def parse(self):
        """
        Use a simple regex pattern to find all [[xxx]] entries in the comment
        body, returning a list of the entries found
        """
        match = re.findall(r'\[\[([^]]+)\]\]', self.comment.body)
        return match
            
if __name__ == '__main__':
    
    logging.info('Starting Reddit bot')

    # Variables, these can be moved to either ENV or CLI arguments
    subreddit = 'MarvelSnap'
    config_file = 'config.json'
    database_update_timeout = 60*60*24

    database = Database()

    # Perform our initial database update to get the first version of our card
    # lookups
    logging.info('Loading card lookup database')
    database.update_card_database()
    last_database_update = datetime.datetime.now()

    reddit_connect = RedditConnect('MarvelSnap', 'config.json')

    # Continue forever...or untill killed
    try:
        while True:

            # Check the current date/time and compare it to the last time the
            # card lookup database has been updated. If it exceeds our set timeout
            # interval, update our internal card lookup database and reset our
            # last time we updated.
            current_time = datetime.datetime.now()
            if (current_time - last_database_update).total_seconds() > database_update_timeout:
                logging.info('Reloading card lookup database')
                database.update_card_database()
                last_database_update = datetime.datetime.now()

            # Fetch the next set of comments
            for comment in reddit_connect.get_comments_shallow():

                # Parse the comment and fetch the card names from it
                parser = CommentParser(comment)
                card_names = parser.parse()

                # Generate a response based on the detected card names in the
                # comment
                response = ''
                for name in card_names:
                    for item in database.search(name):
                        response += str(item)

                # If our response has a length, this means we identified a card
                # request and correctly matched it to a card to reply with. If
                # that is the case, we may proceed with the request
                if len(response) > 0:
                    response += '*Message generated by ' + reddit_connect.get_my_username() + '. Use syntax [[card_name]] to get a reply like this. Report any issues on [github](https://github.com/alexloney/RedditMarvelSnapCardBot).*'

                    logging.info('Detected comment: ' + comment.url)
                    
                    # Obtaining the authors is a more expensive operation, so we
                    # only do this at the very end before we submit the reply.
                    # In this case, we obtain the author names and verify that
                    # our username is not in a reply to this comment. This is to
                    # prevent us from replying to the same comment multiple times
                    authors = reddit_connect.get_comment_reply_author_names(comment.id)
                    if reddit_connect.get_my_username() not in authors:
                        logging.info('Submitting reply')
                        reddit_connect.add_reply(comment.id, response)

    except KeyboardInterrupt:
        pass


