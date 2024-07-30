BOT_NAME = "fix_price"

SPIDER_MODULES = ["fix_price.spiders"]
NEWSPIDER_MODULE = "fix_price.spiders"

ALLOWED_DOMAINS = ["fix-price.com"]
START_URLS = [
    "https://fix-price.com/catalog/kosmetika-i-gigiena/ukhod-za-polostyu-rta?sort=sold&page=1",
    "https://fix-price.com/catalog/igrushki/igrovye-nabory-nastolnye-igry?sort=sold&page=1",
    "https://fix-price.com/catalog/krasota-i-zdorove/dlya-tela?sort=sold&page=1"
]

ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    "fix_price.middlewares.CustomProxyMiddleware": 350,
}

# Adjust concurrency settings as needed
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

FEEDS = {
    'fix_price.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': None,
        'indent': 4,
        'overwrite': True,
    },
}

LOG_LEVEL = 'DEBUG'
