"Simple wrapper for tumblr posts"

from datetime import datetime
from typing import TypedDict
from pytumblr2 import TumblrRestClient

with open('tumblr.keys') as f:
    k1, k2, k3, k4 = [l.strip() for l in f.readlines()]
    tumblr = TumblrRestClient(k1, k2, k3, k4)


class Post(TypedDict):
    timestamp: int
    datetime: datetime
    tags: list[str]
    short_url: str

limit = 20

def get_posts(
    blogname: str,
    cutoff: datetime | None,
    limit=20,
    offset=0
):

    before_cutoff = True
    while before_cutoff:
        resp = tumblr.posts(
            blogname, limit=limit, offset=offset)

        # print(resp)
        if resp.get("meta", {}).get('status') == 429:  # type: ignore
            raise ValueError("Limit exceeded!")

        posts: list[Post] = resp.get('posts', [])  # type: ignore
        if not posts:
            break

        offset += limit
        for post in posts:
            post['datetime'] = datetime.fromtimestamp(post['timestamp'])
            if cutoff and post['datetime'] <= cutoff:
                before_cutoff = False
                break
            yield post