class Comment:
    def __init__(self, id: str, author: str, body: str, url: str):
        self.id = id
        self.author = author
        self.body = body
        self.url = f"https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new?body=[Original Comment]({url})"
