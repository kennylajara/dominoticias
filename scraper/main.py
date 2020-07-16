import requests, os, datetime
import lxml.html as html
from urllib.parse import urljoin as rel2abs


HOME_URL = 'https://www.diariolibre.com/'

XPATH_LINKS_HOLE_TO_ARTICLES = '//article//h2/parent::a[not(starts-with(@href, "/fotos/"))]/@href'
XPATH_TITLE = '//div[@id="notap1a-00"]//h1/span/text()'
XPATH_SUMMARY = '//div[@id="notap1a-00"]//ul/li/text()'
XPATH_BODY = '//normalize-space(div[@id="notap1a-01"]//div[@class="text"]/div[@class="paragraph"]/p)'
XPATH_AUTHOR = '//div[@id="notap1a-00"]//span[@class="author-date"]/a[1]/strong/text()'
XPATH_PLACE = '//div[@id="notap1a-00"]//span[@class="author-date"]/a[2]/span/text()'
XPATH_TIME = '//div[@id="notap1a-00"]//span[@class="author-date"]/time/text()'
XPATH_LINKS_ARTICLE_RELATED_NEWS = '//div[@id="notap1a-01"]//div[contains(@class, "Nota_incrustada")]//blockquote/a[not(starts-with(@href, "/fotos/"))]/@href'
XPATH_LINKS_ARTICLE_MORE_NEWS = '//div[@id="notap1-ml"]//h2/parent::a[not(starts-with(@href, "/fotos/"))]/@href'


def parse_news(link, news_dir):
    print(f'Crawling: {rel2abs(HOME_URL, link)}')
    try:
        response = requests.get(rel2abs(HOME_URL, link))
        if response.status_code == 200:
            news = response.content.decode('utf-8')
            parsed = html.fromstring(news)

            try:
                title = parsed.xpath(XPATH_TITLE)[0]
                summary = parsed.xpath(XPATH_SUMMARY)
                body = parsed.xpath(XPATH_BODY)
                author = parsed.xpath(XPATH_AUTHOR)[0]
                place = parsed.xpath(XPATH_PLACE)[0]
                time = parsed.xpath(XPATH_TIME)[0]
            except IndexError:
                return

            file_name = link.replace(HOME_URL, '').replace('/', '-').strip("-")
            with open(f'{news_dir}/{file_name}.txt', 'w+', encoding='utf-8') as file:
                file.write(title)
                file.write('\n\n')
                file.write(f'{place}, {time} - {author}')
                file.write('\n\n')
                for line in summary:
                    file.write(f'• {line}')
                    file.write('\n\n')
                file.write('\n')
                for line in body:
                    file.write(line)
                    file.write('\n\n')
                file.write('\n')
        else:
            raise ValueError(f'Error: Status code {response.status_code}')
    except ValueError as ve:
        print(ve)


def parse_home():
    print(f'Crawling: {HOME_URL}')
    try:
        response = requests.get(HOME_URL)
        if response.status_code == 200:
            home = response.content.decode('utf-8') # Decode HTML content
            parsed = html.fromstring(home)  # Parsed home
            links_to_news = parsed.xpath(XPATH_LINKS_HOLE_TO_ARTICLES)

            # for link_to_news in links_to_news:
            #     print(rel2abs(HOME_URL, link_to_news))

            today = datetime.date.today().strftime('%Y%m%d')
            news_dir = f'../news/{today}'

            if not os.path.isdir(news_dir):
                os.mkdir(news_dir)

            for link_to_news in links_to_news:
                parse_news(link_to_news, news_dir)

        else:
            raise ValueError(f'Error: Status code {response.status_code}')
    except ValueError as ve:
        print(ve)


def run():
    parse_home()


if __name__ == "__main__":
    run()