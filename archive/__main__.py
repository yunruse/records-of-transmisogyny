from argparse import ArgumentParser
from csv import DictReader, DictWriter
from datetime import datetime
from pathlib import Path

from requests import HTTPError, ConnectionError

from .tumblr import get_posts
from .wayback import archive_job, get_job_result

parser = ArgumentParser()
parser.add_argument("blog", help="The tumblr blog name to archive.")
parser.add_argument("--records", default="./records", type=Path)

args = parser.parse_args()

POSTS: Path = args.records / f'{args.blog}.tsv'
cutoff = None

posts: list[dict[str, str]] = []
if POSTS.is_file():
    with open(POSTS) as f:
        for post in DictReader(f, delimiter="\t"):
            posts.append(post)

cutoff = None
if posts:
    try:
        cutoff = datetime.fromisoformat(posts[-1]['timestamp'])
    except ValueError:
        pass


# First pass: get URLs from tumblr
scraped_posts = get_posts(args.blog, cutoff)

for post in get_posts(args.blog, cutoff):
    posts.append({
        "timestamp": post['datetime'].isoformat(),
        "tags": ','.join(post['tags']),
        "url": post['short_url'],
        "archived url": "",
    })

posts.sort(key=lambda p: p['timestamp'])

# Second pass: Archive URLs (and resolve archive.org jobs)

for post in posts:
    aurl: str | None = post['archived url']
    try:
        if not aurl:
            post['archived url'] = archive_job(post['url'])
        
        elif aurl.startswith("spn2"):
            post['archived url'] = get_job_result(aurl) or aurl

    except (HTTPError, ConnectionError) as e:
        print("Not every post could be archived due to ratelimiting; try again soon")
        break

if posts:
    fieldnames = posts[0].keys()
    with open(POSTS, "w") as f:
        writer = DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(posts)
