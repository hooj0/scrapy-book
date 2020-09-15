#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-12
# @copyright by hoojo @2020
# @changelog scrapy book spider core class


# ===============================================================================
# 标题：scrapy book core code
# ===============================================================================
# 使用：利用 scrapy 框架爬取博客的书籍
# -------------------------------------------------------------------------------
# 描述：爬取书单实体对象
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建 scrapy 框架生成爬虫书籍实体对象
# -------------------------------------------------------------------------------
import scrapy
from _collections import deque
from scrapy_book.items import ScrapyBookItem


class BookSpider(scrapy.Spider):

    """
    name: scrapy 唯一定位实例的属性，必须唯一
    allowed_domains：允许爬取的域名列表，不设置表示允许爬取所有
    start_urls：起始爬取列表
    start_requests：它就是从start_urls中读取链接，然后使用make_requests_from_url生成Request，
                    这就意味我们可以在start_requests方法中根据我们自己的需求往start_urls中写入
                    我们自定义的规律的链接

    parse：回调函数，处理response并返回处理后的数据和需要跟进的url
    log：打印日志信息
    closed：关闭spider
    """

    name = 'book'
    allowed_domains = ['bloogle.top']
    start_urls = ['http://bloogle.top/']

    def parse(self, response):

        for line in response.css('li.menu-item-object-category:not(li.menu-item-has-children)'):
            item = ScrapyBookItem()

            queue = deque([])
            self.find_parent(line, queue)
            print("folder: ", "/".join(queue))

            item["folder"] = "/".join(queue)
            item["category"] = line.css("a::text").get().replace("/", "、")
            item["link"] = line.css("a::attr(href)").get()

            yield item

    def find_parent(self, selector, queue):
        node = selector.xpath("../..")
        text = node.xpath("a/text()").get()
        # text = node.css("a::text").get()

        if text != "书架":
            queue.appendleft(text)
            self.find_parent(node, queue)
