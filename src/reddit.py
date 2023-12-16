from requests import get
import praw

class Reddit:
  def get_posts_from_json(self, sub_reddit: str, time: str = 'yesterday', limit: int = 10):
    USER_AGENT = "YetAnotherContentThief by /u/RoutineParfait3943"
    response = get(
        f"https://www.reddit.com/r/{sub_reddit}/top.json?t={time}&limit={limit}",
        headers={"User-Agent": USER_AGENT}
    )
    if not response.ok:
      raise Exception("Scrape posts Reddit error")

    results = []
    for post in response.json()["data"]["children"]:
      post = post["data"]
      results.append({
          'id': post['id'],
          'url': post['url'],
          'selftext': post['selftext'],
          'title': post['title'],
      })
    return results
    
  def get_posts_from_api(self, client_id: str, client_secret: str, sub_reddit: str, time: str = 'day', limit: int = 10):
    reddit = praw.Reddit(
      client_id=client_id,
      client_secret=client_secret,
      user_agent="YetAnotherContentThief by /u/RoutineParfait3943",
      check_for_async=False,
    )

    results = []
    for post in reddit.subreddit(sub_reddit).top(time_filter=time, limit=limit):
      results.append({
          'id': post.id,
          'url': post.url,
          'selftext': post.selftext,
          'title': post.title,
      })
    return results