from abc import ABC, abstractmethod

class BaseScraper(ABC):

    def __init__(self,
                 scraper_name: str):

        self.scraper_name = scraper_name

    @abstractmethod
    def _get_page_news(self):
        '''
        Метод для получения всех ссылок новостей на текущей странице
        '''
        pass

    @abstractmethod
    def _parse_single_article(self):
        '''
        Метод для получения информации с одной новостной статьи
        '''
        pass