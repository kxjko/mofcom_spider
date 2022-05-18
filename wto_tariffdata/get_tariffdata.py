import os.path
from time import sleep

from bs4 import BeautifulSoup
from loguru import logger

from wto_tariffdata.utils import get_reporters, get_products, retry_request

logger.add("log/{time}.log")

url_prefix = 'http://tariffdata.wto.org/'
select_url = url_prefix + 'ReportersAndProducts.aspx'
download_page_url = url_prefix + 'TariffList.aspx'
download_url = url_prefix + 'DownloadFile.aspx'

# 要查询的国家
nations = ['Australia', 'Brunei Darussalam', 'Cambodia', 'Chile', 'China',
           'Costa Rica', 'Iceland', 'Indonesia''Korea, Republic of', "Lao People's Democratic Republic",
           'Malaysia', 'Malaysia', 'New Zealand', 'Peru', 'Philippines',
           'Singapore', 'Switzerland', 'Thailand', 'Viet Nam']
# 要查询的年份
years = [y for y in range(2021, 1995, -1)]
# 产品分成的部分的数量
part_count = 2
# 文件保存路径
download_path = 'data'
zip_path = os.path.join(download_path, 'zip')
xls_path = os.path.join(download_path, 'xls')

with open('ReportersAndProducts.html', 'r', encoding='utf-8') as f:
    text = f.read()
    products = get_products(text)
    reporters = get_reporters(text)


def get_viewstate(text):
    soup = BeautifulSoup(text, 'html.parser')
    viewstate = soup.find('input', id='__VIEWSTATE')['value']
    viewstate_generator = soup.find('input', id='__VIEWSTATEGENERATOR')['value']
    return viewstate, viewstate_generator


def get_tariff():
    failures = []
    for nation in nations:
        logger.info('开始获取国家：{}的数据', nation)
        for year in years:
            try:
                logger.info('开始获取{}年的数据', year)
                # 请求勾选页面
                logger.info('开始获取cookies，GET:{}', select_url)
                res = retry_request('get', select_url)
                cookies = res.cookies
                logger.info('获取cookies成功！{}', cookies)
                viewstate, viewstate_generator = get_viewstate(res.text)

                # 选择年份
                logger.info('开始设置要查询的年份，POST:{}', select_url)
                params = {'__VIEWSTATE': viewstate,
                          '__VIEWSTATEGENERATOR': viewstate_generator,
                          'ctl00$ScriptManager1': 'ctl00$ScriptManager1|ctl00$ContentView$OkButton',
                          'ctl00$ContentView$OkButton': 'OK',
                          'ctl00$ContentView$CheckBoxNonMfn': 'on',  # 勾选Include non-MFN tariffs
                          'ctl00$ContentView$rbListIdb': 3,  # 选择特定年份
                          'ctl00$ContentView$DropDownListYears': year,
                          'ctl00$ContentView$CheckBoxCTS': 'on'  # 勾选Include bound tariffs
                          }
                # 保存筛选器
                res = retry_request('post', select_url, data=params, cookies=cookies)
                logger.info('设置要查询的年份成功！设置的年份为{}', year)
                viewstate, viewstate_generator = get_viewstate(res.text)

                # 勾选Reporters
                logger.info('开始设置要查询的Reporters，POST:{}', select_url)
                params.pop('ctl00$ContentView$OkButton')
                params['__VIEWSTATE'] = viewstate
                params['__VIEWSTATEGENERATOR'] = viewstate_generator
                params['ctl00$ScriptManager1'] = 'tl00$ScriptManager1|ctl00$ContentView$ButtonReportersSave'
                params['ctl00$ContentView$ButtonReportersSave'] = 'Save'
                reporter = next(reporter for reporter in reporters if reporter['name'] == nation)
                reporter_names = [reporter['name']]
                params[reporter['id']] = 'on'
                for child_reporter in reporter['children']:
                    params[child_reporter['id']] = 'on'
                    reporter_names.append(child_reporter['name'])
                # 保存Reporters勾选
                res = retry_request('post', select_url, data=params, cookies=cookies)
                logger.info('设置要查询的Reporters成功！勾选的Reporters为：{}', reporter_names)
                viewstate, viewstate_generator = get_viewstate(res.text)

                # 为了避免获取的数据超过数量限制，根据Products分成多个部分获取
                params.pop('ctl00$ContentView$ButtonReportersSave')
                params['ctl00$ScriptManager1'] = 'ctl00$ScriptManager1|ctl00$ContentView$ButtonProductsSave'
                params['ctl00$ContentView$ButtonProductsSave'] = 'Save'
                product_pre_part = int(len(products) / part_count)
                logger.info('分成{}个部分获取数据，每个部分的Product数量为{}', part_count, product_pre_part)
                for part in range(part_count):
                    logger.info("准备获取第{}部分的数据，共{}部分", part + 1, part_count)

                    # 设置要勾选的Products
                    logger.info('开始设置要勾选的Products，POST:{}', select_url)
                    new_params = params.copy()
                    new_params['__VIEWSTATE'] = viewstate
                    new_params['__VIEWSTATEGENERATOR'] = viewstate_generator
                    start = part * product_pre_part
                    if part + 1 == part_count:
                        end = len(products)
                    else:
                        end = start + product_pre_part
                    for i in range(start, end):
                        new_params[products[i]['id']] = 'on'
                    # 保存勾选Products勾选
                    res = retry_request('post', select_url, data=new_params, cookies=cookies)
                    logger.info('设置要勾选的Products成功，勾选的范围为({})-----({})', products[start]['name'],
                                products[end - 1]['name'])
                    viewstate, viewstate_generator = get_viewstate(res.text)

                    # 进入下载页面
                    logger.info('开始进入下载页面， GET:{}', download_page_url)
                    res = retry_request('get', download_page_url, cookies=cookies)
                    logger.info('进入下载页面成功！')
                    soup = BeautifulSoup(res.text, 'html.parser')

                    # 生成文件
                    logger.info('开始请求生成文件，POST:{}', download_page_url)
                    data = {'ctl00$ScriptManager1': 'ctl00$ContentView$ctl00|ctl00$ContentView$LinkButtonExport2Excel',
                            '__EVENTTARGET': 'ctl00$ContentView$LinkButtonExport2Excel',
                            '__VIEWSTATE': soup.find('input', id='__VIEWSTATE')['value'],
                            '__VIEWSTATEGENERATOR': soup.find('input', id='__VIEWSTATEGENERATOR')['value'],
                            '__PREVIOUSPAGE': soup.find('input', id='__PREVIOUSPAGE')['value'],
                            '__EVENTVALIDATION': soup.find('input', id='__EVENTVALIDATION')['value']}
                    retry_request('post', download_page_url, cookies=cookies, data=data)
                    logger.info('生成文件成功！')

                    # 下载文件
                    logger.info('开始下载文件，GET:{}', download_url)
                    filename = nation + '_' + str(year) + '_' + str(part) + '.zip'
                    filename = os.path.join(zip_path, filename)
                    res = retry_request('get', download_url, cookies=cookies)
                    with open(filename, "wb") as code:
                        code.write(res.content)
                    logger.info('文件下载成功！文件已保存至：{}', filename)
                    sleep(1)

            except Exception as e:
                logger.exception('获取{}的{}年数据失败', nation, year)
                failures.append({'nation': nation, 'year': years})

            logger.info('获取{}的{}年数据成功！', nation, year)
        logger.info('获取{}的数据成功！', nation)
    logger.info('获取数据结束，共失败{}次，失败的数据为{}', len(failures), failures)


if __name__ == '__main__':
    get_tariff()
