import scrapy
from typing import Dict, Any, List


class FixPriceScrapyItem(scrapy.Item):
    """
    Класс для хранения данных о продукте в формате Scrapy Item.
    """

    timestamp: scrapy.Field[Dict[str, Any]] = scrapy.Field()
    RPC: scrapy.Field[str] = scrapy.Field()
    url: scrapy.Field[str] = scrapy.Field()
    title: scrapy.Field[str] = scrapy.Field()
    brand: scrapy.Field[str] = scrapy.Field()
    marketing_tags: scrapy.Field[str] = scrapy.Field()
    section: scrapy.Field[List[str]] = scrapy.Field()
    price_data: scrapy.Field[Dict[str, Any]] = scrapy.Field()
    assets: scrapy.Field[Dict[str, Any]] = scrapy.Field()
    metadata: scrapy.Field[Dict[str, str]] = scrapy.Field()
