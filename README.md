# scrapy book
https://bloogle.top/ blog crawler, crawl e-book.

## 介绍

爬取博客电子书，按照博客的书单标签建立目录，下载当前标签下的电子书。

## 准备

- `python3.5.2+`
- `scrapy`

## 开始

如果没有安装`scrapy`需要先安装爬虫框架

### 安装环境

```shell
# 利用pip安装scrapy
pip install scrapy
```

如果没有错误安装成功后，即可开始下面的工作。

### 创建项目

```shell
cd worksapce
D:\worksapce>scrapy startproject scrapy_book
```

### 生成代码

`scrapy` 可以自动生成 `spider` 的代码，使用如下命令会在 `spider` 目录生成代码模板。

```shell
D:\work_private>cd scrapy_book
D:\work_private\scrapy_book>scrapy genspider book bloogle.top
```

## 使用

使用命令启动运行项目

```shell
# 使用命令行的方式分析网页，可以进行表达式测试
scrapy shell https://bloogle.top/

# 运行爬虫
scrapy crawl book

# 运行爬虫，存储抓取的数据
scrapy crawl book -o book.json

# 运行爬虫，存储抓取的数据，不分行存储
scrapy crawl book -o book.jl

# 处理存储中文编码
scrapy crawl book -o book.jl -s FEED_EXPORT_ENCODING=utf-8
```

## 清单

在执行爬虫下载图片文件时出现错误代码，如下：

```shell
    from PIL import Image
ModuleNotFoundError: No module named 'PIL'
```

解决办法安装 `pillow`

```shell
pip install pillow

# 已经安装过了，这时可以先卸载，获取最新的pillow
# 运行卸载命令:
pip uninstall pillow
```



## 参考

`scrapy` 官方文档 https://docs.scrapy.org/en/latest/intro/tutorial.html