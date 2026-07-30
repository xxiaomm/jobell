import scrapy


class JobItem(scrapy.Item):
    company_slug = scrapy.Field()
    company_name = scrapy.Field()
    company_careers_url = scrapy.Field()
    ats_type = scrapy.Field()

    external_id = scrapy.Field()
    title = scrapy.Field()
    location = scrapy.Field()
    department = scrapy.Field()
    level = scrapy.Field()
    min_years_experience = scrapy.Field()
    degree_requirement = scrapy.Field()
    url = scrapy.Field()
    posted_at = scrapy.Field()
