#  Sample Parsing Script

import pandas as pd

from scrapers.VtomskeScraper import NewsParser

n_news = int(input('Введите количество новостей, которые необходимо собрать: '))

thematics = [
    'томск',
    'россия',
    'мир',
    'экономика',
    'политика',
    'происшествия',
    'авто',
    'спорт'
]

for thema in thematics:

    parser = NewsParser(thematic = thema)

    result = parser.parse_thematic(n_news = n_news)

    df = pd.DataFrame(result)

    df.to_csv(f'data/{thema}.csv', index = False)

    print(f'Датасет по тематике {thema} сохранен!')