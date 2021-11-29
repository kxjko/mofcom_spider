import csv

import scrapy
from scrapy import Selector

from mofcom_spider.items import FtaSpiderItem


class FtaSpider(scrapy.Spider):
    name = 'fta'
    allowed_domains = ['ftatax.mofcom.gov.cn']
    base_url = 'http://ftatax.mofcom.gov.cn/wmsw/searchFta'
    start_urls = []
    output_file = 'fta.py'

    def __init__(self, ec='CN', ic='SG', hc=None, output_file='fta.py', *args, **kwargs):
        super(FtaSpider, self).__init__(*args, **kwargs)
        self.output_file = output_file
        if not hc:
            code = '0101.21.00'
            self.start_urls.append(self.base_url + '?ec={}&ic={}&hc={}'.format(ec, ic, code))
        else:
            with open(hc, 'r', encoding='utf-8') as f:
                next(f)
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    self.start_urls.append(self.base_url + '?ec={}&ic={}&hc={}'.format(ec, ic, line[0]))

    def parse(self, response):
        def get_text(label):
            res = ''
            for text in label.xpath('text()').extract():
                res += text.strip()
            return res.strip()

        item = FtaSpiderItem()
        selector = Selector(response)
        # 原产地&目的地
        countries = selector.xpath('//section[@class="tol serachF1"]/p')
        item['ec'] = get_text(countries[0])[4:]
        item['ic'] = get_text(countries[1])[4:]
        # 编码
        code = selector.xpath('//section[@class="tol S_result"]//i')
        item['code'] = get_text(code[-1])[:-1]
        # 协定税率&普通税率
        taxes = selector.xpath('//ul[@class="word1 pl40p pt10"]/li')
        item['ct'] = get_text(taxes[0].xpath('span'))
        item['gt'] = get_text(taxes[1])
        # 降税安排
        plan = selector.xpath('//div[@class="fl left1 tol"]')
        item['plan_text'] = get_text(plan)
        plan_table = []
        for line in plan.xpath('table/tr'):
            plan_line = []
            for cell in line.xpath('*'):
                plan_line.append(get_text(cell))
            plan_table.append(plan_line)
        item['plan_table'] = plan_table
        # 原产地判定
        areas = selector.xpath('//section[@class="con"]/p')
        item['ga'] = get_text(areas[0])
        item['sa'] = get_text(areas[1])

        yield item
