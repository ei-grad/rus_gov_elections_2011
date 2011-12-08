#!/usr/bin/env python
# coding: utf-8

import codecs
import sys
from locale import getpreferredencoding
from functools import partial
import logging

from lxml.etree import HTMLParser
from lxml.html import parse


logging.basicConfig(format='%(message)s', level=logging.INFO)

parse = partial(parse, parser=HTMLParser(encoding="cp1251"))
encoding = getpreferredencoding()
urls = set()
out = sys.stdout

columns = [
    u'Регион',
    u'УИК',
    u'Число избирателей, внесенных в список избирателей',
    u'Число избирательных бюллетеней, полученных участковой избирательной комиссией',
    u'Число избирательных бюллетеней, выданных избирателям, проголосовавшим досрочно',
    u'Число избирательных бюллетеней, выданных избирателям в помещении для голосования',
    u'Число избирательных бюллетеней, выданных избирателям вне помещения для голосования ',
    u'Число погашенных избирательных бюллетеней',
    u'Число избирательных бюллетеней в переносных ящиках для голосования',
    u'Число избирательных бюллетеней в стационарных ящиках для голосования',
    u'Число недействительных избирательных бюллетеней',
    u'Число действительных избирательных бюллетеней',
    u'Число открепительных удостоверений, полученных участковой избирательной комиссией',
    u'Число открепительных удостоверений, выданных избирателям на избирательном участке',
    u'Число избирателей, проголосовавших по открепительным удостоверениям на избирательном участке',
    u'Число погашенных неиспользованных открепительных удостоверений',
    u'Число открепительных удостоверений, выданных избирателям территориальной избирательной комиссией',
    u'Число утраченных открепительных удостоверений',
    u'Число утраченных избирательных бюллетеней',
    u'Число избирательных бюллетеней, не учтенных при получении ',
    u'1. СР',
    u'2. ЛДПР',
    u'3. ПР',
    u'4. КПРФ',
    u'5. ЯБЛОКО',
    u'6. ЕР',
    u'7. ПД'
]


def parse_uics(url, name, retry=True):

    logging.info(u"%s: %s" % (name, url))

    try:

        d = parse(url)

        table = d.xpath('//td[@width="90%"]/div/table')
        assert len(table), 1
        table = table[0]

        rows = table.xpath('tr')
        assert len(rows), 27

        uics = rows[0].xpath('td/nobr/text()')

        data = [[int(j) for j in i.xpath('td/nobr/b/text()')]
                for i in rows]

        assert len(data) == 27
        assert len(data[19]) == 0
        del data[19]
        assert len(data[0]) == 0
        del data[0]

        for i in data:
            assert len(i) == len(uics)

        data = list(zip(*data)) # transpose data array

        lines = [';'.join([name, uics[i]] + list(map(str, data[i])))
                 for i in range(len(data))]

        out.write('\n'.join(lines) + '\n')

    except:
        if retry:
            parse_uics(url, name, False)
        else:
            raise

    logging.info(u"Done %s" % name)


def get_regions(tree, prefix=''):
    links = tree.xpath('//a')
    urls = [(a.get('href'), a.text) for a in links]
    if prefix:
        prefix = prefix + ' - '
    return [(url, prefix + name) for url, name in urls
            if url.startswith('http://www.vybory.izbirkom.ru/region/region/izbirkom')]


def parse_region(url, name):
    logging.info(u"Регион %s: %s" % (url, name))
    urls.add(url)
    tree = parse(url)
    uic_link = tree.xpath(
        u'//a[text()="сайт избирательной комиссии субъекта Российской Федерации"]/@href'
    )
    if len(uic_link):
        assert len(uic_link) == 1
        parse_uics(uic_link[0], name)
    else:
        for next_url, next_name in get_regions(tree, name):
            if next_url not in urls:
                parse_region(next_url, next_name)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        out = open(sys.argv[1], 'w')
    out = codecs.getwriter(encoding)(out)

    out.write(u';'.join(columns) + u'\n')

    for url, name in get_regions(parse('http://www.vybory.izbirkom.ru/region/region/izbirkom?action=show&root=1&tvd=100100028713304&vrn=100100028713299&region=0&global=1&sub_region=0&prver=0&pronetvd=null&vibid=100100028713304&type=233')):
        parse_region(url, name)

    out.close()
