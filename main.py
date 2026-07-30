import asyncio
import random
import aiohttp

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
        self.session = aiohttp.ClientSession(
            headers = get_headers(),
        )
        self.data = {"q": j, "l": l}

    async def search(self):
        async with self.session.get(BASE_URL, params= self.data) as response:
            return str(response.url)


    async def fetch(self, url):

        async with self.semaphore:
            for attempt in range(MAX_RETRIES):
                try:
                    await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                    async with self.session.get(
                            url,
                            headers=self.headers,
                            timeout=aiohttp.ClientTimeout(
                                total=15
                            )
                    ) as response:
                        if response.status == 429:
                            retry_after = response.headers.get("Retry-After")

                            if retry_after:
                                wait = int(retry_after)
                            else:
                                wait = 2 ** attempt

                            await asyncio.sleep(wait)

                            continue

                        if response.status == 403:
                            return None

                        response.raise_for_status()

                        return await response.text()

                except Exception:
                    await asyncio.sleep(2 ** attempt)

            return None


if __name__ == "__main__":

    job = input("Write job title, keywords, or company:")
    location = input("Write location (City, state, zip code, or \"remote\":")

    scraper = IndeedScrapper(job, location)
    scraper.search()