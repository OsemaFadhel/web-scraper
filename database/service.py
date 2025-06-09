from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import logging

from .config import DatabaseManager
from .repository import (
	ScrapingSessionRepository, ElementRepository, LinkRepository,
	EmailRepository, ImageRepository
)

logger = logging.getLogger(__name__)

class DatabaseService:
	"""Service layer for database operations"""

	def __init__(self, db_type: str = "sqlite", db_name: Optional[str] = None):
		self.db_manager = DatabaseManager(db_type, db_name)
		self.db_manager.create_tables()

	@contextmanager
	def get_db_session(self):
		"""Context manager for database sessions"""
		session = self.db_manager.get_session()
		try:
			yield session
		except Exception as e:
			session.rollback()
			logger.error(f"Database session error: {str(e)}")
			raise
		finally:
			session.close()

	def save_element_extraction(self, url: str, css_selector: str, elements: List[str],
							metadata: Dict = None) -> int:
		"""Save element extraction results to database"""
		with self.get_db_session() as session:
			# Create repositories
			session_repo = ScrapingSessionRepository(session)
			element_repo = ElementRepository(session)

			# Create scraping session
			scraping_session = session_repo.save(
				url=url,
				scraper_type="element_extraction",
				metadata={"css_selector": css_selector, **(metadata or {})}
			)

			# Save extracted elements
			if elements:
				element_repo.save_batch(scraping_session.id, css_selector, elements)

			return scraping_session.id

	def save_link_extraction(self, url: str, links: List[str],
						metadata: Dict = None) -> int:
		"""Save link extraction results to database"""
		with self.get_db_session() as session:
			# Create repositories
			session_repo = ScrapingSessionRepository(session)
			link_repo = LinkRepository(session)

			# Create scraping session
			scraping_session = session_repo.save(
				url=url,
				scraper_type="link_extraction",
				metadata=metadata
			)

			# Save extracted links
			if links:
				link_repo.save_batch(scraping_session.id, links)

			return scraping_session.id

	def save_email_extraction(self, url: str, emails: List[str],
							metadata: Dict = None) -> int:
		"""Save email extraction results to database"""
		with self.get_db_session() as session:
			# Create repositories
			session_repo = ScrapingSessionRepository(session)
			email_repo = EmailRepository(session)

			# Create scraping session
			scraping_session = session_repo.save(
				url=url,
				scraper_type="email_extraction",
				metadata=metadata
			)

			# Save extracted emails
			if emails:
				email_repo.save_batch(scraping_session.id, emails)

			return scraping_session.id

	def save_image_extraction(self, url: str, images: List[str],
							metadata: Dict = None) -> int:
		"""Save image extraction results to database"""
		with self.get_db_session() as session:
			# Create repositories
			session_repo = ScrapingSessionRepository(session)
			image_repo = ImageRepository(session)

			# Create scraping session
			scraping_session = session_repo.save(
				url=url,
				scraper_type="image_extraction",
				metadata=metadata
			)

			# Save extracted images
			if images:
				image_repo.save_batch(scraping_session.id, images)

			return scraping_session.id

	def save_failed_extraction(self, url: str, scraper_type: str,
							error_message: str, metadata: Dict = None) -> int:
		"""Save failed extraction attempt to database"""
		with self.get_db_session() as session:
			session_repo = ScrapingSessionRepository(session)

			scraping_session = session_repo.save(
				url=url,
				scraper_type=scraper_type,
				status="failed",
				error_message=error_message,
				metadata=metadata
			)

			return scraping_session.id

	def get_extraction_history(self, url: Optional[str] = None,
							limit: int = 10) -> List[Dict]:
		"""Get extraction history"""
		with self.get_db_session() as session:
			session_repo = ScrapingSessionRepository(session)

			if url:
				sessions = session_repo.find_by_url(url)
			else:
				sessions = session_repo.find_recent(limit)

			return [
				{
					"id": s.id,
					"url": s.url,
					"scraper_type": s.scraper_type,
					"timestamp": s.timestamp,
					"status": s.status,
					"error_message": s.error_message,
					"metadata": s.extra_data  # Using extra_data field
				}
				for s in sessions
			]

	def get_session_data(self, session_id: int) -> Optional[Dict]:
		"""Get all data for a specific scraping session"""
		with self.get_db_session() as session:
			session_repo = ScrapingSessionRepository(session)
			element_repo = ElementRepository(session)
			link_repo = LinkRepository(session)
			email_repo = EmailRepository(session)
			image_repo = ImageRepository(session)

			# Get session info
			scraping_session = session_repo.find_by_id(session_id)
			if not scraping_session:
				return None

			result = {
				"session": {
					"id": scraping_session.id,
					"url": scraping_session.url,
					"scraper_type": scraping_session.scraper_type,
					"timestamp": scraping_session.timestamp,
					"status": scraping_session.status,
					"metadata": scraping_session.extra_data  # Using extra_data field
				},
				"data": {}
			}

			# Get specific data based on scraper type
			if scraping_session.scraper_type == "element_extraction":
				elements = element_repo.find_by_session(session_id)
				result["data"]["elements"] = [
					{
						"text": e.element_text,
						"css_selector": e.css_selector,
						"position": e.position
					}
					for e in elements
				]
			elif scraping_session.scraper_type == "link_extraction":
				links = link_repo.find_by_session(session_id)
				result["data"]["links"] = [
					{
						"url": l.url,
						"is_external": l.is_external,
						"is_valid": l.is_valid
					}
					for l in links
				]
			elif scraping_session.scraper_type == "email_extraction":
				emails = email_repo.find_by_session(session_id)
				result["data"]["emails"] = [e.email for e in emails]
			elif scraping_session.scraper_type == "image_extraction":
				images = image_repo.find_by_session(session_id)
				result["data"]["images"] = [
					{
						"url": i.image_url,
						"alt_text": i.alt_text,
						"title": i.title
					}
					for i in images
				]

			return result

	def test_connection(self) -> bool:
		"""Test database connection"""
		return self.db_manager.test_connection()

	def get_statistics(self) -> Dict:
		"""Get scraping statistics"""
		with self.get_db_session() as session:
			from .models import ScrapingSession, ExtractedElements, ExtractedLinks, ExtractedEmails, ExtractedImages

			stats = {
				"total_sessions": session.query(ScrapingSession).count(),
				"successful_sessions": session.query(ScrapingSession).filter(ScrapingSession.status == "success").count(),
				"failed_sessions": session.query(ScrapingSession).filter(ScrapingSession.status == "failed").count(),
				"total_elements": session.query(ExtractedElements).count(),
				"total_links": session.query(ExtractedLinks).count(),
				"total_emails": session.query(ExtractedEmails).count(),
				"total_images": session.query(ExtractedImages).count(),
			}

			return stats
