# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv

from itemadapter import ItemAdapter


class MofcomSpiderPipeline:
    def process_item(self, item, spider):
        with open(spider.output_file, 'a+', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow((item['code'], item['ec'], item['ic'], item['ct'], item['gt'], item['plan_text'],
                             item['plan_table'], item['ga'], item['sa']))
        return item
