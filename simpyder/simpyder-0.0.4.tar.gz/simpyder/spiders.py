# coding=utf-8
from time import sleep
import threading
import queue
import logging
import requests
from lxml.etree import HTML
import datetime
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}


def get_logger(name, level='INFO'):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s @ %(name)s: %(message)s'))
    logger.setLevel(level)
    ch.setLevel(level)
    logger.addHandler(ch)
    logger.critical("线程启动")
    return logger


class Spider():

    def gen_url(self):
        self.except_queue.put('未实现方法: gen_url()，无法开启爬虫任务。')
        yield None

    def get_response(self, url):
        response = requests.get(url, headers=headers)
        if 'html' in response.headers['content-type']:
            response.xpath = HTML(response.text).xpath
        return response

    def parse(response):
        self.logger.critical('未实现方法: parse(response)，将直接返回Response对象')
        return response

    def save(self, item):
        self.logger.critical('未实现方法: save(item)，将直接打印爬取内容。')
        print(item)

    def run_save(self):
        logger = get_logger("{} - 子线程 - SAVE".format(self.name), 'INFO')
        while True:
            if not self.item_queue.empty():
                self.save(self.item_queue.get())
                self.meta['count'] += 1
            else:
                sleep(0.1)

    def assemble(self, gen_url=None, parse=None, save=None):
        if gen_url != None:
            self.gen_url = gen_url
        if parse != None:
            self.parse = parse
        if save != None:
            self.save = save
        pass

    def __init__(self, gen_url=None, parse=None, save=None, name="My Spider"):
        self.name = name
        self.assemble(gen_url, parse, save)
        self.QUEUE_LEN = 1000
        self.PARSE_THREAD_NUMER = 8
        self.url_queue = queue.Queue(self.QUEUE_LEN)
        self.item_queue = queue.Queue(self.QUEUE_LEN)
        self.except_queue = queue.Queue(1)
        self.queueLock = threading.Lock()
        self.threads = []
        self.logger = get_logger("{} - 主线程".format(name))

    def get_info(self):
        log = get_logger("{} - 子线程 - INFO".format(self.name), 'INFO')
        history = []
        interval = 5
        while True:
            c_time = datetime.datetime.now()
            history.append((c_time, self.meta['count']))
            if len(history) > 60 / interval:
                history = history[-12:]
            if (c_time - self.meta['start_time']).total_seconds() % interval < 1 and len(history) > 1:
                delta = (history[-1][1] - history[0][1]) * 60 / \
                    (history[-1][0] - history[0][0]).total_seconds()
                log.info(
                    "正在爬取第 {} 个链接，({}/min)".format(self.meta['count'], int(delta)))
            sleep(1)

    def run(self):
        meta = {'count': 0}
        start_time = datetime.datetime.now()
        meta['start_time'] = start_time
        self.meta = meta
        info_thread = threading.Thread(target=self.get_info, name="状态打印线程")
        info_thread.setDaemon(True)
        info_thread.start()
        save_thread = threading.Thread(target=self.run_save, name="保存项目线程")
        save_thread.setDaemon(True)
        save_thread.start()
        for i in range(self.PARSE_THREAD_NUMER):
            self.threads.append(self.ParseThread('{} - 子线程 - No.{}'.format(self.name, i), self.url_queue, self.queueLock,
                                                 self.get_response, self.parse, self.save, self.except_queue, self.item_queue, meta))
        for each_thread in self.threads:
            each_thread.setDaemon(True)
            each_thread.start()
        url_gener = self.gen_url()
        for each_url in url_gener:
            # self.queueLock.acquire()
            if (self.url_queue.full()):
                # self.queueLock.release()
                sleep(0.1)
            else:
                self.url_queue.put(each_url)
                # self.queueLock.release()

        while self.url_queue.empty() == False:
            if self.except_queue.empty() == False:
                except_info = self.except_queue.get()
                self.logger = get_logger(self.NAME)
                self.logger.error(except_info)
                # for each_thread in self.threads:
                #     each_thread.join()
                break
            pass
            sleep(1)
        self.logger.critical("爬取完毕")
        self.logger.critical("合计爬取项目数：{}".format(meta["count"]))

    class ParseThread(threading.Thread):
        def __init__(self, name, url_queue, queueLock, get_response, parse, save, except_queue, item_queue, meta):
            threading.Thread.__init__(self, target=self.run)
            self.name = name
            self.url_queue = url_queue
            self.queueLock = queueLock
            self.get_response = get_response
            self.parse = parse
            self.save = save
            self.item_queue = item_queue
            self.except_queue = except_queue
            self.logger = get_logger(self.name)
            self.meta = meta

        def run(self):
            while True:
                try:
                    self.queueLock.acquire()
                    if not self.url_queue.empty():
                        url = self.url_queue.get()
                    else:
                        url = None
                    self.queueLock.release()

                    if url == None:
                        sleep(1)
                        continue
                    self.logger.debug("开始爬取 {}".format(url))

                    response = self.get_response(url)
                    item = self.parse(response)
                    self.item_queue.put(item)

                    datetime.timedelta(1)
                except NotImplementedError as e:
                    self.logger.error(e)
                    return
                except Exception as e:
                    self.logger.error(e)
