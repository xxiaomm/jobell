# Jobell

Track new job postings from top companies in near real time — filter by title, level,
location, years of experience, degree requirement and post date, and get emailed when a
new job matches your saved filters.

## Stack

- **Frontend**: Next.js (TypeScript) + Tailwind CSS + shadcn/ui-style components — SSR for SEO on job listing/detail pages
- **Backend API**: FastAPI + SQLAlchemy + PostgreSQL (filtering, auth, subscriptions)
- **Scraper**: Scrapy (+ httpx-style direct JSON API calls where available, scrapy-playwright for JS-heavy/anti-bot sites)
- **Notifications**: Redis pub/sub → worker → SMTP email

## Layout

```
shared/     Python package shared by backend + scraper: DB models, DB session, redis client
backend/    FastAPI app (API + auth) and the notification worker (app/worker/notifier.py)
scraper/    Scrapy project; greenhouse_spider.py is a real, runnable example
frontend/   Next.js app
```

## Running locally

1. Copy the env file and adjust as needed:

   ```bash
   cp .env.example .env
   ```

2. Start the core services and database/queue:

   ```bash
   docker compose up -d postgres redis mailhog
   ```

3. Run migrations:

   ```bash
   docker compose run --rm backend alembic upgrade head
   ```

4. Start the API, notifier worker and frontend:

   ```bash
   docker compose up -d backend notifier frontend
   ```

5. Run a crawl (one-shot — not part of `docker compose up`; scheduling it periodically via
   cron/celery-beat is a follow-up, not included in this base scaffold). Note `--profile`
   goes before `run`, not after:

   ```bash
   docker compose --profile tools run --rm scraper
   ```

6. Open the app:

   - Frontend: http://localhost:3000
   - API docs (Swagger): http://localhost:8000/docs
   - MailHog (catches notification emails in dev): http://localhost:8025

Day to day, once `.env` and the DB schema exist, steps 2 and 4 collapse into one:

```bash
docker compose up -d
```

(`scraper` has `profiles: ["tools"]` so it's excluded from a plain `up` — trigger it with the
step 5 command whenever you want a fresh crawl.)

To stop everything:

```bash
docker compose down      # stop containers, keep DB data
docker compose down -v   # stop and also wipe the postgres volume
```

## Notification flow

`scraper` pipeline inserts a new `Job` row → publishes its id on the redis `new_jobs`
channel → `notifier` worker matches it against every user's `Subscription` filters → sends
an email via SMTP (MailHog locally) to each matching user.

## Adding another company to the scraper

- **Has a clean JSON API** (check devtools → Network → XHR/Fetch on the company's careers
  page first — most ATS-backed pages call one): add a plain `scrapy.Spider` that hits it
  directly, like `scraper/jobell_scraper/spiders/greenhouse_spider.py`.
- **No usable API / heavy anti-bot** (e.g. Workday): extend
  `scraper/jobell_scraper/playwright_base.py`'s `BasePlaywrightSpider`.
