import re
import requests

from tqdm import tqdm
from bs4 import BeautifulSoup

from scrapers.BaseScraper import BaseScraper

class VtomskeScraper(BaseScraper):

    BASE_URL = 'https://vtomske.ru'

    def __init__(self,
                 scraper_name: str):

        super().__init__(scraper_name)

    def _get_bs_object(self,
                       url: str) -> BeautifulSoup:
        """
        Метод для получения объекта BeautifulSoup

        Args:
            url: str
        
        Returns:
            BeautifulSoup | None: Объект BeautifulSoup или None при status_code != 200
        """

        response = requests.get(url = url)

        if response.status_code != 200:

            print(f'The request was unsuccessfull')
            print(f'Status code: {response.status_code}')
            print(f'Response: text: {response.text}')

            return None

        bs_object = BeautifulSoup(response.text, 'html.parser')

        return bs_object

    def _parse_headline(self,
                        news_url: str) -> str | None:
        '''
        Метод для сбора заголовка с конкретной новостной статьи
        '''

        bs_object = self._get_bs_object(url = news_url)

        if bs_object is None:
            return None

        news_headline = bs_object.find('h1').text

        if not news_headline:
            return None

        else:
            return news_headline

    def _parse_news_body(self,
                         news_url: str) -> str | None:
        """
        Метод для получения тела новости

        Args:
            news_url (str): URL-новости
        
        Returns:
            str | None: Текст новости либо None. 
        """

        bs_object = self._get_bs_object(url = news_url)

        if bs_object is None:

            return None

        page_content = bs_object.find('div', class_='material-content')

        if not page_content:
            return None

        all_text_material = page_content.find_all(re.compile(r'^(h[1-6]|p|ul)$')) # Получаем все возможные теги

        news_body = '\n'.join([x.text for x in all_text_material])

        return news_body

    def _parse_publishing_date(self,
                               news_url: str) -> str | None:
        '''
        Метод для получения даты (datetime) публикации новости в формате строки

        Args:
            news_url (str): Ссылка на страницу новости.
        
        Returns:
            str | None: datetime новости в формате str или None
        '''

        bs_object = self._get_bs_object(url = news_url)

        if bs_object is None:
            return bs_object

        material_information = bs_object.find('div', class_='material-info')

        if not material_information:
            return None

        time_tag = material_information.find('time', class_='material-date')

        dt_str = time_tag.get('datetime')

        return dt_str

    def _parse_author(self,
                      news_url: str) -> str | None:
        '''
        Метод для получения автора новостной статьи
        '''

        bs_object = self._get_bs_object(url = news_url)

        material_tag = bs_object.find('div', class_='material-info')

        if not material_tag:
            return None

        author = material_tag.find('a', class_='material-author').text

        return author

    def _get_page_news(self,
                       page_url: str) -> list[str] | None:
        """
        Метод для получения всех ссылок на новости со страницы.

        Args:
            page_url (str): URL-страницы, с которой требуется собрать все ссылки.

        Returns:
            list[str] | None: Список со всеми ссылками со страницы либо None

        """

        bs_object = self._get_bs_object(url = page_url)

        links_element = bs_object.find_all("a", class_="lenta_material")

        if not links_element:

            return None

        links = [self.BASE_URL + str(x.get('href')) for x in links_element]

        return links

    def _parse_single_article(self,
                              news_url: str) -> dict[str, str | None]:
        """
        Метод выполняющий парсинг одной новостной статьи.

        Args:
            news_url (str): URL конкретной новостной статьи
        
        Returns:
            dict: Словарь со следующими ключами:
            - headline. Заголовок новостной статьи.
            - news_body. Тело (основной текст) новостной статьи.
            - publishing_date. Дата публикации datetime в формате строки.
            - author. Автор новости.
        """

        base_dict = {
            "headline": None,
            "news_body": None,
            "publishing_date": None,
            "author": None
        }


        try:

            parsed_headline = self._parse_headline(news_url = news_url)
            parsed_body = self._parse_news_body(news_url = news_url)
            parsed_publishing_date = self._parse_publishing_date(news_url = news_url)
            parsed_author = self._parse_author(news_url = news_url)

            base_dict['headline'] = parsed_headline
            base_dict['news_body'] = parsed_body
            base_dict['publishing_date'] = parsed_publishing_date
            base_dict['author'] = parsed_author

            return base_dict

        except Exception as e:

            print(f'An unexpected Error occured during article parsing!')
            print(f'Exception text: {e}')

            return base_dict

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
