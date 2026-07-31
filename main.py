import asyncio
import random
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE_URL = "https://pk.indeed.com/jobs"

MAX_CONCURRENT_REQUESTS = 3

MIN_DELAY = 1
MAX_DELAY = 3

MAX_RETRIES = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Upgrade-Insecure-Requests": "1",
}

class IndeedScrapper:

    def __init__(self, j, l):
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.session = None
        self.data = {"q": j, "l": l}


    async def start(self):
        self.session = aiohttp.ClientSession(headers=HEADERS)

    async def close(self):
        await self.session.close()

    async def search(self):
        async with self.session.get(BASE_URL, params= self.data) as response:
            return str(response.url)


    async def fetch(self, url):

        print("Fetching", url)

        async with self.semaphore:
            for attempt in range(MAX_RETRIES):

                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    page = await browser.new_page()

                    try:
                        await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                        response = await page.goto(url)
                        await page.wait_for_load_state("networkidle")

                        if response and response.status == 429:
                            await asyncio.sleep(2 ** attempt)
                            continue

                        if response and response.status == 403:
                            print("Blocked:", url)
                            return None

                        html = await page.content()
                        await browser.close()

                        if "Too Many Requests" not in html:
                            return html

                    except Exception as e:
                        print(e)
                        await asyncio.sleep(2 ** attempt)

            return None

    async def parse_jobs(self, html):
        soup = BeautifulSoup(html, "html.parser")
        data = []

        jobs = soup.find_all("table", {"class": "mainContentTable"})
        for job in jobs:
            d = {}
            d["title"]= job.select_one("span[id^='jobTitle-']").text.strip()
            d["company"]= job.select_one("[data-testid='company-name']").text.strip()
            d["location"]= job.select_one("[data-testid='text-location']").text.strip()

            data.append(d)

        print(data[0])
        return data




async def main():
    job = input("Write job title, keywords, or company:")
    location = input("Write location (City, state, zip code, or \"remote\":")

    scraper = IndeedScrapper(job, location)
    await scraper.start()
    try:
        url = await scraper.search()
        html = await scraper.fetch(url)
        await scraper.parse_jobs(html)

    except Exception as e:
        print("Error:", e)

    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())