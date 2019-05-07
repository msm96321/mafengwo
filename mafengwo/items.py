# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CityItem(scrapy.Item):
    city_id = scrapy.Field()
    city_name = scrapy.Field()
    city_num = scrapy.Field()


class SpotItem(scrapy.Item):
    city_id = scrapy.Field()
    spot_id = scrapy.Field()
    spot_name = scrapy.Field()
    spot_desc = scrapy.Field()
    spot_phone = scrapy.Field()
    spot_traffic = scrapy.Field()
    spot_ticket = scrapy.Field()
    spot_open_time = scrapy.Field()
    spot_address = scrapy.Field()
    num = scrapy.Field()
    num1 = scrapy.Field()
    num2 = scrapy.Field()
    num3 = scrapy.Field()