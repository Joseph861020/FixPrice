import os
import re
import time
from typing import Optional, Union, Dict, Any, Generator

from dotenv import load_dotenv
import scrapy
from scrapy.http import HtmlResponse, TextResponse

from fix_price.items import FixPriceScrapyItem
from fix_price.settings import ALLOWED_DOMAINS, START_URLS

load_dotenv()


class FixPriceSpider(scrapy.Spider):
    name: str = "fix_price"
    allowed_domains: list[str] = ALLOWED_DOMAINS
    start_urls: list[str] = START_URLS

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """
        Отправляет начальные запросы на указанные URL-адреса с использованием прокси.

        :return: Генератор запросов Scrapy.
        """
        proxy_login = os.getenv("PROXY_LOGIN")
        proxy_password = os.getenv("PROXY_PASSWORD")
        proxy_ip = os.getenv("PROXY_IP")
        proxy_port = os.getenv("PROXY_PORT")
        proxy_url = f"http://{proxy_login}:{proxy_password}@{proxy_ip}:{proxy_port}"

        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"proxy": proxy_url}
            )

    def parse(self, response: Union[HtmlResponse, TextResponse]) -> None:
        """
        Обрабатывает HTML-ответ страницы и извлекает ссылки на страницы продуктов и страницы пагинации.

        :param response: Ответ Scrapy, который может быть HTML или текстом.
        """
        next_pages = response.css(".pagination.pagination a.number::attr(href)").extract()
        if not next_pages:
            self.logger.info('No pagination links found.')

        # Следуем за ссылками на страницы продуктов
        for href in response.css('a.title::attr(href)').extract():
            url = response.urljoin(href)
            yield response.follow(url, callback=self.parse_products)

        # Следуем за ссылками пагинации, если они есть
        for href in next_pages:
            url = response.urljoin(href)
            yield response.follow(url, callback=self.parse)

    def parse_products(self, response: Union[HtmlResponse, TextResponse], **kwargs: Any) -> None:
        """
        Извлекает информацию о продукте с страницы и формирует элементы данных для сохранения.

        :param response: Ответ Scrapy, который может быть HTML или текстом.
        :param kwargs: Дополнительные аргументы.
        """
        match = re.search(r"specialPrice:(\{.*?\})",
                          response.xpath("//script[contains(text(), 'specialPrice')]/text()").extract_first(''))
        special_price_value: Optional[str] = None
        if match:
            special_price_match = re.search(r'price:"([^"]+)"', match.group(1))
            if special_price_match:
                special_price_value = special_price_match.group(1)

        original_price_element = response.css("div.price-quantity-block > div > meta[itemprop='price']")
        original_price_value: Optional[str] = original_price_element.attrib["content"] if original_price_element else None
        original_price: Optional[float] = float(original_price_value) if original_price_value else None
        special_price: Optional[float] = float(special_price_value) if special_price_value else None

        sale_tag: Optional[str] = None
        if special_price and original_price:
            discount_percentage = ((original_price - special_price) / original_price) * 100
            sale_tag = f"Скидка {discount_percentage:.2f}%"

        metadata: Dict[str, str] = {"__description": response.css(".product-details .description::text").extract_first("").strip()}
        for prop_element in response.css("div.properties p.property"):
            key: Optional[str] = prop_element.css("span.title::text").extract_first()
            value: Optional[str] = prop_element.css("span.value::text").extract_first()
            if key and value:
                metadata[key] = value.strip()

        set_images: str = "div.product-images link[itemprop='contentUrl']::attr(href)"
        item: Dict[str, Any] = {
            "timestamp": int(time.time()),
            "RPC": response.css("span.value::text").extract_first(default="").strip(),
            "url": response.request.url,
            "title": response.css("h1.title::text").extract_first(default="").strip(),
            "brand": response.css(".properties p:nth-child(1) .value a::text").extract_first(default="").strip(),
            "marketing_tags": response.css("p.special-auth::text").extract_first(default=""),
            "section": [section.strip() for section in response.css("div.breadcrumbs span::text").extract() if
                        section.strip()],
            "price_data": {
                "current": special_price if special_price is not None else original_price,
                "original": original_price,
                "sale_tag": sale_tag
            },
            "assets": {
                "main_image": response.css("div.product-images img.normal::attr(src)").extract_first(default=""),
                "set_images": response.css(set_images).extract(),
                "view_zoom": response.css("div.product-images img.zoom::attr(src)").extract()
            },
            "metadata": metadata
        }
        yield FixPriceScrapyItem(item)
