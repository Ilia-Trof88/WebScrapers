# Скрипт сбора новостей по всем тематикам используя класс парсера из scrapers.GazetaScaper

# Работоспособность проверена 15.09.2026

from scrapers.GazetaScraper import Scrapper

n_news = int(input('Введите количество новостей, которое необходимо собрать: '))

target_categories = [
    'Наука',
    'Спорт',
    'Политика',
    'Город',
    'Происшествия',
    'Ленобласть',
    'Культура'
]

for category in target_categories:

    parser = Scrapper(category = category)

    result = parser.scrape_news(n_news = n_news,
                                save_path = f"data/{category}.csv")
    
    print(f'Сбор новостей по тематике {category} окончен! Собрано новостей: {len(result)}')