import re
import requests
import cloudscraper

from bs4 import BeautifulSoup
from scrapers.BaseScraper import BaseScraper


class EuroNewsScraper(BaseScraper):
    """
    Класс, предназначенный для автоматизированного сбора новостей
    с сайта информационного агентства EuroNews (https://www.euronews.com/)
    """

    def __init__(self, base_url: str):

        super().__init__(scraper_name="EuroNews Scraper")

        self.scraper_name = self.scraper_name
        self.scraper = cloudscraper.create_scraper()

        self.base_url = base_url

        print(f"{self.scraper_name} was initialized")

    def _get_bs_object(self, target_url: str) -> BeautifulSoup | None:
        """
        Метод позволяет получить объект BeautifulSoup по URL-запросу,
        путем отправки запроса и парсинга ответа (респонса) по заданому URL.

        Args:
            target_url (str): URL для отправки запроса.

        Returns:
            BeautifulSoup | None: Объект BeautifulSoup или None (при статусе запроса != 200)
        """

        response = self.scraper.get(target_url)

        if response.status_code != 200:

            print("An error while sending request!")
            print(f"Status Code: {response.status_code}")
            print(f"Text: {response.text}")

            return None

        bs_object = BeautifulSoup(response.text, "html.parser")

        return bs_object

    def _get_page_news(self, page_url: str) -> list[str] | None:
        """
        Метод позволяющих собрать все новости (ссылки на новости) с текущей страницы.

        Args:
            page_url (str): Страница, с которой требуется собрать ссылки на новости

        Returns:
            list[str] | None: Лист, содержащий ссылки на новости или None, если изначальный запрос не вернул код 200.
        """

        page_content = self._get_bs_object(target_url=page_url)

        if page_content is None:

            print("Failed to fetch page content!")
            return None

        news_listing_el = page_content.find(
            "div", class_="h-grid h-grid-body b-listing__body"
        )

        articles = news_listing_el.find_all("article")

        hrefs_list = []

        for article in articles:

            link = article.find("a", class_="the-media-object__link")

            if link and link.get("href"):

                hrefs_list.append(self.base_url + link.get("href"))

        return hrefs_list

    def _parse_headline(self, bs_object: BeautifulSoup) -> str | None:
        """
        Метод для парсинга заголовка новостной статьи.

        Args:
            bs_object (BeautifulSoup): Объект BeautifulSoup

        Returns:
            str | None: Новостной заголовок в формате строки или None.
        """

        headline = bs_object.find("h1", class_="c-article-redesign-title")

        headline = headline.text.strip() if headline is not None else None

        return headline

    def _parse_lead(self, bs_object: BeautifulSoup) -> str | None:
        """
        Метод для парсинга лида новостной статьи.

        Args:
            bs_object (Объект BeautifulSoup)

        Returns:
            str | None: Лид в формате строки или None
        """

        lead = bs_object.find("h2", class_="c-article-summary")

        lead = lead.text.strip() if lead is not None else None

        return lead

    def _parse_date(self, bs_object: BeautifulSoup) -> str | None:
        """
        Метод для парсинга даты публикации новостной статьи.

        Args:
            bs_object (BeautifulSoup): Объект BeautifulSoup

        Returns:
            str | None: Дата публикации в формате строки или None.
        """

        date = bs_object.find("div", class_="c-article-publication-date")

        date = date.text.strip() if bs_object is not None else None

        return date

    def _parse_author(self, bs_object: BeautifulSoup) -> str | None:
        """
        Метод для парсинга автора новостной статьи.

        Args:
            bs_object (BeautifulSoup): Объект BeautifulSoup

        Returns:
            str | None: Автор новостной статьи в формате строки или None.
        """

        author_element = bs_object.find("div", class_="c-article-contributors")

        concrete_author = author_element.find("a")

        concrete_author = (
            concrete_author.text.strip() if concrete_author is not None else None
        )

        return concrete_author

    def _parse_body(self, bs_object: BeautifulSoup) -> str | None:
        """
        Метод для парсинга тела новостной статьи (основного текста новостной статьи).

        Args:
            bs_object (BeautifulSoup): Объект BeautifulSoup

        Returns:
            str | None: Тело новости в формате строки или None.
        """

        text_element = bs_object.find("div", class_=re.compile(r"^c-article-content"))

        if text_element is None:

            print("Failed to locate article body!")

            return None

        article_paragraphs = text_element.find_all("p")

        article_body = "\n\n".join([x.text.strip() for x in article_paragraphs])

        return article_body

    def _parse_single_article(self, article_url: str) -> dict | None:
        """
        Метод для парсинга одинарной новостной статьи.

        Применяемые методы:
        - _parse_headline.
        - _parse_lead.
        - _parse_date.
        - _parse_author.
        - _parse_body

        Args:
            article_url (str): URL конкретной новостной статьи

        Returns:
            dict | None: Словарь, содержащий информацию в соответствии с применяемыми метода или None
        """

        if (
            "/video/" in article_url
        ):  # Примитивная проверка, на EuroNews есть новостные статьи, в который представлено только видео, осознанно пропускаем такие статьи

            print("Video article detected! Skipping parsing...")
            print(f"Skipped URL: {article_url}")
            return None

        soup = self._get_bs_object(target_url=article_url)

        article_dictionary = {
            "headline": "",
            "lead": "",
            "date": "",
            "author": "",
            "article_text": "",
            "source_url": article_url,
            "root_url": self.base_url,
        }

        article_dictionary["headline"] = self._parse_headline(bs_object=soup)
        article_dictionary["lead"] = self._parse_lead(bs_object=soup)
        article_dictionary["date"] = self._parse_date(bs_object=soup)
        article_dictionary["author"] = self._parse_author(bs_object=soup)
        article_dictionary["article_text"] = self._parse_body(bs_object=soup)

        return article_dictionary

    def _get_main_paginator(self, page_url: str) -> BeautifulSoup:
        """
        Функция для получения основного элемента пагинатора (необходим для навигации по страницам)

        Args:
            page_url (str): URL страницы, на которой необходимо собрать основной элемент.

        Returns:
            BeautifulSoup: Объект BeautifulSoup. Если основной пагинатор is None, вызовет ValueError.
        """

        soup = self._get_bs_object(target_url=page_url)

        main_paginator = soup.find("ul", class_="c-paginator")

        if main_paginator is None:
            raise ValueError("Main paginator not found!")

        return main_paginator

    def _get_total_num_pages(self, page_url: str) -> int:
        """
        Метод для получения сумарного количества страниц в целевой новостной рубрике.
        Необходим для эффективного отслеживания прогресса при парсинге рубрик.

        Args:
            page_url (str): URL-страницы. Вне зависимости, стартовая страница или нет, общее кол-во можно отследить.

        Returns:
            int: Общее количество новостных статей. Вызывает ValueError, если не удалось найти сумарное кол-во
        """

        main_paginator = self._get_main_paginator(page_url=page_url)

        paginator_buttons = main_paginator.find_all(
            ["a", "span"], class_="c-paginator__button"
        )

        if paginator_buttons is None:
            raise ValueError("Pagination Buttons were not found!")

        pages = [int(x.text.strip()) for x in paginator_buttons]

        total_num_pages = max(pages)  # Выбираем максимальное число

        return total_num_pages

    def _get_next_page_url(self, page_url: str) -> str | None:
        """
        Метод для эффективной навигации между страницами новостной рубрики.

        Предполагаемый алгоритм навигации: current_page + 1, То есть вперед на одну страницу,
        ?p=1 -> ?p=2

        Args:
            page_url (str): URL страницы на текущей итерации.

        Returns:
            str | None: хвост ссылки следующей страницы, например: /tag/united-kingdom?p=2.
        """

        main_paginator = self._get_main_paginator(page_url=page_url)

        next_href = main_paginator.find("a", class_="c-cta u-chevron-ie-a").get("href")

        next_href = next_href if next_href is not None else None  # Should never happen

        return next_href  # next_href usually looks like this: '/tag/united-kingdom?p=2', so the base_url must be added to it

    def _get_current_page_num(self, page_url: str) -> int:
        """
        Метод, позволяющий получить номер текущей страницы новостной рубрики.

        Args:
            page_url (str): URL-страницы, для которой необходимо узнать номер

        Returns:
            int: Номер текущей страницы. Вызывает ValueError, если номер не был найден.
        """

        main_paginator = self._get_main_paginator(page_url=page_url)

        current_page_num = main_paginator.find(
            "span", class_="c-paginator__button c-current-page"
        ).text

        if current_page_num is None:
            raise ValueError("Current page element was not found!")

        else:
            return int(current_page_num)

    def parse_rubric(self, start_url: str, num_collected_news: int = 100) -> list[dict]:
        """
        Метод для парсинга конкретной рубрики с сайта новостного агентства Euro News.

        Args:
            start_url (str): Стартовая страница, с которой необходимо начать сбор.
            num_collected_news (int): Количество новостей, которое необходимо собрать. Default = 100.

        Returns:
            list[dict]: Список словарей. С названием ключей можно ознакомиться в методе _parse_single_article
        """

        news_list = []  # list[dict] -> список словарей собранных новостей

        rubric_num_pages = self._get_total_num_pages(
            page_url=start_url
        )  # Сколько страниц в рубрике

        collected_news = 0

        while collected_news < num_collected_news:

            page_news = self._get_page_news(
                page_url=start_url
            )  # Получаем все новости со страницы

            for link in page_news:

                try:

                    parsed_article = self._parse_single_article(article_url=link)

                    if parsed_article is not None:

                        news_list.append(parsed_article)

                except Exception as e:

                    print("An error occured during article scraping")
                    print(f"Exception: {e}")

            page_number = self._get_current_page_num(page_url=start_url)

            collected_news = len(news_list)

            print(f"Итерация сбора новостей с URL `{start_url}` успешно завершена!")
            print(
                f"Успешно собраны новости со страницы {page_number} из {rubric_num_pages}"
            )
            print(f"Количество собранных новостей: {collected_news}")

            # I. Определяем номер страницы, с которой были собраны новости, если page_num = total_page_num - break
            if page_number == rubric_num_pages:

                print(f"Все новости рубрики были успешно собраны, завершаю цикл...")
                break

            # II. Определяем URL следующей страницы

            next_url = self._get_next_page_url(page_url=start_url)

            if next_url is None:
                break  # Прекращаем цикл если нет следующей страницы, should never happen

            start_url = self.base_url + next_url

            print(f"URL для следующей итерации: {start_url}")

        return news_list
