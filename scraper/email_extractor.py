from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import List

class EmailExtractor(BaseScraper):
	def __init__(self, session, database_service=None):
		super().__init__(session, database_service)

	def scrape(self, url):
		response = self.session.get(url)
		response.raise_for_status()
		soup = BeautifulSoup(response.content, "html.parser")
		emails = set()
		for a in soup.find_all('a', href=True):
			if 'mailto:' in a['href']:
				email = a['href'].split('mailto:')[1]
				emails.add(email)
		return list(emails)

	def _save_to_database(self, url: str, data: List[str], **kwargs) -> int:
		"""Save email extraction data to database"""
		if not self.database_service:
			raise ValueError("Database service not configured")

		return self.database_service.save_email_extraction(
			url=url,
			emails=data,
			metadata=kwargs
		)
