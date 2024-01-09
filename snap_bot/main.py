#!python

import datetime
import logging
import argparse
import os
import sys
import time

from database import Database
from reddit_connect import RedditConnect
from comments import CommentParser

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO)
logging.captureWarnings(True)

if __name__ == '__main__':
    
    logging.info('Starting Reddit bot')

    # Configuration variables for running. We first apply default values to all
    # of the variables, next we will fetch each variable from the environment
    # variables (useful for unning in a Docker container), overriding all default
    # values. Finally, we will again fetch each variable from the CLI arguments
    # as the final say in the variable value
    subreddit = ''
    config_file = ''
    db_update_timeout = 60*60*24
    max_fuzzy_distance = 2
    dry_run = False
    debug = False
    client_id = ''
    client_secret = ''
    user_agent = ''
    reddit_username = ''
    reddit_password = ''

    if os.environ.get('SUBREDDIT') is not None:
        subreddit = os.environ.get('SUBREDDIT')
    if os.environ.get('CONFIG_FILE') is not None:
        config_file = os.environ.get('CONFIG_FILE')
    if os.environ.get('DB_TIMEOUT') is not None:
        db_update_timeout = int(os.environ.get('DB_TIMEOUT'))
    if os.environ.get('MAX_FUZZY_DISTANCE') is not None:
        max_fuzzy_distance = int(os.environ.get('MAX_FUZZY_DISTANCE'))
    if os.environ.get('DRY_RUN') is not None:
        if os.environ.get('DRY_RUN').lower() == 'true':
            dry_run = True
        else:
            dry_run = False
    if os.environ.get('DEBUG') is not None:
        if os.environ.get('DEBUG').lower() == 'true':
            debug = True
        else:
            debug = False
    if os.environ.get('CLIENT_ID') is not None:
        client_id = os.environ.get('CLIENT_ID')
    if os.environ.get('CLIENT_SECRET') is not None:
        client_secret = os.environ.get('CLIENT_SECRET')
    if os.environ.get('USER_AGENT') is not None:
        user_agent = os.environ.get('USER_AGENT')
    if os.environ.get('REDDIT_USERNAME') is not None:
        reddit_username = os.environ.get('REDDIT_USERNAME')
    if os.environ.get('REDDIT_PASSWORD') is not None:
        reddit_password = os.environ.get('REDDIT_PASSWORD')

    parser = argparse.ArgumentParser(description='Marvel Snap Card Bot for Reddit')
    parser.add_argument(
        '--subreddit', 
        '-s', 
        default=subreddit,
        help='Subreddit to monitor comments from, use \'+\' to monitor multiple at the same time (env: SUBREDDIT)')
    parser.add_argument(
        '--config-file',
        '-c',
        default=config_file,
        help='Configuration file to use for secrets (env: CONFIG_FILE)')
    parser.add_argument(
        '--database-update-timeout',
        '-u',
        default=db_update_timeout,
        help='Delay (in seconds) between database refresh (env: DB_TIMEOUT)')
    parser.add_argument(
        '--max-fuzzy-distance',
        default=max_fuzzy_distance,
        help='Allowed distance between search and match (env: MAX_FUZZY_DISTANCE)')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run but do not actually post to Reddit (env: DRY_RUN)')
    parser.add_argument(
        '--debug',
        '-d',
        action='store_true',
        help='Display additonal debug logging (env: DEBUG)')
    parser.add_argument(
        '--client-id',
        default=client_id,
        help='Reddit application client ID (env: CLIENT_ID)')
    parser.add_argument(
        '--client-secret',
        default=client_secret,
        help='Reddit application client secret (env: CLIENT_SECRET)')
    parser.add_argument(
        '--user-agent',
        default=client_secret,
        help='Reddit application user agent (env: USER_AGENT)')
    parser.add_argument(
        '--reddit-username',
        default=reddit_username,
        help='Reddit account username (env: REDDIT_USERNAME)')
    parser.add_argument(
        '--reddit-password',
        default=reddit_password,
        help='Reddit account password (env: REDDIT_PASSWORD)')
    
    args = parser.parse_args()

    subreddit = args.subreddit
    config_file = args.config_file
    db_update_timeout = args.database_update_timeout
    max_fuzzy_distance = args.max_fuzzy_distance
    dry_run = args.dry_run
    debug = args.debug
    client_id = args.client_id
    client_secret = args.client_secret
    user_agent = args.user_agent
    reddit_username = args.reddit_username
    reddit_password = args.reddit_password

    logging.info('Subreddit: ' + subreddit)
    logging.info('Config File: ' + config_file)
    logging.info('DB Update Timeout: ' + str(db_update_timeout))
    logging.info('Max Fuzzing Distance: ' + str(max_fuzzy_distance))
    logging.info('Dry Run: ' + str(dry_run))
    logging.info('Debug: ' + str(debug))
    logging.info('Client ID: ' + client_id)
    logging.info('User Agent: ' + user_agent)
    logging.info('Reddit Username: ' + reddit_username)

    if debug:
        logging.getLogger("").setLevel(logging.DEBUG)
        logging.debug('Debug logging enabled')

    if len(config_file) == 0 and \
       (len(client_id) == 0 or \
        len(client_secret) == 0 or \
        len(user_agent) == 0 or \
        len(reddit_username) == 0 or \
        len(reddit_password) == 0):
        print('Error: Either a config file, or all config details must be provided')
        sys.exit(1)
    
    if len(subreddit) == 0:
        print('Error: You must provide a subreddit to monitor')
        sys.exit(1)

    database = Database(max_fuzzy_distance)

    # Perform our initial database update to get the first version of our card
    # lookups
    logging.info('Loading card lookup database')
    database.update_card_database()
    last_database_update = datetime.datetime.now()
    logging.info('Next DB update in ' + str(db_update_timeout) + 's')

    logging.info('Establishing Reddit connection (' + subreddit + ')')
    if len(config_file) > 0:
        logging.info('Using Reddit config file')
        reddit_connect = RedditConnect(subreddit)
        reddit_connect.init_reddit_config(config_file)
    else:
        logging.info('Using supplied id/secret/agent/user/pass')
        reddit_connect = RedditConnect(subreddit)
        reddit_connect.init_reddit_args(client_id, client_secret, user_agent, reddit_username, reddit_password)
    logging.info('Reddit connection established')

    # Continue forever...or untill killed
    try:
        while True:

            # Check the current date/time and compare it to the last time the
            # card lookup database has been updated. If it exceeds our set timeout
            # interval, update our internal card lookup database and reset our
            # last time we updated.
            current_time = datetime.datetime.now()
            if (current_time - last_database_update).total_seconds() > db_update_timeout:
                logging.info('Reloading card lookup database')
                database.update_card_database()
                last_database_update = datetime.datetime.now()

            # Fetch the next set of comments
            for comment in reddit_connect.get_comments_shallow():

                # Prevent replying to my own comments, if the author of the
                # comment is the bot itself, then simply ignore the comment
                if reddit_connect.get_my_username() == comment.author:
                    continue

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
                    response += '*Message generated by ' + reddit_connect.get_my_username() + '. Use syntax [[card_name]] to get a reply like this. Report any issues on [github](https://github.com/alexloney/reddit_marvel_snap_card_bot).*'

                    logging.info('Detected comment: ' + comment.url)
                    
                    # Obtaining the authors is a more expensive operation, so we
                    # only do this at the very end before we submit the reply.
                    # In this case, we obtain the author names and verify that
                    # our username is not in a reply to this comment. This is to
                    # prevent us from replying to the same comment multiple times
                    authors = reddit_connect.get_comment_reply_author_names(comment.id)
                    if reddit_connect.get_my_username() not in authors:
                        logging.info('Submitting reply')
                        logging.debug(response)
                        if dry_run == False:
                            reddit_connect.add_reply(comment.id, response)
                    else:
                        logging.info('Ignoring comment, bot reply detected')
                        

    except KeyboardInterrupt:
        pass


