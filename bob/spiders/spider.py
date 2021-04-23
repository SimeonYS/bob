import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BobItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'


class BobSpider(scrapy.Spider):
    name = 'bob'
    start_urls = ['https://www.bob.bt/media/']

    def parse(self, response):
        articles = response.xpath('//div[@class="col-md-12"]/p/b')
        for index in range(len(articles)):
            date = response.xpath(f'(//div[@class="col-md-12"]/p/b)[{index + 1}]/text()').get()
            date = re.findall(r'\w+\s\d+(?:th|nd|st|rd)\,\s\d+', date)
            post_links = response.xpath(f'(//a[contains(text(),"Read More..")])[{index + 1}]/@href').get()
            title = response.xpath(f'(//div[@class="col-md-12"]/p/b)[{index + 1}]/text()').get().split(', Posted ')[0]
            if not 'pdf' in post_links:
                yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date, title=title))

    def parse_post(self, response, date, title):
        content = response.xpath('//div[@class="entry-content"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=BobItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()
