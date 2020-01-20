import sys
import scrapy
from scrapy.crawler import CrawlerProcess

from crawltools.utils.arguments import Arguments
from crawltools.spider import Spider


def main(args: Arguments.parse.Namespace):
    process = CrawlerProcess(vars(args))

    process.crawl(Spider.get(args.command))
    process.start()


if __name__ == "__main__":
    main(Arguments())
