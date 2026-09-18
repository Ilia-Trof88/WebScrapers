import requests

from scrapers.BaseScraper import BaseScraper


class TassScraper(BaseScraper):

    def __init__(self, rubrics: str):

        super().__init__(scraper_name="TASS Scraper")

        self.rubrics = rubrics

        print(f"{self.scraper_name} was initialized!")

    def _get_page_news(
        self,
        search_api_url: str,
        tass_headers: dict,
        news_limit: int = 30,
        search_after: str = None,
    ) -> list[dict] | None:
        """
        Метод для получения списка новостей на конкретной странице.

        На сайте новостного агентства ТАСС реализована так называемая "бесконечная лента",
        где нет конкретной страницы.

        В данном случае, необходимо обновление timestamp'а (параметр search_after), чтобы "сдвигать" стартовую дату.
        Значение данного параметра следует получать из последней новости из возвращаемого массива данного метода.

        Args:
            search_api_url (str): Эндпоинт API-поиска.
            tass_headers (dict): Headers для новостного агентства ТАСС.
            news_limit (int): Кол-во новостей в возвращаемом массиве (max & default = 30) > 30 приведет к ошибке.
            search_after (str): Timestamp - дата, после которой будут собраны новости.
        """

        payload = {
            "rubrics": self.rubrics,
            "limit": news_limit,
            "lang": "ru",
            "search_after": search_after,
        }

        try:

            response = requests.get(
                url=search_api_url, headers=tass_headers, params=payload
            ).json()

        except Exception as e:

            print(f"Произошла ошибка при получении JSON. Текст ошибки: {e}")

            return None

        try:
            return response["result"]["contents"]  # list[dict]

        except (
            Exception
        ) as e:  # Most likely the KeyError will be encountered, yet connection troubles are also possible
            print(f"An error occured! Error text: {e}")
            return None

    def _parse_single_article(
        self, tass_content_url: str, news_id: str, rubrics: str, headers: dict
    ) -> dict | None:
        """
        Метод для получения информации по конкретной новости.

        Args:
            tass_content_url (str): Специфичный для ТАСС эндпоинт контента (content_url).
            news_id (str): Уникальный идентификатор новости.
            rubrics (str): Конкретная рубрика. (не можем использовать self.rubrics, т.к. часто целевая рубрика не совпадает с основной рубрикой конкретной новости).
            headers (dict): Специфические для ТАСС заголовки.

        Returns:
            dict | None: None при ошибке парсинга или словарь со следующими ключами:
                - headline (Заголовок).
                - lead (Лид).
                - source (Источник новости).
                - author (Автор, при наличии).
                - body (Основной текст новости).
                - source_url (URL, по которому можно обнаружить новость).
                - timestamp (Момент публикации новости).
                - tass_rubric. Основная рубрика, присвоенная новости новостным агентством.
                - category. Выбранная категория, например, в категории "Москва" могут быть новости с рубрикой "Экономика", "Общество" и т.п.
        """
        url = tass_content_url + news_id

        params = {"lang": "ru", "path": rubrics}  # Хардкодим русский

        def get_article_text(news_dictionary: dict) -> str:
            """
            Хелпер функция для получения текста новости.

            Если в словаре есть items, значит есть и текст.
            Если в словаре нет items, значит текст новости отсутствует.
            """

            news_text = ""

            if (
                "items" in news_dictionary["content_blocks"][0]
            ):  # Если в первом 'items' есть текст - значит есть текст новости.

                for dictionary in news_dictionary["content_blocks"]:

                    try:

                        news_text += (
                            dictionary["items"][0]["text"] + " "
                        )  # Проверяем наличие текста в каждом словаре.

                    except KeyError:

                        pass

            return news_text

        try:

            result = requests.get(url=url, params=params, headers=headers).json()[
                "result"
            ]

            news_dictionary = {
                "headline": result.get("title", "No Title Found"),
                "lead": result.get("lead", "No Lead Found"),
                "source": "ТАСС",
                "author": result.get("author", "No Author Mentioned"),
                "body": get_article_text(news_dictionary=result),
                "source_url": f"https://tass.ru/{rubrics}/{news_id}",
                "timestamp": result["published_dt"],
                "tass_rubric": rubrics,
                "category": self.rubrics,
            }

            return news_dictionary

        except Exception as e:

            print(
                f"An error occured while trying to scrape news article!\nError text: {e}"
            )
            return None

    def scrape_rubric(
        self,
        search_api_url: str,
        tass_headers: dict,
        tass_content_url: str,
        max_retry_attemps: int = 5,
        search_after: str = None,
        max_collected_news: int = 90,
    ) -> list[dict]:
        """
        Метод для сбора новостей по целевой тематике.

        Args:
            search_api_url (str): Специфичный для ТАСС эндпоинт для поиска (search_url).
            tass_headers (dict): Специфичные для ТАСС заголовки.
            tass_content_url (str): Специфичный для ТАСС эндпоинт контента (content_url).
            max_retry_attempts (int): Количество попыток в течение которых будет продолжаться попытка собрать все новости со страницы. По достижению данного значения цикл будет прекращен.
            search_after (str): TimeStamp с указанием, начиная с какого периода следует искать новости. Default = None, будет автоматически перезаписано если в основном цикле > 1 итерации.
            max_collected_news (int): Целевое количество новостей, которое требуется собрать. Default = 90.

        Returns:
            list[dict]: Список словарей, где словарь содержит всю необходимую информацию по конкретной новости.
        """

        fail_counter = 0

        news_list = []

        while fail_counter != max_retry_attemps:

            current_page_news = self._get_page_news(
                search_api_url=search_api_url,
                tass_headers=tass_headers,
                search_after=search_after,
            )

            if current_page_news is None:
                fail_counter += 1
                print(f"Значение fail_counter = {fail_counter}")
                continue

            for dictionary in current_page_news:

                current_result = self._parse_single_article(
                    tass_content_url=tass_content_url,
                    news_id=str(dictionary["id"]),
                    rubrics=dictionary["url"].split("/")[1],
                    headers=tass_headers,
                )

                if current_result is not None:

                    news_list.append(current_result)  # dict

            try:

                search_after = news_list[-1][
                    "timestamp"
                ]  # Обновляем исходную дату, от которой идет поиск новостей (по убыванию)

            except:

                print("Не удалось получить следующую дату поиска! Прерываю цикл...")

            print(f"Количество собранных новостей: {len(news_list)}")

            if len(news_list) >= max_collected_news:
                print("Целевое количество новостей собрано, останавливаю цикл!")
                print(f"Количество собранных новостей: {len(news_list)}")
                break

        return news_list
