# 获取指定目的地的商品代码
import csv
import json

import requests

country = 'PK'
lang = 'EN'
class_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
url = 'http://ftatax.mofcom.gov.cn/wmsw/crossDomain/getCodeByFather'
res = {}


def get_code():
    # 通过一级分类获取二级分类
    for main_class in class_list:
        print('获取{}的二级分类'.format(main_class))
        class_url = 'http://ftatax.mofcom.gov.cn/wmsw/crossDomain/getCodeByCodeClass?codeClass={}'.format(
            main_class)
        response = requests.get(class_url)
        subclasses = json.loads(response.text.replace(' ', '').replace('jsonpcallback(', '')[:-1])
        # 通过二级分类获取商品代码
        for subclass in subclasses:
            find_child(*tuple(subclass[:3]))


def find_child(code, name, label):
    print('正在处理，编号{}，名称{}'.format(code, name))
    # 是商品编号则加入结果集
    if label == 'true':
        if res.get(code) is None:
            res[code] = name
        return
    # 不是商品编号，继续查找下级
    sub_url = url + '?queryType={}&hsCountry={}&fatherCode={}'.format(lang, country, code)
    response = requests.get(sub_url)
    subclasses = json.loads(response.text.replace(' ', '').replace('jsonpcallback(', '')[:-1])
    for subclass in subclasses:
        find_child(*tuple(subclass[:3]))


if __name__ == '__main__':
    get_code()
    print(res)
    filename = "{}_code_{}.csv".format(country, lang)
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['code', 'name'])
        for code, name in res.items():
            # 如果没有.分隔，手动添加
            if len(code.split('.')) <= 1:
                code = code[:4] + '.' + code[4:6] + '.' + code[6:]
            csv_writer.writerow([code, name])
