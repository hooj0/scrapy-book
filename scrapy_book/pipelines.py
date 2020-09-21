#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-12
# @copyright by hoojo @2020
# @changelog scrapy book spider item pipeline class


# ===============================================================================
# 标题：scrapy book core code
# ===============================================================================
# 使用：利用 scrapy 框架爬取博客的书籍、图片进行去重下载
# -------------------------------------------------------------------------------
# 描述：对爬取书单实体对象，进行去重并下载对应的图片和mobi电子书，
# 对重复的文件进行去重保留目录最深的文件
# -------------------------------------------------------------------------------
from urllib.request import unquote
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse
from os.path import basename, dirname, join, abspath, exists
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem
import logging
import scrapy
import shutil
import os


# -------------------------------------------------------------------------------
# scrapy 框架item pipeline去重
# -------------------------------------------------------------------------------
class DuplicatesPipeline:

    download_img_pipeline = "scrapy_book.pipelines.DownloadImgPipeline"
    download_file_pipeline = "scrapy_book.pipelines.DownloadFilePipeline"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = get_project_settings()

        self.files_store = self.settings["FILES_STORE"]
        self.images_store = self.settings["IMAGES_STORE"]
        self.item_pipelines = self.settings["ITEM_PIPELINES"]
        self.images, self.books = self.files_name(dirname(self.files_store))

        self.logger.info("existed images: %s", self.images)
        self.logger.info("existed books: %s", self.books)

    def files_name(self, file_dir):
        images, books = {}, {}

        if file_dir is None or len(file_dir) == 0:
            raise scrapy.exceptions.NotConfigured("<<<<<<<file dir configuration is None!>>>>>>>>")

        for root, dirs, files in os.walk(file_dir):
            for file in files:
                self.logger.debug("find file: %s", file)

                suffix = os.path.splitext(file)[1]
                if suffix == ".jpg":
                    images[file] = join(root, file)
                elif suffix == ".mobi":
                    books[file] = join(root, file)

        return images, books

    def process_item(self, item, spider):
        img = get_full_name(item, "tmp.jpg")
        book = get_full_name(item, "tmp.mobi")

        img_full_path = join(self.images_store, get_full_path(item, img))
        book_full_path = join(self.files_store, get_full_path(item, book))

        if self.download_img_pipeline in self.item_pipelines and self.download_file_pipeline in self.item_pipelines:
            processed = False
            if img in self.images and book in self.books:
                self.move_file(self.images[img], img_full_path)
                self.move_file(self.books[book], book_full_path)
                raise DropItem("Duplicate item found: %s" % img)

            if img in self.images:
                self.move_file(self.images[img], img_full_path)
                item["img_downloaded"] = True
            else:
                self.images[img] = img_full_path
                processed = True

            if book in self.books:
                self.move_file(self.books[book], book_full_path)
                item["file_downloaded"] = True
            else:
                self.books[book] = book_full_path
                processed = True

            if processed:
                return item

        elif self.download_img_pipeline in self.item_pipelines:
            if img in self.images:
                self.move_file(self.images[img], img_full_path)
                raise DropItem("Duplicate item found: %s" % img)
            else:
                self.images[img] = img_full_path
                return item

        elif self.download_file_pipeline in self.item_pipelines:
            if book in self.books:
                self.move_file(self.books[book], book_full_path)
                raise DropItem("Duplicate item found: %s" % book)
            else:
                self.books[book] = book_full_path
                return item
        else:
            return item

    def move_file(self, existed_file, process_file):
        existed_file_abspath = abspath(existed_file)
        process_file_abspath = abspath(process_file)

        existed_file_level = existed_file_abspath.count("\\")
        process_file_level = process_file_abspath.count("\\")

        def move():
            if exists(existed_file_abspath):
                if not exists(abspath(dirname(process_file))):
                    os.makedirs(abspath(dirname(process_file)))

                shutil.move(existed_file_abspath, process_file_abspath)
                self.logger.debug("(%s) ====>> (%s)" % (existed_file, process_file))

        if existed_file_level < process_file_level:
            move()
        elif existed_file_level == process_file_level and existed_file_abspath < process_file_abspath:
            move()
        else:
            self.logger.debug("(%s) don't move: (%s)" % (existed_file, process_file))


# -------------------------------------------------------------------------------
# scrapy 框架item pipeline下载图片
# -------------------------------------------------------------------------------
class DownloadImgPipeline(ImagesPipeline):

    logger = logging.getLogger(__name__)

    def get_media_requests(self, item, info):
        if item.get("img_downloaded", False):
            return None
        self.logger.debug("download img: %s", unquote(item["image"]))

        # 获取目录层级，提取优先级
        full_path = join(item["folder"], item["category"])
        level = full_path.count("\\")

        # 设置优先级
        request = scrapy.Request(url=item["image"], priority=level)
        request.meta["item"] = item

        yield request

    # 用于指定被下载文件的路径
    def file_path(self, request, response=None, info=None):
        # 获取请求链接
        url = request.url
        # 获取去掉域名后的路径
        path = urlparse(url).path
        # 获取文件名称
        filename = basename(path)

        '''
        print("url: ", url)
        print("path: ", path)
        print("filename: ", filename)
        # 获取解码后的文件名
        print("filename unquote: ", unquote(filename))

        # 获取最后一个“/”后的名称
        print("basename: ", basename(path))
        # 获取去除文件名的完整路径
        print("dirname: ", dirname(path))
        # 获取路径的最后一个文件夹
        print("basename dirname: ", basename(dirname(path)))
        '''
        item = request.meta["item"]

        return get_full_path(item, filename)

    # 下载完成
    def item_completed(self, results, item, info):
        # 结果 True,{url path checksum}
        if len(results) > 0:
            self.logger.info(results)
        # process_item中的return item 作用一致
        return item


# -------------------------------------------------------------------------------
# scrapy 框架item pipeline下载文件
# -------------------------------------------------------------------------------
class DownloadFilePipeline(FilesPipeline):

    logger = logging.getLogger(__name__)

    def get_media_requests(self, item, info):
        if item.get("file_downloaded", False):
            return None
        self.logger.debug("download file: %s", item["download_url"])

        # 获取目录层级，提取优先级
        full_path = join(item["folder"], item["category"])
        level = full_path.count("\\")

        # 设置优先级
        request = scrapy.Request(url=item["download_url"], priority=level)
        request.meta["item"] = item

        yield request

    def file_path(self, request, response=None, info=None):
        item = request.meta["item"]

        return get_full_path(item, "tmp.mobi")

    def item_completed(self, results, item, info):
        if len(results) > 0:
            self.logger.info(results)
        return item


def get_full_name(item, filename):
    file_suffix = filename.split(".")[-1]
    full_name = "%s-%s.%s" % (item["author"], item["name"], file_suffix)

    return full_name


def get_full_path(item, filename):
    full_path = join(item["folder"], item["category"], get_full_name(item, filename))
    logging.debug("full path: %s", full_path)

    return full_path