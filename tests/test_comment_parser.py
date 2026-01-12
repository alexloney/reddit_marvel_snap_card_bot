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

    parser = argparse.ArgumentParser(description='Reddit bot for Marvel Snap card comments.')
    parser.add_argument('--subreddit', type=str, help='Subreddit to monitor')
    parser.add_argument('--config-file', type=str, help='Path to configuration file')
    parser.add_argument('--db-timeout', type=int, help='Database update timeout in seconds')
    parser.add_argument('--max-fuzzy-distance', type=int, help='Maximum Levenshtein distance for fuzzy matching')
    parser.add_argument('--exact-match-threshold', type=int, help='Threshold for exact match')
    parser.add_argument('--dry-run', action='store_true', help='Run the bot without making any changes')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--client-id', type=str, help='Reddit API client ID')
    parser.add_argument('--client-secret', type=str, help='Reddit API client secret')
    parser.add_argument('--user-agent', type=str, help='User agent string for Reddit API requests')
    parser.add_argument('--reddit-username', type=str, help='Reddit username')
    parser.add_argument('--reddit-password', type=str, help='Reddit password')

    args = parser.parse_args()

    if args.subreddit:
        subreddit = args.subreddit
    if args.config_file:
        config_file = args.config_file
    if args.db_timeout:
        db_update_timeout = args.db_timeout
    if args.max_fuzzy_distance:
        max_fuzzy_distance = args.max_fuzzy_distance
    if args.exact_match_threshold:
        exact_match_threshold = args.exact_match_threshold
    if args.dry_run:
        dry_run = True
    if args.debug:
        debug = True
    if args.client_id:
        client_id = args.client_id
    if args.client_secret:
        client_secret = args.client_secret
    if args.user_agent:
        user_agent = args.user_agent
    if args.reddit_username:
        reddit_username = args.reddit_username
    if args.reddit_password:
        reddit_password = args.reddit_password

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