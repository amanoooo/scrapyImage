#coding=utf-8

import scrapy

from scrapyImage.items import ScrapyImageItem
from scrapy.selector import Selector

class Landscape(scrapy.Spider):
    name = "landscape"
    allowed_domains = ["win4000.com"]
    start_urls = [
        "http://www.win4000.com/zt/fengjing.html",
    ]
    # images = []

    def parse(self, response):
        mainSecector = response.xpath('//div[@class="Left_bar"]//div[@class="tab_box"]//ul//a')
        for sel in mainSecector:
            link = sel.xpath('./@href').extract()[0]
            title = sel.xpath('./@title').extract()[0]
            print 'link is', type(link), link, type(title), title
            yield scrapy.http.Request(link, callback=self.parse_detail)
        # link = mainSecector[0].xpath('./@href').extract()[0]
        # title = mainSecector[0].xpath('./@title').extract()[0]
        # print 'link is', type(link), link, type(title), title
        # yield scrapy.http.Request(link, callback=self.parse_detail)

    def parse_detail(self, response):
        category = response.xpath('//div[@class="breadcrumbs"]/span/text()').extract()[0]
        image = response.xpath('//img[@class="pic-large"]/@src').extract()
        nextPage = response.xpath('//div[@class="pic-next-img"]/a/@href').extract()[0]
        # print 'nextPage is ', nextPage
        # print 'category is ', category
        # print 'images is ', Landscape.images

        yield scrapy.http.Request(nextPage, callback=self.parseNextPage, meta={'category': category, 'images': image })


    def parseNextPage(self, response):
        category = response.meta['category']
        images = response.meta['images']
        nextCategory = response.xpath('//div[@class="breadcrumbs"]/span/text()').extract()[0]
        image = response.xpath('//img[@class="pic-large"]/@src').extract()
        newImages = images + image
        nextPage = response.xpath('//div[@class="pic-next-img"]/a/@href').extract()[0]
        print "catewgory is ", category, nextCategory
        if(category == nextCategory):
            yield scrapy.http.Request(nextPage, callback=self.parseNextPage, meta={'category': nextCategory,'images': newImages })
        else:
            item = ScrapyImageItem()
            # image 应为 1个长度的list
            item['image'] = newImages
            item['title'] = category
            yield item

