from argparse import ArgumentParser
from csv import DictReader, DictWriter
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Iterable

from requests import HTTPError, ConnectionError
from tqdm import tqdm

from .tumblr import Post, get_posts
from .wayback import archive_job, get_job_result

parser = ArgumentParser()
parser.add_argument(
    "blog",
    help="The tumblr blog name to archive.")
parser.add_argument(
    "--records", type=Path, default="./records",
    help="The directory archive TSV files should go to.")
parser.add_argument(
    "--timeout", type=int, default=2,
    help="The timeout per request (in seconds) for archive.org to avoid ratelimiting. Defaults to two seconds.")

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
scraped_posts: Iterable[Post]
try:
    scraped_posts = get_posts(args.blog, cutoff)
    scraped_posts = list(tqdm(scraped_posts, "Scraping posts"))
except ValueError:
    print("Tumblr reached rate limit; attempting to archive")
    scraped_posts = []

for post in scraped_posts:
    posts.append({
        "timestamp": post['datetime'].isoformat(),
        "tags": ','.join(post['tags']),
        "url": post['short_url'],
        "archived url": "",
    })

posts.sort(key=lambda p: p['timestamp'])

# Second pass: Archive URLs (and resolve archive.org jobs)

for post in tqdm(posts, "Archiving"):
    aurl: str | None = post['archived url']
    archived = False
    try:
        if not aurl:
            post['archived url'] = archive_job(post['url'])
            archived = True
        
        elif aurl.startswith("spn2"):
            post['archived url'] = get_job_result(aurl) or aurl
            archived = True

    except (HTTPError, ConnectionError) as e:
        print("Not every post could be archived due to ratelimiting; try again soon")
        print(e)
        break
    if archived:
        sleep(args.timeout)

if posts:
    fieldnames = posts[0].keys()
    with open(POSTS, "w") as f:
        writer = DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(posts)
