from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import requests
from typing import List

class ImageExtractor(BaseScraper):
	def __init__(self, session, database_service=None):
		super().__init__(session, database_service)

	def scrape(self, url):
		try:
			response = self.session.get(url)
			response.raise_for_status()
			soup = BeautifulSoup(response.content, "html.parser")

			images = soup.find_all('img', src=True)
			for img in images:
				img['src'] = requests.compat.urljoin(url, img['src'])
			print(f"Found {len(images)} images on the page.")
			return [img['src'] for img in images]
		except Exception as e:
			print(f"Error extracting images: {e}")
			return []

	def _save_to_database(self, url: str, data: List[str], **kwargs) -> int:
		"""Save image extraction data to database"""
		if not self.database_service:
			raise ValueError("Database service not configured")

		return self.database_service.save_image_extraction(
			url=url,
			images=data,
			metadata=kwargs
		)
