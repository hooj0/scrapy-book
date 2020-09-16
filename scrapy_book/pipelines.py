# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse
from urllib.request import unquote
from os.path import basename, dirname, join
import scrapy


class ScrapyBookPipeline:

    def process_item(self, item, spider):

        return item


class DownloadImgPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        request = scrapy.Request(url=item['image'])
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
        # print("item: ", item)

        file_suffix = filename.split(".")[-1]
        full_name = "%s-%s.%s" % (item["author"], item["name"], file_suffix)
        full_path = join(item["folder"], item["category"], full_name)
        print("full_path: ", full_path)

        return full_path

    # 下载完成
    def item_completed(self, results, item, info):
        # 结果 True,{url path checksum}
        print(results)

        # process_item中的return item 作用一致
        return item


class DownloadFilePipeline(FilesPipeline):

    def get_media_requests(self, item, info):

        print("download: ", item['download_url'])
        yield scrapy.Request(url=item['download_url'])

    def file_path(self, request, response=None, info=None):

        path = urlparse(request.url).path
        print("path: ", path)

        # return '%s/%s' % (basename(dirname(path)), basename(path))
        return join(basename(dirname(path)), basename(path))

    def item_completed(self, results, item, info):
        print(results)
        return item