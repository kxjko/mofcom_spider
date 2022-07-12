import json
from time import sleep

import requests
from bs4 import BeautifulSoup
from loguru import logger

max_retry = 5
wait_seconds = 1


def get_reporters(text):
    soup = BeautifulSoup(text, 'html.parser')
    div = soup.find('div', id='ctl00_ContentView_r')
    reporters = []
    for child in div.contents:
        if child.name == 'table':
            checkbox = child.find('input', type='checkbox')
            id = checkbox['id']
            for sibling in checkbox.next_siblings:
                if sibling.name == 'a':
                    name = sibling.string
            reporters.append({'id': id, 'name': name, 'children': []})
        if child.name == 'div':
            tds = child.find_all('td', class_='ctl00_ContentView_r_2')
            for td in tds:
                id = td.input['id']
                name = td.span.string
                reporters[-1]['children'].append({'id': id, 'name': name})

    return reporters


def get_reporter_id_by_nation(text, nation):
    soup = BeautifulSoup(text, 'html.parser')
    div = soup.find('div', id='ctl00_ContentView_r')
    reporter_ids = []
    for child in div.contents:
        if not reporter_ids and child.name == 'table':
            checkbox = child.find('input', type='checkbox')
            nation_id = checkbox['id']
            for sibling in checkbox.next_siblings:
                if sibling.name == 'a' and sibling.string == nation:
                    reporter_ids.append(nation_id)
                    nodes = div.find('div', id=nation_id.replace('CheckBox', 'Nodes'))
                    # nodes = child.next_sibling
                    # while nodes and nodes['id'] != nation_id.replace('CheckBox', 'Nodes'):
                    #     nodes = nodes.next_sibling
                    if nodes:
                        tds = nodes.find_all('td', class_='ctl00_ContentView_r_2')
                        for td in tds:
                            reporter_ids.append(td.input['id'])
                    break

    return reporter_ids


def get_products(text):
    soup = BeautifulSoup(text, 'html.parser')
    div = soup.find('div', id='ctl00_ContentView_p')
    products = []
    for child in div.contents:
        if child.name == 'table':
            checkbox = child.find('input', type='checkbox')
            id = checkbox['id']
            for sibling in checkbox.next_siblings:
                if sibling.name == 'a':
                    name = sibling.string
            products.append({'id': id, 'name': name})

    return products


# 请求失败时重试
def retry_request(*args, **kwargs):
    count = 0
    while count < max_retry:
        count += 1
        try:
            res = requests.request(*args, **kwargs)
            if res.status_code == 200:
                return res
        except Exception as e:
            if count >= max_retry:
                raise e
        logger.warning('请求失败，当前已尝试{}次，最多尝试{}次', count, max_retry)
        sleep(wait_seconds)
    raise RuntimeError(res.reason)


if __name__ == '__main__':
    with open('ReportersAndProducts.html', 'r', encoding='utf-8') as f:
        text = f.read()
        products = get_products(text)
        reporters = get_reporters(text)
        print(get_reporter_id_by_nation(text, 'Australia'))
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=4)
    with open('reporters.json', 'w', encoding='utf-8') as f:
        json.dump(reporters, f, indent=4)
