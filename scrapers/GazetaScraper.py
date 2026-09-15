import requests
import pandas as pd

from bs4 import BeautifulSoup


class Scrapper:
    """
    Класс для автоматизированного сбора текстов новостных статей с сайта https://gazeta.spb.ru/
    Парсер был актуализирован 15.07.2026.
    """

    def __init__(self, category: str):
        """
        Конструктор класса автоматизированного сбора новостей.
        Один объект = Одна тематика.

        Args:
            category (str): Тематика новостей, по которой требуется собрать новостные тексты.
        """

        allowed_categories = [
            "Город",
            "Происшествия",
            "Ленобласть",
            "Культура",
            "Спорт",
            "Политика",
            "Наука",
        ]

        if category not in allowed_categories:

            raise KeyError(
                f"Введенная тематика не поддерживается! Поддерживаются следующие тематики: {', '.join(allowed_categories)}"
            )

        mapping_dictionary = {
            "Город": "https://gazeta.spb.ru/category/",
            "Происшествия": "https://gazeta.spb.ru/category/proisshestviya-20/",
            "Ленобласть": "https://gazeta.spb.ru/category/leningradskaya-oblast/",
            "Культура": "https://gazeta.spb.ru/category/kultura-40978/",
            "Спорт": "https://gazeta.spb.ru/category/sport-4/",
            "Политика": "https://gazeta.spb.ru/category/politika-6/",
            "Наука": "https://gazeta.spb.ru/category/nauka-10724-8287/",
        }

        self.news_category = category
        self.category_url = mapping_dictionary.get(category)

    # Parsing news body

    def parse_news_article(self, url: str) -> dict:
        """
        Метод позволяет осуществить сбор информации с одной новой новостной статьи.

        Будут собраны следующие данные:
            1. Заголовок новости.
            2. Тело новости.
            3. Список тэгов (в формате строки).
            4. Дата публикации.
            5. Категория (тематика) новости.

        Args:
            url (str): URL-адрес новостной статьи.

        Returns:
            dict: Словарь с ключами, которые указаны выше.
        """

        try:

            result = requests.get(url).text

            page_content = BeautifulSoup(result, "html.parser")

            news_headline = page_content.find("h1").text  # Заголовок новости

            tags_class = page_content.find("ul", class_="tdb-tags")

            date_class = page_content.find(
                "time", class_="entry-date updated td-module-date"
            )

            publish_date = date_class["datetime"]

            tags = ", ".join(
                [tag.get_text(strip=True) for tag in tags_class.find_all("a")]
            )

            content_div = page_content.find(
                "div",
                class_="td_block_wrap tdb_single_content tdi_73 td-pb-border-top td_block_template_1 td-post-content tagdiv-type",
            )

            artcile_text = " ".join(
                [x.get_text(strip=True) for x in content_div.find_all("p")]
            )

            news_dictionary = {
                "Headline": news_headline,
                "Body": artcile_text,
                "Tags": tags,
                "Publishing_Date": publish_date,
                "News_Category": self.news_category,
            }

            return news_dictionary

        except Exception as e:

            print(f"Произшла ошибка при сборе новости! Текст ошибки: {e}")

            emergency_dict = {
                "Headline": "Unknown",
                "Body": "Unknown",
                "Tags": "Unknown",
                "Publishing_Date": "Unknown",
                "News_Category": "Unknown",
            }

            return emergency_dict  # Чтобы в случае единичной ошибки парсинга не падал весь цикл. Частый триггер - рекламные статьи, где отличается структура страницы.

    def find_all_urls(self, url: str) -> list[str]:
        """
        Метод для нахождения всех URL на странице.

        Args:
            url (str): URL-страницы рубрики, на которой необходимо найти все ссылки на новостные статьи.

        Returns:
            list[str]: Список всех найденных на странице ссылок
        """

        b = BeautifulSoup(requests.get(url).text, "html.parser")

        h3 = b.find("h3", class_="entry-title td-module-title")

        h3_tags = b.select("h3.entry-title.td-module-title")

        hrefs = []

        for h3 in h3_tags:

            a = h3.find("a")

            if a and a.get("href"):
                hrefs.append(a["href"])

        return hrefs

    def scrape_news(self, n_news: int, save_path: str) -> pd.DataFrame:
        """
        Метод для автоматизированного сбора определенного количества новостей.

        Args:
            n_news (int): Количество новостей, которое необходимо собрать.
            save_path (str): Путь, по которому необходимо сохранить датасет. Необходимо указать полный путь + имя файла в формате .csv

        Returns:
            pd.DataFrame: Датафрейм, содержащий все собранные новостныи статьи. См. метод 'parse_news_article'.
        """

        appendix = "/page/{num}"

        iteration_counter = 1

        news_list = []  # list[dict]

        while len(news_list) < n_news:

            current_url = self.category_url + appendix.format(num=iteration_counter)

            # Sanity Check

            status_code = requests.get(current_url).status_code

            if status_code != 200:

                print(f"Статус ответа на запрос: {status_code}")
                print(f"Было собрано: {len(news_list)} новостных статей")
                break

            all_page_urls = self.find_all_urls(url=current_url)

            for url in all_page_urls:

                news_data = self.parse_news_article(url=url)  # dict

                if (
                    "Unknown" not in news_data.values()
                ):  # Если есть одно значение Unknown, значит все остальные также Unknown - не добавляем такие элементы в общий список

                    news_list.append(news_data)

            iteration_counter += (
                1  # Увеличиваем для корректного перехода по страницам сайта.
            )

            print(f"Было собрано: {len(news_list)} новостей")

        df = pd.DataFrame(news_list)

        df.to_csv(save_path, index=False)

        return df
