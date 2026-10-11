#!python

import datetime
import logging
import argparse
import os
import sys
import time

from catalog import Catalog, MarvelSnapPro
from reddit_connect import RedditConnect
from request_handler import RequestHandler

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
    exact_match_threshold = 3
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
    if os.environ.get('EXACT_MATCH_THRESHOLD') is not None:
        exact_match_threshold = int(os.environ.get('EXACT_MATCH_THRESHOLD'))
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
        type=int,
        help='Delay (in seconds) between database refresh (env: DB_TIMEOUT)')
    parser.add_argument(
        '--max-fuzzy-distance',
        default=max_fuzzy_distance,
        type=int,
        help='Allowed distance between search and match (env: MAX_FUZZY_DISTANCE)')
    parser.add_argument(
        '--exact-match-threshold',
        default=exact_match_threshold,
        type=int,
        help='Minimum string length required for an exact match to be made (env: EXACT_MATCH_THRESHOLD)')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=dry_run,
        help='Run but do not actually post to Reddit (env: DRY_RUN)')
    parser.add_argument(
        '--debug',
        '-d',
        action='store_true',
        default=debug,
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
        default=user_agent,
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
    exact_match_threshold = args.exact_match_threshold
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
    logging.info('Exact Match Threshold: ' + str(exact_match_threshold))
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

    catalog = Catalog(MarvelSnapPro(), max_fuzzy_distance, exact_match_threshold)

    # Perform our initial catalog refresh to get the first version of our card
    # lookups. Without it there is nothing to serve, so a failure here is fatal
    logging.info('Loading card catalog')
    catalog.refresh()
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

    request_handler = RequestHandler(catalog, reddit_connect, dry_run)

    # Continue forever...or untill killed
    try:
        while True:

            # Check the current date/time and compare it to the last time the
            # catalog has been refreshed. If it exceeds our set timeout
            # interval, refresh it and reset our last time we refreshed. A
            # failed refresh keeps serving the existing catalog and is retried
            # after the next interval.
            current_time = datetime.datetime.now()
            if (current_time - last_database_update).total_seconds() > db_update_timeout:
                logging.info('Reloading card catalog')
                try:
                    catalog.refresh()
                except Exception:
                    logging.exception('Catalog refresh failed, keeping the existing catalog')
                last_database_update = datetime.datetime.now()

            # Fetch the next set of comments
            for comment in reddit_connect.get_comments_shallow():

                request_handler.handle(comment)

    except KeyboardInterrupt:
        pass


