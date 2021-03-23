import scrapy

from scrapy.loader import ItemLoader

from ..items import UbpItem
from itemloaders.processors import TakeFirst


class UbpSpider(scrapy.Spider):
	name = 'ubp'
	start_urls = ['https://www.ubp.com/en/sites/ubp/newsroom/pagecontent/ubp-news-automatic-boxes-list.js?contentTemplate=MainContent5&cat=&offset=0&rowCount=99999']

	def parse(self, response):
		data = scrapy.Selector(text=response.text)
		post_links = data.xpath('//p[@class="box-title"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "row-p", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//p//text()[normalize-space()] | //*[contains(concat( " ", @class, " " ), concat( " ", "notransi", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "col-xs-11", " " ))]//p//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "col-lg-14", " " ))]//span[@class="box-date"]/text()').get()

		item = ItemLoader(item=UbpItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
