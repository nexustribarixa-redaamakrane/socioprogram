import requests
from datetime import datetime, timezone


def fetch_reddit_feed(subreddit):
    """Fetch newest posts from a subreddit via public JSON API."""
    try:
        headers = {'User-Agent': 'Socioprogram/1.0'}
        resp = requests.get(
            f'https://www.reddit.com/r/{subreddit}/new.json?limit=20',
            headers=headers, timeout=10
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        children = data.get('data', {}).get('children', [])

        posts = []
        for child in children:
            d = child.get('data', {})
            if d.get('is_sponsored'):
                continue  # Anti-ads: filter out sponsored content
            posts.append({
                'id': f"reddit_{d.get('id', '')}",
                'source': 'reddit',
                'author': d.get('author', 'unknown'),
                'title': d.get('title', ''),
                'content': d.get('selftext', '') or d.get('url', ''),
                'external_url': f"https://reddit.com{d.get('permalink', '')}",
                'created_at': datetime.fromtimestamp(d.get('created_utc', 0), tz=timezone.utc),
                'post_type': 'discussion',
            })
        return posts
    except Exception:
        return []


def fetch_github_feed(username):
    """Fetch public activity from a GitHub user."""
    try:
        resp = requests.get(
            f'https://api.github.com/users/{username}/events/public',
            timeout=10
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        if not isinstance(data, list):
            return []

        posts = []
        for event in data[:20]:
            posts.append({
                'id': f"github_{event.get('id', '')}",
                'source': 'github',
                'author': event.get('actor', {}).get('display_login', username),
                'title': f"[{event.get('type', 'Event')}] in {event.get('repo', {}).get('name', 'unknown')}",
                'content': (event.get('payload', {}).get('commits', [{}])[0].get('message', 'Activity event.')
                            if event.get('payload', {}).get('commits') else 'Activity event.'),
                'external_url': f"https://github.com/{event.get('repo', {}).get('name', '')}",
                'created_at': datetime.fromisoformat(event.get('created_at', '').replace('Z', '+00:00')),
                'post_type': 'project',
            })
        return posts
    except Exception:
        return []


def get_aggregated_feed(subreddits=None, github_users=None):
    """Merge external feeds, sorted chronologically."""
    all_posts = []

    for sub in (subreddits or ['programming']):
        all_posts.extend(fetch_reddit_feed(sub))

    for user in (github_users or []):
        all_posts.extend(fetch_github_feed(user))

    # Strict chronological order — no algorithm
    all_posts.sort(key=lambda p: p.get('created_at', datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
    return all_posts
