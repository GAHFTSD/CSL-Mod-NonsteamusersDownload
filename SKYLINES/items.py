# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SkylinesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    modlink = scrapy.Field()
    modimg = scrapy.Field()
    modname = scrapy.Field()
    modattr = scrapy.Field()
    publishdate = scrapy.Field()
    upgradedate = scrapy.Field()
    downloadurl = scrapy.Field()
    filesize = scrapy.Field()
    steamlink = scrapy.Field()
    page  = scrapy.Field()

    pass