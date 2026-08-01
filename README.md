# Indeed Job Scraper

An asynchronous Python scraper that searches [Indeed](https://pk.indeed.com) for job listings by title/keyword and location, and exports the results (job title, company, and location) to a CSV file.

Built with `asyncio`, `aiohttp`, `playwright`, and `BeautifulSoup4`.

## Features

- Async, concurrency-limited scraping (via `asyncio.Semaphore`)
- Headless-browser page fetching with `playwright` for JS-rendered content
- Randomized delays between requests to reduce rate-limiting
- Automatic retries with exponential backoff on failures / `429 Too Many Requests`
- Detects and handles `403 Forbidden` (blocked) responses
- Scrapes multiple result pages (pages 2–5) in parallel
- Exports results to `results.csv`

## Requirements

- Python 3.8+
- Google Chrome/Chromium (installed automatically by Playwright)

## Installation

1. Clone or download this project.
2. Install the Python dependencies:

   ```bash
   pip install aiohttp beautifulsoup4 playwright
   ```

3. Install the Playwright browser binaries:

   ```bash
   playwright install chromium
   ```

## Usage

Run the script from the command line:

```bash
python scraper.py
```

You will be prompted for:

- **Job title, keywords, or company** — e.g. `python developer`
- **Location** — e.g. `Lahore`, a zip code, or `remote`

The scraper will:

1. Perform the initial search on Indeed.
2. Discover additional result pages (up to page 5).
3. Scrape job listings (title, company, location) from each page concurrently.
4. Save all results to `results.csv` in the project directory.

### Example output (`results.csv`)

| Job Title        | Company      | Location      |
|-------------------|-------------|---------------|
| Python Developer   | Acme Corp   | Lahore, Punjab |
| Backend Engineer   | Tech Solutions | Remote      |

## Configuration

These constants can be adjusted at the top of the script:

| Constant | Description | Default |
|---|---|---|
| `MAX_CONCURRENT_REQUESTS` | Max number of concurrent page fetches | `3` |
| `MIN_DELAY` / `MAX_DELAY` | Random delay range (seconds) between actions | `1` – `3` |
| `MAX_RETRIES` | Retry attempts per page on failure | `3` |
| `HEADERS` | HTTP headers used for requests (User-Agent, etc.) | See script |

## Notes & Limitations

- The browser is launched with `headless=False` by default, so a visible Chromium window will open during scraping. Set `headless=True` in `browser.py` inside `start()` if you'd prefer a headless run.
- Indeed's page structure (CSS selectors/classes) can change over time, which may break parsing (`parse_jobs`) — selectors may need periodic updates.
- Scraping is subject to Indeed's [Terms of Service](https://www.indeed.com/legal) and [robots.txt](https://pk.indeed.com/robots.txt). Use responsibly, at a reasonable request rate, and only for permitted purposes (e.g. personal job search, research with permission). You are responsible for ensuring your use complies with applicable terms and laws.
- Aggressive scraping may still result in IP blocking (`403`) or CAPTCHAs despite the built-in delays and retries.

## Project Structure

```
.
├── scraper.py       # Main scraper script
├── results.csv       # Generated after running the script
└── README.md
```

## License

This project is provided as-is for educational purposes.
