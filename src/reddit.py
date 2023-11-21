from requests import get


class Reddit:
  USER_AGENT = "YetAnotherContentThief by /u/RoutineParfait3943"

  def get_post(self, sub_reddit: str, time: str = 'yesterday', limit: int = 10):
    response = get(
        f"https://www.reddit.com/r/{sub_reddit}/top.json?t={time}&limit={limit}",
        headers={"User-Agent": self.USER_AGENT}
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