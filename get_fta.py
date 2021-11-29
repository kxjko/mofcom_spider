import csv

from scrapy import cmdline

ec = 'CN'
ic = 'SG'
code_file = 'SG_code_EN.csv'
output_file = 'fta_{}2{}.csv'.format(ec, ic)

if __name__ == '__main__':
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('编码', '原产地', '目的地', '协定税率', '普通税率', '降税安排备注', '降税安排表格', '一般原产地规则', '特定原产地规则'))
    # cmdline.execute('scrapy crawl fta'.split())

    cmdline.execute(
        'scrapy crawl fta -a ec={} -a ic={} -a hc={} -a output_file={}'.format(ec, ic, code_file, output_file).split())
