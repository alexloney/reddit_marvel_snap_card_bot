class Comment:
    def __init__(self, id: str, author: str, body: str, url: str):
        self.id = id
        self.author = author
        self.body = body
        self.url = url

    def update_body_with_issue_link(self):
        new_body = f"{self.body} [Create New Issue](https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new?body=[Original%20Comment]({self.url}))"
        return Comment(self.id, self.author, new_body, self.url)