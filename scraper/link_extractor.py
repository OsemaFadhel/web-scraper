from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import List

class LinkExtractor(BaseScraper):
	def __init__(self, session, database_service=None):
		super().__init__(session, database_service)

	def scrape(self, url):
		response = self.session.get(url)
		response.raise_for_status()
		soup = BeautifulSoup(response.content, "html.parser")
		return [a['href'] for a in soup.find_all('a', href=True)]

	def _save_to_database(self, url: str, data: List[str], **kwargs) -> int:
		"""Save link extraction data to database"""
		if not self.database_service:
			raise ValueError("Database service not configured")

		return self.database_service.save_link_extraction(
			url=url,
			links=data,
			metadata=kwargs
		)
