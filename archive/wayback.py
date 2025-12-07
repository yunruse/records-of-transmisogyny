"Simple wrapper for the Wayback Machine in archive.org"

import requests

with open('archive.keys') as f:
    k1, k2 = [l.strip() for l in f.readlines()]


def archive_job(url: str):
    "Archive a URL to archive.org and get its job ID."

    r = requests.post(
        "https://web.archive.org/save",
        data={
            "url": url,
            "capture_all": 1,
        },
        headers={
            "Accept": "application/json",
            "Authorization": f"LOW {k1}:{k2}",
        }
    )
    r.raise_for_status()
    return r.json()['job_id']

def get_job_result(job_id: str):
    "Return a URL from an archive job, or None if pending."
    r = requests.get(
        f"https://web.archive.org/save/status/{job_id}")
    r.raise_for_status()
    data = r.json()
    if data.get('status') != 'success':
        return None

    return f'https://web.archive.org/{data['timestamp']}/{data['original_url']}'