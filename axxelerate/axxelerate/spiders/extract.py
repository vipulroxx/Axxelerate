from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.item import Item, Field
import modify_query

class url_item(Item):
    url= Field()
    keywords = Field()
    title = Field()
    linksTo = Field()

class axxelerate_spider(CrawlSpider):
    name = 'axxelerate'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Main_Page']
    rules = (Rule(LxmlLinkExtractor(allow=(allowed_domains)), callback='parse_obj', follow=True),)

    def parse_obj(self,response):
        item = url_item()
        item['url'] = response.url
        item['keywords'] = []
        tags = ["h1", "title", "article", "div", "blockquote", "td", "li", "p", "span", "strong", "b", "i"]
        for tag in tags:
            texts = response.xpath("//%s/text()" % (tag)).extract()
            for text in texts:
                text =  text.encode("latin1", "ignore")
                result = modify_query.query(text)
                item['keywords'] = item['keywords'] + result
        item['title'] = response.xpath("//title/text()").extract_first()
        item['keywords'] = set(item['keywords'])
        item['linksTo'] = []
        for link in LxmlLinkExtractor(allow=(),deny = ()).extract_links(response):
            if link.url.startswith('https://en.wikipedia.org'):
                item['linksTo'].append(link.url)
        return item
