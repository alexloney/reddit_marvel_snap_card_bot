class Comment:
    def __init__(self, id: str, author: str, body: str, url: str):
        self.id = id
        self.author = author
        self.body = body
        self.url = url

    def update_github_link(self) -> None:
        github_new_issue_url = "https://github.com/alexloney/reddit_marvel_snap_card_bot/issues/new"
        updated_body = f"{self.body} [Create Issue]({github_new_issue_url}?body=[Original Comment]({self.url}))"
        self.body = updated_body