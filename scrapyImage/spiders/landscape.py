#coding=utf-8

import scrapy

from scrapyImage.items import ScrapyImageItem
from scrapy.selector import Selector

class DmozSpider(scrapy.Spider):
    name = "landscape"
    allowed_domains = ["win4000.com"]
    start_urls = [
        "http://www.win4000.com/zt/fengjing.html",
    ]

    def parse(self, response):
        mainSecector = response.xpath('//div[@class="Left_bar"]//div[@class="tab_box"]//ul//a')
        for sel in mainSecector:
            link = sel.xpath('./@href').extract()[0]
            title = sel.xpath('./@title').extract()[0]
            print 'link is', type(link), link, type(title), title
            yield scrapy.http.Request(link, callback=self.parse_detail)

    def parse_detail(self, response):
        category = response.xpath('//div[@class="breadcrumbs"]/span/text()').extract()[0]
        image = response.xpath('//img[@class="pic-large"]/@src').extract()
        # print 'category is ', category
        # print 'image is ', image

        item = ScrapyImageItem()
        #  image 应为 1个长度的list
        item['image'] = image
        item['title'] = category
        print 'landscape item is ', item
        return item
