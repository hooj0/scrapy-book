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

# 存储抓取的数据
scrapy crawl book -o book.json
```

## 参考

`scrapy` 官方文档 https://docs.scrapy.org/en/latest/intro/tutorial.html