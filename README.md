# records-of-transmisogyny

This is a record of certain tumblr blogs which indicate a general pattern of Tumblr's systematic transmisogyny.

Records are stored as `records/BLOGNAME.tsv`.

Posts are archived to archive.org as soon as possible (but may be subject to ratelimiting).

## `archive` tool

In the event you need to archive a blog yourself, this blog can automatically get all blog posts and put them on archive.org in case they are deleted.

1. Put [tumblr API keys](https://api.tumblr.com/console/calls/user/info) and [archive.org "s3" keys](https://archive.org/account/s3.php) into `tumblr.keys` and `archive.keys` respectively, each key on a newline.
2. `pip install requests pytumblr2 tqdm`
3. Run `python -m archive [blogname]`, as in `auto-archive.sh`

This can be ran multiple times to fetch newer posts and to continue to archive posts, as archive.org may induce ratelimiting.