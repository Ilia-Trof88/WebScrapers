# Работоспособность проверена 18.09.2026
import pandas as pd

from scrapers.GazetaScraper import GazetaScraper

n_news = int(input("Введите количество новостей, которое необходимо собрать: "))

target_rubric = input("Введите рубрику, по которой хотите собрать новости: ")

scraper = GazetaScraper(scraper_name="GazetaScraper", rubric_name=target_rubric)

result = scraper.parse_rubric(target_news_num=n_news)

df = pd.DataFrame(result)

df.to_csv(f"data/gazeta_data/{target_rubric}.csv", index=False)

print(
    f"Цикл сбора новостей успешно сохранен, новости успешно сохранены в следующую директорию: data/gazeta_data/{target_rubric}.csv"
)
