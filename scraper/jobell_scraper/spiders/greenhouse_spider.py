"""Spider for companies that use Greenhouse's public Job Board API
(https://developers.greenhouse.io/job-board.html) - the same JSON endpoint
their own career-page widgets call, so no browser/rendering is needed. This
is the "check devtools for a clean JSON API first" path; reach for
scrapy-playwright (see playwright_base.py) only when a target has no such
API.

Board tokens below are illustrative public examples; verify a company's
current token from their careers page (usually
boards.greenhouse.io/<token>) before relying on it.
"""
from datetime import datetime

import scrapy

from jobell_scraper.heuristics import guess_degree_requirement, guess_level, guess_min_years_experience
from jobell_scraper.items import JobItem

BOARDS = [
    {"slug": "stripe", "name": "Stripe", "careers_url": "https://stripe.com/jobs"},
    {"slug": "airbnb", "name": "Airbnb", "careers_url": "https://careers.airbnb.com"},
    {"slug": "notion", "name": "Notion", "careers_url": "https://www.notion.so/careers"},
]

API_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"


class GreenhouseSpider(scrapy.Spider):
    name = "greenhouse_spider"
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def start_requests(self):
        for board in BOARDS:
            yield scrapy.Request(
                API_URL.format(token=board["slug"]),
                callback=self.parse_board,
                cb_kwargs={"board": board},
                headers={"Accept": "application/json"},
            )

    async def start(self):
        # Scrapy >=2.13 calls start() instead of start_requests(); keep both
        # so this spider also works on older Scrapy versions.
        for request in self.start_requests():
            yield request

    def parse_board(self, response: scrapy.http.Response, board: dict):
        data = response.json()
        for job in data.get("jobs", []):
            content = job.get("content") or ""
            title = job.get("title", "")

            yield JobItem(
                company_slug=board["slug"],
                company_name=board["name"],
                company_careers_url=board["careers_url"],
                ats_type="greenhouse",
                external_id=str(job["id"]),
                title=title,
                location=(job.get("location") or {}).get("name"),
                department=", ".join(d["name"] for d in job.get("departments", []) if d.get("name")) or None,
                level=guess_level(title),
                min_years_experience=guess_min_years_experience(content),
                degree_requirement=guess_degree_requirement(content),
                url=job.get("absolute_url"),
                posted_at=self._parse_updated_at(job.get("updated_at")),
            )

    @staticmethod
    def _parse_updated_at(value: str | None):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
