import scrapy
import os


class DiarioLibreSpider(scrapy.Spider):

    name = 'diario_libre'
    allowed_domains = ['www.diariolibre.com']
    start_urls = ['http://www.diariolibre.com/']
    custom_settings = {
        'FEED_URI': '../../../news/diario_libre.json',
        'FEED_FORMAT': 'json',
        'MEMUSAGE_LIMIT_MB': 2048,
        'MEMUSAGE_NOTIFY_MAIL': ['kennylajara@gmail.com'],
        #'USER_AGENT': 'Dominoticias +(http://dominoticias.com/bot.txt)',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }


    def parse(self, response):

        # Delete file if exists
        if os.path.exists(self.custom_settings['FEED_FORMAT']):
            os.remove(self.custom_settings['FEED_FORMAT'])

        # XPath to links
        XPATH_LINKS_TO_ARTICLES = '//article//h2/parent::a[not(starts-with(@href, "/fotos/"))]/@href'
        XPATH_LINKS_TO_CATEGORIES = '//nav[@id="main-nav"]//ul[@class="parent-nav lst cf"]/li/div/a/@href'
        XPATH_LINKS_TO_TAGS = '//nav[@id="bottom-main-nav"]//div[@class="temas-dia"]/div[position()>1]//a/@href'

        # Links to arcticles found
        links = response.xpath(XPATH_LINKS_TO_ARTICLES).getall()
        for link in links:
            yield response.follow(link, callback=self.parse_news)

        # Links categories found
        links = response.xpath(XPATH_LINKS_TO_CATEGORIES).getall()
        for link in links:
            yield response.follow(link, callback=self.parse_section)

        # Links tags found
        links = response.xpath(XPATH_LINKS_TO_TAGS).getall()
        for link in links:
            yield response.follow(link, callback=self.parse_section)


    def parse_section(self, response):

        # XPath to links
        XPATH_LINKS_TO_ARTICLES = '//article//h2/parent::a[not(starts-with(@href, "/fotos/"))]/@href'

        # Follow links to "related news"
        links = response.xpath(XPATH_LINKS_TO_ARTICLES).getall()
        for link in links:
             yield response.follow(link, callback=self.parse_news)


    def parse_news(self, response):

        # XPath to important data 
        XPATH_TITLE = '//div[@id="notap1a-00"]//h1/span/text()'
        XPATH_SUMMARY = '//div[@id="notap1a-00"]//ul/li/text()'
        XPATH_BODY = '//div[@id="notap1a-01"]//div[@class="text"]/div[@class="paragraph"]/p'
        XPATH_AUTHOR = '//div[@id="notap1a-00"]//span[@class="author-date"]/a[1]/strong/text()'
        XPATH_PLACE = '//div[@id="notap1a-00"]//span[@class="author-date"]/a[2]/span/text()'
        XPATH_TIME = '//div[@id="notap1a-00"]//span[@class="author-date"]/time/text()'

        # Extracting data from XPath
        title = response.xpath(XPATH_TITLE).get()
        body = response.xpath(XPATH_BODY).getall()
        if title and len(body) > 0:
            summary = response.xpath(XPATH_SUMMARY).getall()
            author = response.xpath(XPATH_AUTHOR).get()
            place = response.xpath(XPATH_PLACE).get()
            time = response.xpath(XPATH_TIME).get()

            #Save article
            yield {
                'title': title,
                'summary': summary,
                'body': body,
                'author': author,
                'place': place,
                'time': time,
                'url': response.request.url,
            }
