# tass_headers можно получить на вкладке Network при анализе исходного кода (кнопка "Посмотреть код")
# headers необходимо указать следующие поля: accept, user-agent, referer

import pandas as pd

from config.tass_headers import tass_headers
from scrapers.TassScraper import TassScraper
from src.functions import read_yaml_config

config = read_yaml_config(config_path = 'config/tass_config.yaml')

target_rubric = input('Введите название Рубрики, например "/moskva": ')
num_news = int(input('Введите количество новостей для сбора: '))


scaper = TassScraper(rubrics = target_rubric)

news = scaper.scrape_rubric(
    search_api_url = config['tass_endpoints']['search_url'],
    tass_headers = tass_headers,
    tass_content_url = config['tass_endpoints']['content_url'],
    max_collected_news = num_news
)

result = pd.DataFrame(news)

result.to_csv(f'data/tass_data/{target_rubric}.csv', index = False) # Удостоверьтесь, что в data есть субдиректория /tass/data

print('Цикл сбора успешно завершен! Файл успешно сохранен!')