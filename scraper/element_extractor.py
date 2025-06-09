from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import List

class ElementExtractor(BaseScraper):
	def __init__(self, session, css_selector, database_service=None):
		super().__init__(session, database_service)
		self.css_selector = css_selector

	def scrape(self, url):
		response = self.session.get(url)
		response.raise_for_status()
		soup = BeautifulSoup(response.content, "html.parser")
		return [element.get_text() for element in soup.select(self.css_selector)]

	def _save_to_database(self, url: str, data: List[str], **kwargs) -> int:
		"""Save element extraction data to database"""
		if not self.database_service:
			raise ValueError("Database service not configured")

		return self.database_service.save_element_extraction(
			url=url,
			css_selector=self.css_selector,
			elements=data,
			metadata=kwargs
		)
