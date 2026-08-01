import asyncio
import random
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import csv

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

class IndeedScraper:

    def __init__(self, j, l):
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.session = None
        self.data = {"q": j, "l": l}
        self.playwright = None
        self.browser = None


    async def start(self):
        self.session = aiohttp.ClientSession(headers=HEADERS)
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()
        await self.session.close()

    async def search(self):
        async with self.session.get(BASE_URL, params= self.data) as response:
            return str(response.url)


    async def fetch(self, url):

        print("Fetching", url)

        async with self.semaphore:
            for attempt in range(MAX_RETRIES):

                page = await self.browser.new_page()

                try:
                    await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                    response = await page.goto(url)
                    await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                    if response and response.status == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue

                    if response and response.status == 403:
                        print("Blocked:", url)
                        return None

                    html = await page.content()

                    if "Too Many Requests" not in html:
                        return html

                except Exception as e:
                    print(e)
                    await asyncio.sleep(2 ** attempt)

                finally:
                    await page.close()

            return None

    @staticmethod
    def parse_jobs(html):
        soup = BeautifulSoup(html, "html.parser")
        data = []

        jobs = soup.find_all("table", {"class": "mainContentTable"})
        for job in jobs:
            d = {}
            d["title"]= job.select_one("span[id^='jobTitle-']").text.strip()
            d["company"]= job.select_one("[data-testid='company-name']").text.strip()
            d["location"]= job.select_one("[data-testid='text-location']").text.strip()

            data.append(d)

        return data

    @staticmethod
    def find_urls(html):
        soup = BeautifulSoup(html, "html.parser")
        urls = []
        for i in range(2,6):
            url = soup.find("a", {"aria-label": str(i), "data-testid": f"pagination-page-{i}"})
            if url:
                urls.append(urljoin(BASE_URL,url["href"]))
            else:
                print(f"No url for Page {i}")

        return list(set(urls))

    async def scrape_jobs(self, url):
        html = await self.fetch(url)
        if html is None:
            print(f"No html for {url}")
            return []
        jobs = IndeedScraper.parse_jobs(html)

        return jobs


async def main():
    job = input("Write job title, keywords, or company:")
    location = input("Write location (City, state, zip code, or \"remote\":")

    scraper = IndeedScraper(job, location)
    await scraper.start()
    try:
        first_url = await scraper.search()
        html = await scraper.fetch(first_url)
        if html is None:
            print("No html found at all.")
        urls = scraper.find_urls(html)
        urls.insert(0, first_url)

        tasks = [
            scraper.scrape_jobs(url) for url in urls
        ]

        results = await asyncio.gather(*tasks)

        return results

    except Exception as e:
        print("Error:", e)

    finally:
        await scraper.close()

if __name__ == "__main__":
    scrapingResults = asyncio.run(main())
    with open("results.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Job Title", "Company", "Location"])

        for result in scrapingResults:
            for job in result:
                writer.writerow([job["title"], job["company"], job["location"]])