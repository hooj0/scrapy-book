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
import logging
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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }

    logger = logging.getLogger(__name__)

    def parse(self, response):

        # for line in response.css('li.menu-item-object-category:not(li.menu-item-has-children)'):
        # for line in response.css('li.menu-item-object-category'):
        for line in response.css('li#menu-item-2197, li#menu-item-2197 li.menu-item-object-category'):
            queue = deque([])
            self.find_parent(line, queue)

            folder = "/".join(queue)
            category_url = line.css("a::attr(href)").get()
            category = line.css("a::text").get().replace("/", "、")

            if category_url is not None:
                request = scrapy.Request(category_url, headers=self.headers, callback=self.parse_book_list)
                request.cb_kwargs["book"] = {"folder": folder, "category": category, "category_url": category_url}

                yield request

            #break

    def parse_book_list(self, response, book):

        for article in response.css("article"):

            title_node = article.css("h2.entry-title a")
            detail_url = title_node.attrib["href"]
            title = title_node.css("::text").get()

            titles = self.get_book_name_author(title)
            print("title: ", title)

            item = ScrapyBookItem()

            item["folder"] = book["folder"]
            item["category"] = book["category"]
            item["category_url"] = book["category_url"]
            item["name"] = titles[0].strip().replace("《", "").replace("》", "").replace(":", "：")
            item["author"] = titles[1].strip().replace(":", "：")
            item["detail_url"] = detail_url
            item["image"] = article.css("a.post-thumbnail img::attr(src)").get()

            if detail_url is not None:
                request = scrapy.Request(detail_url, headers=self.headers, callback=self.parse_book_detail, dont_filter=True)
                request.cb_kwargs["item"] = item

                yield request

        next_page = response.css("nav.pagination a.next::attr(href)").get()
        if next_page is not None:
            print("next page:", next_page)
            request = scrapy.Request(next_page, headers=self.headers, callback=self.parse_book_list)
            request.cb_kwargs["book"] = book

            yield request

    def parse_book_detail(self, response, item):

        item["download_url"] = response.css("a.wp-block-button__link::attr(href)").get()
        yield item

    @staticmethod
    def split(title, key):

        titles = title.split(key + "：")
        if len(titles) != 2:
            titles = title.split(key + ":")
        if len(titles) != 2:
            titles = title.split(key + "")

        return titles

    def get_book_name_author(self, title):

        titles = self.split(title, "作者")
        if len(titles) != 2:
            titles = self.split(title, "主编")

        return titles

    def find_parent(self, selector, queue):
        node = selector.xpath("../..")
        text = node.xpath("a/text()").get()
        # text = node.css("a::text").get()

        if text != "书架":
            queue.appendleft(text)
            self.find_parent(node, queue)
