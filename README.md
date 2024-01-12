# Reddit Marvel Snap Card Bot

## Overview

A few days prior to this bot being created, I went to the [/r/MarvelSnap](https://www.reddit.com/r/MarvelSnap) 
subreddit and made a comment where I tagged a card using the [[card]] notation. Previously, when a card was
tagged like this, the [/u/MarvelSnapCardBot](https://www.reddit.com/u/MarvelSnapCardBot) would reply with a
comment including the card information. However, the comment simply remained there with no reply.

I then investigated the /u/MarvelSnapCardBot and found that it had not replied to any comments in about
a month. I was unable to find the owner of the bot, the best I found was [this post on /r/MarvelSnap](https://www.reddit.com/r/MarvelSnap/comments/yjnvm5/introducing_marvel_snap_card_bot/)
where the bot introduced itself with details on how to use it. However, it did not seem to mention
who created it, so I had no way of reaching out to the owner of the bot to inform them that it was not
operational anymore.

From there, I decided to take on the project of building a replacement bot for /r/MarvelSnap as it seemed
like a fun and interesting challenge. Additionally, the original bot had some shortcomings (such as the
card had to be an exact match) that I wanted to take on and resolve.

## Usage

This bot is intended to run as a Reddit bot, where it will monitor the /r/MarvelSnap subreddit and 
when a comment is made that contains the text [[card]], it will attempt to look up the card information and
reply to the post with details about the card.

The bot uses marvelsnap.pro as the source of card data, so it will only be as up to date as marvelsnap.pro is.

## Features

The following are the features that this bot offers:
* Open Source! - I was unable to find the previous bots source code to determine how it operated, which resulted in building this from scratch. Many similar Reddit and Discord bots are closed-source, however I want to make this open source to help anyone that may wish to build similar bots or to enhance this bot
* Fuzzy card searching - Cards will not have to be an exact match to work, instead if they are reasonably close enough to an exact match, it will count and display the card. So small typos may occur and the bot will handle it correctly. This is performed by using approximate string matching or "edit distance" between the supplied search term and the actual card name
* No filesystem usage - I'm achieving this by checking the replies to a comment before commenting on it and checking to see if the bot has already replied to the comment. This is to allow the bot to run in an environment where it does not have access to a persistent filesystem where it may store IDs for comments it has already commented on.
* ENV and CLI configurable - Connection details and configurations controllable via the environment variables and CLI, for easy Docker integration or manually running
* Dry-Run mode - Run without actually replying, great for testing
* Unit test coverage - Many components have unit test coverage
* CI/CD coverage - Unit tests are executed with every push to CI/CD environment
* Partial search supported - Card names do not need to be the full name, for example "Mobius" can be used to search for "Mobius M. Mobius"

## TODO

Here are features that I am considering for changes/additons to the bot:
* Since it is running from a Docker container and not from any location where it does not have storage access, I am considering enhancing this to use a SQLite database for storing card details as well as details on the comments it has already seen.

## Deployment

This bot may be easily ran in two ways. You may run it directly from the command-line locally or you may run it from a Docker container. The local option is better for development/testing and the Docker option is better for long-term execution to provide persistent runtime

### Command-line
```bash
python snap_bot/main.py --config config.json --subreddit MarvelSnap
```

### Docker
```bash
docker pull ghcr.io/alexloney/reddit_marvel_snap_card_bot:latest
docker run --name reddit_marvel_snap_card_bot \
    --restart unless-stopped \
    -e SUBREDDIT="MarvelSnap" \
    -e CLIENT_ID="xxx" \
    -e CLIENT_SECRET="xxx" \
    -e USER_AGENT="xxx" \
    -e REDDIT_USERNAME="xxx" \
    -e REDDIT_PASSWORD="xxx" \
    -e TZ="America/Los_Angeles" \
    ghcr.io/alexloney/reddit_marvel_snap_card_bot:latest
```
