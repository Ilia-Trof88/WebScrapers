import re
import requests
import pandas as pd

from bs4 import BeautifulSoup

from scrapers.BaseScraper import BaseScraper

class GazetaScraper(BaseScraper):

    rubric_dictionary = {
        "город": "https://gazeta.spb.ru/category/",
        "происшествия": "https://gazeta.spb.ru/category/proisshestviya-20/",
        "ленобласть": "https://gazeta.spb.ru/category/leningradskaya-oblast/",
        "культура": "https://gazeta.spb.ru/category/kultura-40978/",
        "спорт": "https://gazeta.spb.ru/category/sport-4/",
        "политика": "https://gazeta.spb.ru/category/politika-6/",
        "наука": "https://gazeta.spb.ru/category/nauka-10724-8287/"
        }

    def __init__(self,
                 scraper_name: str,
                 rubric_name: str):
        super().__init__(scraper_name)

        supported_rubrics = ', '.join(list(self.rubric_dictionary.keys()))

        if rubric_name.lower() not in self.rubric_dictionary:
            raise ValueError(f'Введена недопустимая рубрика!\nПоддерживаемые рубрики: {supported_rubrics}')

        self.rubric_name = rubric_name.lower()
        self.initial_url = self.rubric_dictionary.get(self.rubric_name)

        print(f'GazetaScraper по тематике {self.rubric_name} успешно инициализирован!')

        
    def _get_bs_object(self,
                       target_url: str) -> BeautifulSoup | None:
        '''
        Метод для получения объекта BeautifulSoup.

        Args:
            target_url (str): URL-страницы, для которой необходимо получить объект BS.
        
        Returns:
            BeautifulSoup | None: Объект BeautifulSoup | None при response_code != 200.
        '''

        try:

            response = requests.get(url = target_url)

            if response.status_code != 200:

                print('Произошла непредвиденная ошибка при отправка запроса!')
                print(f'Status Code: {response.status_code}')
                print(f'Текст ошибки: {response.text}')
                return None

            bs_object = BeautifulSoup(response.text, 'html.parser')

            return bs_object

        except Exception as e:

            print('Произошла ошибка при отправке запроса')
            print(f'Текст ошибки: {e}')

            empty_bs_object = BeautifulSoup() # Поиск по такому объекту вернет None, но не выдаст ошибку как в случае поиска по None

            return empty_bs_object

    def _parse_headline(self,
                        news_url: str) -> str | None:
        '''
        Метод для получения заголовка новостной статьи.

        Args:
            news_url (str): URL новостной статьи, из которой нужно извлечь заголовок
        
        Returns:
            str | None: Новостной заголовок в формате str | None, если выделить не удалось.
        '''

        bs_object = self._get_bs_object(target_url = news_url)

        news_headline = bs_object.find('h1').text

        headline = None if news_headline is None else news_headline

        return headline

    def _parse_news_body(self,
                         news_url: str) -> str | None:
        '''
        Метод для получения основного текста (тела) новостной статьи.

        Args:
            news_url (str): URL новостной статьи, с которой нужно собрать информацию.
        
        Returns:
            str | None: Тело новостной статьи в формате str | None, если произошла ошибка при выполнении запроса
        '''

        bs_object = self._get_bs_object(target_url = news_url)

        content_div = bs_object.find('div', class_='td_block_wrap tdb_single_content tdi_73 td-pb-border-top td_block_template_1 td-post-content tagdiv-type')

        body_pattern = re.compile(r"^h[1-6]$|^p$")

        matches = content_div.find_all(re.compile(body_pattern))

        if not matches:
            return None

        else:

            article_text = '\n\n'.join([x.get_text(strip = True) for x in matches])

            return article_text


    def _parse_date(self,
                    news_url: str) -> str | None:
        '''
        Метод для получения даты публикации новости в формате строки.

        Args:
            news_url (str): URL новостной статьи для сбора даты публикации.
        
        Returns:
            str | None: Дата (datetime) публикации в формате строки | None если дату выделить не удалось.
        '''

        bs_object = self._get_bs_object(target_url = news_url)

        date_class = bs_object.find('time', class_='entry-date updated td-module-date')

        publish_date = None if date_class is None else date_class['datetime']

        return publish_date

    def _parse_author(self,
                      news_url: str) -> str:
        '''
        Метод для получения автора статьи

        Args:

        Returns:

        '''

        bs_object = self._get_bs_object(target_url = news_url)

        author_block = bs_object.find('a', class_='tdb-author-name')

        author = None if author_block is None else author_block.text.strip()

        return author

    def _parse_tags(self,
                    news_url: str) -> str:
        '''
        Метод для получения тегов (в формате строки).

        Args:

        Returns:

        '''

        bs_object = self._get_bs_object(target_url = news_url)

        tags_class = bs_object.find('ul', class_='tdb-tags')

        tags = None if tags_class is None else ', '.join(tag.get_text(strip = True) for tag in tags_class.find_all('a'))

        return tags

    def _parse_single_article(self,
                              news_url: str) -> dict:
        '''
        Метод для сбора всей информации по конкретной новости.

        Args:
            news_url (str): Ссылка на новостную статью
        
        Returns:
            dict: Словарь со следующими ключами:
            - headline:
            - body:
            - publishing_date:
            - url:
            - rubric_name: 
        '''

        news_dictionary = {
            "headline": self._parse_headline(news_url = news_url),
            "body": self._parse_news_body(news_url = news_url),
            "tags": self._parse_tags(news_url = news_url),
            "publishing_date": self._parse_date(news_url = news_url),
            "author": self._parse_author(news_url = news_url),
            "url": news_url,
            "rubric_name": self.rubric_name
        }

        return news_dictionary

    def _get_page_news(self,
                       target_url: str) -> list[str] | None:
        '''
        Метод получения всех URL-новостей на заданной странице.

        Args:
            target_url (str): URL, с которого необходимо собрать все ссылки (URL) на новости

        Returns:
            list[str] | None: Список ссылок, при успешном запросе или None.
        '''

        bs_object = self._get_bs_object(target_url = target_url)

        h3_tags = bs_object.select('h3.entry-title.td-module-title')

        if h3_tags is None:
            return None # На текущей странице не обнаружено новостей

        hrefs = []

        for h in h3_tags:

            a = h.find("a")

            if (a) and (a.get('href')):

                hrefs.append(a['href'])

        return hrefs

    def parse_rubric(self,
                     target_news_num: int) -> list[dict]:
        '''
        Метод для сбора новостей по конкретной тематике.
        
        Сбор организован итеративным продвижение вперед по страницам выбранной тематике.
        По сбору желаемого кол-ва новостей цикл прекращается.

        Args:
            num_news (int): Количество новостей, которое необходимо собрать
        
        Returns:
            list[dict]: Список словарей. Словари следует структуре, которая указана в методе _parse_single_article.
        '''

        collected_news = []

        num_collected_news = 0

        page_counter = 1

        appendix = 'page/{page_counter}/' # Строка, которую постоянно обновляем в процессе продвижения по страницам

        while num_collected_news < target_news_num:

            current_page_url = self.initial_url + appendix.format(page_counter = page_counter)

            print(f'Сбор новостей со следующего URL: {current_page_url}')

            page_news = self._get_page_news(target_url = current_page_url)

            if not page_news:
                print('На странице не обнаружено новостей! Завершаю цикл...')
                break

            for article in page_news:

                news_dictionary = self._parse_single_article(news_url = article)

                collected_news.append(news_dictionary)

            num_collected_news = len(collected_news) # Обновляем количество собранных новостей

            page_counter+=1 # Обновляем счетчик страницы (необходимо для перехода на следующую страницу)

            print(f'Был успешно произведен сбор со страницы: {current_page_url}')
            print(f'Количество собранных новостей: {num_collected_news}')

        print('Цикл сбора новостей успешно завершен')
        print(f'Количество собранных новостей: {num_collected_news}')

        return collected_news


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
