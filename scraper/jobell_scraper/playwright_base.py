"""Base class for spiders that target career sites with no usable JSON API
and/or heavy anti-bot protection (Workday, some custom SPAs). Before writing
one of these: open the target careers page in devtools -> Network -> XHR/
Fetch and check whether the page is actually calling a clean backend JSON
endpoint under the hood. If it is, write a plain `scrapy.Spider` that hits
that endpoint directly (see greenhouse_spider.py) instead - it will be
10-100x faster and cheaper than driving a full browser.

Use this base only when there truly is no API, or the site requires real
interaction / JS challenges to reach the job data.
"""
import abc

import scrapy


class BasePlaywrightSpider(scrapy.Spider, abc.ABC):
    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30_000,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_listing,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": self.page_methods(),
                },
            )

    async def start(self):
        # Scrapy >=2.13 calls start() instead of start_requests(); keep both
        # so subclasses also work on older Scrapy versions.
        for request in self.start_requests():
            yield request

    def page_methods(self) -> list:
        """Override to wait for/interact with dynamic content, e.g.:

        from scrapy_playwright.page import PageMethod
        return [PageMethod("wait_for_selector", ".job-list-item")]
        """
        return []

    @abc.abstractmethod
    def parse_listing(self, response: scrapy.http.Response):
        """Yield JobItem(s) from the rendered listing page. `response.meta["playwright_page"]`
        gives you the live Playwright Page if you need further interaction
        (pagination clicks, infinite scroll, etc.) - remember to `await page.close()`.
        """
        raise NotImplementedError
