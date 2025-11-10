from csv import DictWriter
from email.utils import parsedate_to_datetime

import requests


def convert_to_csv():
    with open('qa-uris.csv', mode='w') as csv_fh:
        writer = DictWriter(csv_fh, fieldnames=('uri', 'last_modified'))
        writer.writeheader()
        with open('qa-uris.txt') as txt_fh:
            for line in txt_fh:
                uri = line.rstrip('\n')
                res = requests.head(uri)
                last_modified = parsedate_to_datetime(res.headers['Last-Modified'])
                binary = {
                    'uri': uri,
                    'last_modified': str(last_modified),
                }
                print(binary)
                writer.writerow(binary)


convert_to_csv()
