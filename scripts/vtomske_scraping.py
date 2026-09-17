#  Скрипт актуализирован 17.09.2026
# В соответствии с изменениями парсера. Новая версия - VtomskeScraper

import pandas as pd

from scrapers.VtomskeScraper import VtomskeScraper


thematics_url = {
    "томск": "https://vtomske.ru/tag/tomsk",
    "россия": "https://vtomske.ru/tag/russia",
    "мир": "https://vtomske.ru/tag/world",
    "экономика": "https://vtomske.ru/tag/economics",
    "политика": "https://vtomske.ru/tag/politics",
    "происшествия": "https://vtomske.ru/tag/incident",
    "авто": "https://vtomske.ru/tag/auto",
    "спорт": "https://vtomske.ru/tag/sport",
}

scraper = VtomskeScraper(
    scraper_name = 'VtomskeScraper'
)

n_news = int(input('Введите количество новостей, которые необходимо собрать: '))

user_thematic = input('Введите название тематики (рубрики), по которой необходимо собрать новости: ').lower()

thematic_url = thematics_url.get(user_thematic, None)

if not thematics_url:
    print(f'Введена отутсвующая тематика: ```{user_thematic}```')
    print(f'Список поддерживаемых тематик: {'\n'.join(list(thematics_url.keys()))}')
    raise ValueError('Повторите ввод, используя поддерживаемую тематику')


resulting_news = scraper.parse_rubric(start_url = thematic_url,
                                      num_news = n_news)

df = pd.DataFrame(resulting_news)

df.to_csv(f'data/vtomske_data/{user_thematic}.csv', index = False) # Перед запуском убедитесь, что в директории data присутсвует поддиректория vtomske_data