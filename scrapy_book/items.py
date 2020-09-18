#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-12
# @copyright by hoojo @2020
# @changelog scrapy book item object


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


class ScrapyBookItem(scrapy.Item):
    # 目录
    folder = scrapy.Field()
    # 类别
    category = scrapy.Field()
    # 书名
    name = scrapy.Field()
    # 作者
    author = scrapy.Field()
    # 类别链接
    category_url = scrapy.Field()
    # 书籍链接
    detail_url = scrapy.Field()
    # 书籍封面
    image = scrapy.Field()
    # 下载链接
    download_url = scrapy.Field()
    # 书籍已下载
    file_downloaded = scrapy.Field()
    # 图片已下载
    img_downloaded = scrapy.Field()