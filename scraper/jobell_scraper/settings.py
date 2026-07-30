BOT_NAME = "jobell_scraper"

SPIDER_MODULES = ["jobell_scraper.spiders"]
NEWSPIDER_MODULE = "jobell_scraper.spiders"

# boards-api.greenhouse.io is Greenhouse's officially documented public Job
# Board API (the same endpoint career-page embed widgets call), not a page
# scrape - so it's fine to hit directly without honoring robots.txt here.
# Flip this back to True for any spider that crawls a company's own site.
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.5

ITEM_PIPELINES = {
    "jobell_scraper.pipelines.JobPersistencePipeline": 300,
}

# Spiders that need a real browser (scrapy-playwright) opt in per-request via
# meta={"playwright": True}; see playwright_base.py.
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
LOG_LEVEL = "INFO"
