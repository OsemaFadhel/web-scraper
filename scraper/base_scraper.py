from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
	"""Enhanced base scraper with database integration"""

	def __init__(self, session=None, database_service=None):
		self.session = session
		self.database_service = database_service
		self.logger = logging.getLogger(self.__class__.__name__)

	@abstractmethod
	def scrape(self, url: str) -> List[Any]:
		"""Scrape data from the given URL."""
		pass

	def scrape_and_save(self, url: str, save_to_db: bool = False,
					save_to_json: bool = False, json_filename: str = None,
					**kwargs) -> Dict[str, Any]:
		"""
		Scrape data and optionally save to database and/or JSON file

		Returns:
			Dict containing scraped data and metadata
		"""
		result = {
			"url": url,
			"success": False,
			"data": [],
			"error": None,
			"session_id": None,
			"scraper_type": self.__class__.__name__.lower().replace('extractor', '_extraction')
		}

		try:
			# Perform scraping
			scraped_data = self.scrape(url)
			result["data"] = scraped_data
			result["success"] = True

			# Save to database if requested
			if save_to_db and self.database_service:
				try:
					session_id = self._save_to_database(url, scraped_data, **kwargs)
					result["session_id"] = session_id
					self.logger.info(f"Data saved to database with session ID: {session_id}")
				except Exception as db_error:
					self.logger.error(f"Failed to save to database: {str(db_error)}")
					result["db_error"] = str(db_error)

			# Save to JSON if requested
			if save_to_json:
				try:
					from utils.file_utils import save_to_json
					filename = json_filename or f"{result['scraper_type']}_{url.replace('://', '_').replace('/', '_')}.json"
					save_to_json(scraped_data, filename)
					result["json_filename"] = filename
				except Exception as json_error:
					self.logger.error(f"Failed to save to JSON: {str(json_error)}")
					result["json_error"] = str(json_error)

		except Exception as e:
			result["error"] = str(e)
			result["success"] = False
			self.logger.error(f"Scraping failed for {url}: {str(e)}")

			# Save failed attempt to database if enabled
			if save_to_db and self.database_service:
				try:
					session_id = self.database_service.save_failed_extraction(
						url=url,
						scraper_type=result["scraper_type"],
						error_message=str(e),
						metadata=kwargs
					)
					result["session_id"] = session_id
				except Exception as db_error:
					self.logger.error(f"Failed to save error to database: {str(db_error)}")

		return result

	@abstractmethod
	def _save_to_database(self, url: str, data: List[Any], **kwargs) -> int:
		"""Save scraped data to database. Must be implemented by subclasses."""
		pass
