import asyncio
import random
import requests

BASE_URL = "https://pk.indeed.com/jobs"

MAX_CONCURRENT_REQUESTS = 3

MIN_DELAY = 1
MAX_DELAY = 3

MAX_RETRIES = 3

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

class IndeedScrapper:

    def __init__(self, j, l):
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.session = requests.Session()
        self.data = {"q": j, "l": l}
        self.headers = get_headers()

    def search(self):
        return self.session.get(
            BASE_URL,
            params=self.data,
            headers=self.headers
        ).url

if __name__ == "__main__":

    job = input("Write job title, keywords, or company:")
    location = input("Write location (City, state, zip code, or \"remote\":")

    scraper = IndeedScrapper(job, location)
    scraper.search()