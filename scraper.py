# https://www.centrepointstores.com/qa/en/department/women
import csv
import re
import traceback
from pprint import pprint

import requests

ids = ["8517046", "8517051", "1020038", "2094053", "6035937", "4407713", "4010435", "4010894", "4408003", "4408044",
       "8600988", "9106360", "6035682", "9106144", "8600625", "5531750", "5529592", "3411835", "8600616", "7524734",
       "7525197", "7525017", "7525137", "7525175", "7524798", "7524142", "7525230", "7524848", "7523802", "7524854",
       "7524826", "7525231", "7525229", "7524817", "7524841", "7525284", "7523579", "7523580", "7523797", "7524818",
       "7525185", "7524839"]


class CentrePointStores:
    def __init__(self):
        self.session: requests.Session = self.init_session()
        self.mapped_headers = self.map_headers()
        self.headers = list(self.mapped_headers.keys())
        self.products = []

    @staticmethod
    def init_session():
        session = requests.session()
        session.headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'DNT': '1',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/93.0.4577.82 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Origin': 'https://www.centrepointstores.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.centrepointstores.com/',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,sv;q=0.6',
        }
        return session

    def get_product_details(self, product_id):
        params = (
            ('X-Algolia-API-Key', '7a625e3a548ccdd0393b5565896c5d89'),
            ('X-Algolia-Application-Id', 'LM8X36L8LA'),
            ('X-Algolia-Agent', 'Algolia for vanilla JavaScript 2.9.7'),
        )

        data = f'{{"params":"query=&facetFilters=%5B%22approvalStatus%3A1' \
               f'%22%2C%5B%22objectID%3A{product_id}%22%5D%5D"}}'
        try:
            response = self.session.post(
                'https://lm8x36l8la-dsn.algolia.net/1/indexes/prod_qa_centrepoint_Product/query',
                params=params, data=data)
            return response.json()['hits'][0]
        except Exception:
            traceback.print_exc()
            return None

    def parse_details(self, info):
        parsed_info = {'url_en': '', 'url_ar': '', 'id': info['objectID']}

        # get the url
        url = info['url']
        for _url in url.values():
            parsed_info['url_en'] = _url['en']
            parsed_info['url_ar'] = _url['ar']
            break

        # get the categories from url
        en_url = parsed_info['url_en'].split('/')
        ar_url = parsed_info['url_ar'].split('/')
        try:
            cat_en = en_url[1]
            subcat_en = en_url[2]
            innercat_en = en_url[3]
        except Exception:
            cat_en = ''
            subcat_en = ''
            innercat_en = ''

        try:
            cat_ar = ar_url[1]
            subcat_ar = ar_url[2]
            innercat_ar = ar_url[3]
        except Exception:
            cat_ar = ''
            subcat_ar = ''
            innercat_ar = ''

        parsed_info['cat_en'] = cat_en
        parsed_info['subcat_en'] = subcat_en
        parsed_info['innercat_en'] = innercat_en
        parsed_info['cat_ar'] = cat_ar
        parsed_info['subcat_ar'] = subcat_ar
        parsed_info['innercat_ar'] = innercat_ar

        parsed_info['price'] = info['price']
        parsed_info['was_price'] = info['wasPrice']

        # get the product name
        parsed_info['name_en'] = info['name']['en']
        parsed_info['name_ar'] = info['name']['ar']

        # get the manufacturer
        parsed_info['manufacturer_en'] = info['manufacturerName']['en']
        parsed_info['manufacturer_ar'] = info['manufacturerName']['ar']

        # get the thumbnail
        parsed_info['thumbnail'] = info['345WX345H_https']

        # get variants and quantities
        _variants = info['childDetail']['childsDetails']
        variants = []
        quantities = []
        for variant in _variants:
            for _Key, _val in variant.items():
                variants.append(_Key)
                quantities.append(_val['inStock'])
        parsed_info['variants'] = variants
        parsed_info['quantities'] = quantities

        # get color variants
        try:
            for sibling in info['sibiling']:
                sibling_info = parsed_info.copy()
                sibling_info.update({
                    'color': sibling['color'],
                    'thumbnail': self.get_thumbnail(parsed_info['thumbnail'], sibling['code']),
                    'url_en': 'https://www.centrepointstores.com/qa' + parsed_info['url_en'],
                    'url_ar': 'https://www.centrepointstores.com/qa' + parsed_info['url_ar'],
                })
                self.products.append(sibling_info)
        except KeyError:
            # when there are no siblings
            sibling_info = parsed_info.copy()
            sibling_info.update({
                'color': info['color']['en'].capitalize(),
                'url_en': 'https://www.centrepointstores.com/qa' + parsed_info['url_en'],
                'url_ar': 'https://www.centrepointstores.com/qa' + parsed_info['url_ar'],
            })
            self.products.append(sibling_info)

    @staticmethod
    def get_thumbnail(url, color_id):
        return re.sub(r'(?<=lmsin\.net/)(.*?)(?=-)', str(color_id), url)

    @staticmethod
    def map_headers():
        return {
            'Name En': 'name_en',
            'Name Ar': 'name_ar',
            'Product Id': 'id',
            'Category En': 'cat_en',
            'Category Ar': 'cat_ar',
            'Sub category En': 'subcat_en',
            'Sub Category Ar': 'subcat_ar',
            'Inner Category En': 'innercat_en',
            'Inner Category Ar': 'innercat_ar',
            'Manufacturer En': 'manufacturer_en',
            'Manufacturer Ar': 'manufacturer_ar',
            'Units': 'variants',
            'Color': 'color',
            'Price': 'price',
            'Full Price': 'wa_price',
            'Quantities': 'quantities',
            'Link En': 'url_en',
            'Link Ar': 'url_ar',
            'Thumbnail': 'thumbnail',
        }

    def get_row(self, parsed_info):
        return [
            parsed_info.get(header) for header in self.mapped_headers.values()
        ]

    def save(self):
        with open('data.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            for product in self.products:
                writer.writerow(self.get_row(product))


def main():
    store = CentrePointStores()
    for i, product_id in enumerate(ids):
        print(f'[{i + 1}/{len(ids)}] {product_id}')
        info = store.get_product_details(product_id)
        store.parse_details(info)
    store.save()


if __name__ == '__main__':
    main()
