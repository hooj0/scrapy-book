# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from urllib.request import unquote
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse
from os.path import basename, dirname, join, abspath
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem
import logging
import scrapy
import shutil
import os


class DuplicatesPipeline:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = get_project_settings()

        self.files_store = self.settings["FILES_STORE"]
        self.images_store = self.settings["IMAGES_STORE"]
        self.images, self.books = self.files_name(dirname(self.files_store))

        self.logger.info("existed images: %s", self.images)
        self.logger.info("existed books: %s", self.books)

    def files_name(self, file_dir):
        images, books = {}, {}

        for root, dirs, files in os.walk(file_dir):
            for file in files:
                self.logger.debug("find file: %s", file)

                if os.path.splitext(file)[1] == '.jpg':
                    images[file] = join(root, file)
                elif os.path.splitext(file)[1] == '.mobi':
                    books[file] = join(root, file)

        return images, books

    def process_item(self, item, spider):
        img = get_full_name(item, "tmp.jpg")
        book = get_full_name(item, "tmp.mobi")

        img_full_path = join(self.images_store, get_full_path(item, img))
        book_full_path = join(self.files_store, get_full_path(item, book))

        if img in self.images:
            self.move_file(self.images[img], img_full_path)
            raise DropItem("Duplicate img item found: %r" % img)
        elif book in self.books:
            self.move_file(self.books[book], book_full_path)
            raise DropItem("Duplicate book item found: %r" % book)
        else:
            self.images[img] = img_full_path
            self.books[book] = book_full_path
            return item

    def move_file(self, existed_file, process_file):

        existed_file_level = abspath(existed_file).count("\\")
        process_file_level = abspath(process_file).count("\\")

        if existed_file_level < process_file_level:
            shutil.move(abspath(existed_file), abspath(process_file))
            self.logger.info("(%s) ====>>>> (%s)" % (existed_file, process_file))
        else:
            self.logger.info("(%s) dont move: (%s)" % (existed_file, process_file))


class DownloadImgPipeline(ImagesPipeline):

    logger = logging.getLogger(__name__)

    def get_media_requests(self, item, info):
        # 获取目录层级，提取优先级
        full_path = join(item["folder"], item["category"])
        level = full_path.count("\\")

        # 设置优先级
        request = scrapy.Request(url=item['image'], priority=level)
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
        self.logger.info(results)

        # process_item中的return item 作用一致
        return item


class DownloadFilePipeline(FilesPipeline):

    logger = logging.getLogger(__name__)

    def get_media_requests(self, item, info):
        print("download: ", item['download_url'])

        request = scrapy.Request(item['download_url'])
        request.meta["item"] = item

        yield request

    def file_path(self, request, response=None, info=None):
        item = request.meta["item"]

        return get_full_path(item, "tmp.mobi")

    def item_completed(self, results, item, info):
        self.logger.info(results)(results)

        return item


def get_full_name(item, filename):
    file_suffix = filename.split(".")[-1]
    full_name = "%s-%s.%s" % (item["author"], item["name"], file_suffix)

    return full_name


def get_full_path(item, filename):
    full_path = join(item["folder"], item["category"], get_full_name(item, filename))

    logging.debug("full path: %s", full_path)
    return full_path