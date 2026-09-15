import pandas as pd

from scrapers.EuroNewsScraper import EuroNewsScraper


possible_urls = [
    'https://www.euronews.com',
    'https://de.euronews.com',
    'https://fr.euronews.com'
]

scraper = EuroNewsScraper(
    base_url = possible_urls[0] # DE
)

num_news = int(input('Введите количество новостей для сбора: '))

output_filename = input('Введите название файла, под которым будет сохранен файл: ')

start_url = 'https://www.euronews.com/tag/artificial-intelligence' # Example

result = scraper.parse_rubric(
    start_url = start_url,
    num_collected_news = num_news
)

df = pd.DataFrame(result)

df.to_csv(f'data/euronews_data/{output_filename}.csv', index = False) # Удостоверьтесь, что в data существует субдиректория /euronews_data/


