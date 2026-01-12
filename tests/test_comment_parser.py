#!python

import datetime
import logging
import argparse
import os
import sys
import time

from database import Database, Card
from reddit_connect import RedditConnect
from comments import CommentParser
import utils

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO)
logging.captureWarnings(True)

if __name__ == '__main__':
    
    logging.info('Starting Reddit bot')

    # Configuration variables for running. We first apply default values to all
    # of the variables, next we will fetch each variable from the environment
    # variables (useful for running in a Docker container), overriding all default
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
        dry_run = os.environ.get('DRY_RUN').lower() in ['true', '1', 't']
    if os.environ.get('DEBUG') is not None:
        debug = os.environ.get('DEBUG').lower() in ['true', '1', 't']
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

    # Initialize Reddit connection
    reddit_connect = RedditConnect(client_id, client_secret, user_agent, reddit_username, reddit_password)
    subreddit_instance = reddit_connect.get_subreddit(subreddit)

    # Initialize database
    db = Database(config_file)

    # Main loop to process comments
    while True:
        try:
            for comment in subreddit_instance.stream.comments():
                if dry_run:
                    logging.info(f'Dry run: Processing comment {comment.id}')
                else:
                    logging.info(f'Processing comment {comment.id}')

                parser = CommentParser(comment)
                results = parser.parse()

                if not results:
                    continue

                # Construct the response message
                response_message = "Here are the cards you requested:\n"
                for result in results:
                    card = db.get_card_by_name(result, max_fuzzy_distance, exact_match_threshold)
                    if card:
                        response_message += f"- {card.name}: {card.description}\n"
                    else:
                        response_message += f"- No card found matching '{result}'\n"

                # Construct the GitHub issue link with pre-filled body
                github_issue_url = "https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new"
                if comment.url:
                    github_issue_url += f"?body=[Original Comment]({comment.url})"
                else:
                    logging.warning(f"Comment {comment.id} does not have a URL. Skipping pre-filled body.")

                response_message += f"\nIf you encounter any issues, please [report here]({github_issue_url})."

                # Post the response
                if not dry_run:
                    comment.reply(response_message)
                    logging.info(f'Replied to comment {comment.id}')

        except Exception as e:
            logging.error(f'An error occurred: {e}')
            time.sleep(60)  # Wait for a minute before retrying