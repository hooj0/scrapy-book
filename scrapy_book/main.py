#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-12
# @copyright by hoojo @2020
# @changelog scrapy book main class


# ===============================================================================
# 标题：scrapy book main func
# ===============================================================================
# 使用：利用 scrapy 框架爬取博客的书籍
# -------------------------------------------------------------------------------
# 描述：爬取书单入口函数
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建 scrapy 框架生成爬虫书籍实体对象
# -------------------------------------------------------------------------------
from scrapy.cmdline import execute


# execute(["scrapy", "crawl", "book", "-o", "book.jl"])
execute("scrapy crawl book".split(" "))
#execute("scrapy crawl rename -o rename.jl".split(" "))