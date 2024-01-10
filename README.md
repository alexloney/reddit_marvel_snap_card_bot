# Reddit Marvel Snap Card Bot
This is a bot for displaying information about Marvel Snap cards on Reddit. It 
operates by monitoring comments as they come through the Marvel Snap subreddit 
(/r/MarvelSnap) and checking each comment for the inclusion of a `[[card_name]]`. 
If something of this form is found, it will reply to the comment with details 
about the requested card, including power, cost, and ability.

This bot creation began when I noticed that the /u/MarvelSnapCardBot had not
posted any card responses in almost a month. From there, I decided to try 
creating a Reddit bot to see what is required for that process.

This bot is intended to mostly provide the same functionality as the original 
/u/MarvelSnapCardBot did, with the following enhancements:
* Open Source! - I was unable to find the previous bots source code to determine how it operated, which resulted in building this from scratch. Many similar Reddit and Discord bots are closed-source, however I want to make this open source to help anyone that may wish to build similar bots or to enhance this bot
* Fuzzy card searching - Cards will not have to be an exact match to work, instead if they are reasonably close enough to an exact match, it will count and display the card. So small typos may occur and the bot will handle it correctly. This is performed by using approximate string matching or "edit distance" between the supplied search term and the actual card name
* No filesystem usage - I'm achieving this by checking the replies to a comment before commenting on it and checking to see if the bot has already replied to the comment. This is to allow the bot to run in an environment where it does not have access to a persistent filesystem where it may store IDs for comments it has already commented on.
* ENV and CLI configurable - Connection details and configurations controllable via the environment variables and CLI, for easy Docker integration or manually running
* Dry-Run mode - Run without actually replying, great for testing
* Unit test coverage - Many components have unit test coverage
* CI/CD coverage - Unit tests are executed with every push to CI/CD environment
* Partial search supported - Card names do not need to be the full name, for example "Mobius" can be used to search for "Mobius M. Mobius"

Things still left to do:
* Obtain approval from /r/MarvelSnap moderators to allow the bot to operate - I've sent two messages to the /r/MarvelSnap moderators, awaiting response.

## Usage
Here are some example snippets to use this

### Docker CLI
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
