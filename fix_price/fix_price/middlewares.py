import os
from typing import Generator, Optional, Any
from dotenv import load_dotenv
from scrapy import signals
from scrapy.http import Request, Response

load_dotenv()


class FixPriceScrapySpiderMiddleware:
    """
    Промежуточное ПО для обработки запросов и ответов от паука Scrapy.
    """

    @classmethod
    def from_crawler(cls, crawler) -> 'FixPriceScrapySpiderMiddleware':
        """
        Создает экземпляр промежуточного ПО из объекта Crawler.

        :param crawler: Объект Crawler.
        :return: Экземпляр промежуточного ПО.
        """
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response: Response, spider: Any) -> Optional[Generator]:
        """
        Обрабатывает входящие ответы от паука.

        :param response: Ответ Scrapy.
        :param spider: Экземпляр паука.
        :return: Генератор или None.
        """
        return None

    def process_spider_output(self, response: Response, result: Any, spider: Any) -> Generator:
        """
        Обрабатывает выходные данные от паука.

        :param response: Ответ Scrapy.
        :param result: Результаты обработки.
        :param spider: Экземпляр паука.
        :return: Генератор результатов.
        """
        for i in result:
            yield i

    def process_spider_exception(self, response: Response, exception: Exception, spider: Any) -> Optional[Generator]:
        """
        Обрабатывает исключения, возникшие в процессе работы паука.

        :param response: Ответ Scrapy.
        :param exception: Исключение, которое было выброшено.
        :param spider: Экземпляр паука.
        :return: Генератор или None.
        """
        spider.logger.error(f"Spider error: {exception}")

    def process_start_requests(self, start_requests: Generator[Request, None, None], spider: Any) -> Generator[Request, None, None]:
        """
        Обрабатывает начальные запросы от паука.

        :param start_requests: Начальные запросы.
        :param spider: Экземпляр паука.
        :return: Генератор запросов.
        """
        for r in start_requests:
            yield r

    def spider_opened(self, spider: Any) -> None:
        """
        Логирует информацию о том, что паук был открыт.

        :param spider: Экземпляр паука.
        """
        spider.logger.info(f"Spider opened: {spider.name}")


class FixPriceScrapyDownloaderMiddleware:
    """
    Промежуточное ПО для обработки запросов и ответов от загрузчика Scrapy.
    """

    @classmethod
    def from_crawler(cls, crawler) -> 'FixPriceScrapyDownloaderMiddleware':
        """
        Создает экземпляр промежуточного ПО из объекта Crawler.

        :param crawler: Объект Crawler.
        :return: Экземпляр промежуточного ПО.
        """
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request: Request, spider: Any) -> Optional[Request]:
        """
        Обрабатывает входящие запросы от загрузчика.

        :param request: Запрос Scrapy.
        :param spider: Экземпляр паука.
        :return: Запрос или None.
        """
        return None

    def process_response(self, request: Request, response: Response, spider: Any) -> Response:
        """
        Обрабатывает ответы от загрузчика.

        :param request: Запрос Scrapy.
        :param response: Ответ Scrapy.
        :param spider: Экземпляр паука.
        :return: Ответ Scrapy.
        """
        return response

    def process_exception(self, request: Request, exception: Exception, spider: Any) -> Optional[Response]:
        """
        Обрабатывает исключения, возникшие в процессе обработки запросов.

        :param request: Запрос Scrapy.
        :param exception: Исключение, которое было выброшено.
        :param spider: Экземпляр паука.
        :return: Ответ Scrapy или None.
        """
        spider.logger.error(f"Downloader error: {exception}")
        return None

    def spider_opened(self, spider: Any) -> None:
        """
        Логирует информацию о том, что паук был открыт.

        :param spider: Экземпляр паука.
        """
        spider.logger.info(f"Spider opened: {spider.name}")


class CustomProxyMiddleware:
    """
    Промежуточное ПО для обработки запросов с использованием прокси.
    """

    def __init__(self) -> None:
        """
        Инициализирует прокси-сервер из переменных окружения.
        """
        proxy_login = os.getenv("PROXY_LOGIN")
        proxy_password = os.getenv("PROXY_PASSWORD")
        proxy_ip = os.getenv("PROXY_IP")
        proxy_port = os.getenv("PROXY_PORT")
        proxy_url = f"http://{proxy_login}:{proxy_password}@{proxy_ip}:{proxy_port}"
        self.proxy: str = proxy_url

    def process_request(self, request: Request, spider: Any) -> None:
        """
        Устанавливает прокси для запроса, если он еще не установлен.

        :param request: Запрос Scrapy.
        :param spider: Экземпляр паука.
        """
        if 'proxy' not in request.meta:
            request.meta['proxy'] = self.proxy

    def get_proxy(self) -> str:
        """
        Возвращает URL прокси-сервера.

        :return: URL прокси-сервера.
        """
        return self.proxy
