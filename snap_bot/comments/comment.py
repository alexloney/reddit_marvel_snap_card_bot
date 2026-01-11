class Comment:
    def __init__(self, id: str, author: str, body: str, url: str):
        self.id = id
        self.author = author
        self.body = body
        self.url = f"{url}?from_comment={id}"

    def get_github_url(self) -> str:
        return self.url