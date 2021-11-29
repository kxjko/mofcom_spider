# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MofcomSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class FtaSpiderItem(scrapy.Item):
    code = scrapy.Field()
    ec = scrapy.Field()
    ic = scrapy.Field()
    ct = scrapy.Field()
    gt = scrapy.Field()
    plan_text = scrapy.Field()
    plan_table = scrapy.Field()
    ga = scrapy.Field()
    sa = scrapy.Field()
