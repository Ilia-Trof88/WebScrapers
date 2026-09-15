# Дата создания парсера: 24.06.2026
import re
import requests

from tqdm import tqdm
from bs4 import BeautifulSoup


class NewsParser:
    """
    Класс позволяет совершить автоматический сбор n-новостей по одной из поддерживаемых тематик
    """

    def __init__(self, thematic: str):
        """
        Args:
            thematic (str): Тематика, по которой следует собрать новостные статьи
            Поддерживаемые тематики:
                1. Томск.
                2. Россия.
                3. Мир.
                4. Экономика.
                5. Политика.
                6. Происшествия.
                7. Авто.
                8. Спорт.
        """

        self.thematics_url = {
            "томск": "https://vtomske.ru/tag/tomsk",
            "россия": "https://vtomske.ru/tag/russia",
            "мир": "https://vtomske.ru/tag/world",
            "экономика": "https://vtomske.ru/tag/economics",
            "политика": "https://vtomske.ru/tag/politics",
            "происшествия": "https://vtomske.ru/tag/incident",
            "авто": "https://vtomske.ru/tag/auto",
            "спорт": "https://vtomske.ru/tag/sport",
        }

        if thematic not in list(self.thematics_url.keys()):

            return KeyError("Выбранная тематика не поддерживается!")

        else:

            self.thematic_url = self.thematics_url.get(thematic)

        self.origin_url = "https://vtomske.ru"

    def parse_single_article(self, url: str) -> dict:
        """
        Метод посвящен сбору информации с веб-страницы одной новостной статьи.

        Args:
            url (str): URL-страницы с новостью

        Returns:
            list[dict]: Список словарей, ключами которых служат: news_headline - заголовок новостной статьи, news_body: текст новостной статьи.
        """

        search_pattern = re.compile(
            r"^h[2-9]$"
        )  # Паттерн для выделения всех элементов с тэгов h[2-9]

        clean_pattern = r"<[^>]*>"  # Паттерн удаления HTML-тэгов.

        tags = [search_pattern, "p", "ul"]  # Ищем со второго по 9

        text_response = requests.get(url).text

        all_page_elements = BeautifulSoup(text_response, "html.parser")

        news_headline = all_page_elements.find("h1")

        news_body = all_page_elements.find_all(tags)  # list[tags]

        news_body = "".join([str(x) for x in news_body])

        news_string = re.sub(clean_pattern, "", news_body)

        news_headline = re.sub(clean_pattern, "", str(news_headline))

        news_dictionary = {
            "news_headline": news_headline,
            "news_body": news_string.strip(),
        }

        return news_dictionary

    def parse_thematic(self, n_news: int) -> list[dict]:
        """
        Метод посвящен сбору заданного количества новостей (n_news) по конкретной тематике.

        Args:
            n_news (int): Количество новостей, которое необходимо собрать.
                * 45 - количество ссылок на новостные статьи в рамках одной страницы.
                * Если n_news - число не кратное 45 количество новостей может превышать установленный лимит.
        """

        news_list = []  # list[dict]

        next_page_link = ""

        while len(news_list) < n_news:

            try:

                thema_url = self.thematic_url + next_page_link

                all_page_content = requests.get(thema_url)

                # I. Get all the links on the page

                elements = BeautifulSoup(all_page_content.text, "html.parser")

                links = elements.find_all("a", class_="lenta_material")

                hrefs = [
                    link.get("href") for link in links
                ]  # Complete list of page href's

                # II. Parse all the news from the page

                for href in tqdm(
                    hrefs, total=len(hrefs), desc="Data Gathering is in process..."
                ):

                    temp_dict = self.parse_single_article(url=self.origin_url + href)

                    news_list.append(temp_dict)

                # III. Finding link to the new page

                next_page_link = elements.find("a", class_="btn lenta_pager_next").get(
                    "href"
                )

            except Exception as e:
                print("Произошла ошибка! Прерываю цикл")
                print(f"Текст ошибки: {e}")
                break

        return news_list
