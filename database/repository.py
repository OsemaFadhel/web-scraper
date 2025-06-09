from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from .models import (
	ScrapingSession, ScrapedData, ExtractedElements,
	ExtractedLinks, ExtractedEmails, ExtractedImages
)

logger = logging.getLogger(__name__)

class BaseRepository(ABC):
	"""Base repository interface"""

	def __init__(self, db_session: Session):
		self.db_session = db_session

	@abstractmethod
	def save(self, data: Any) -> Any:
		pass

	@abstractmethod
	def find_by_id(self, id: int) -> Optional[Any]:
		pass

class ScrapingSessionRepository(BaseRepository):
	"""Repository for scraping sessions"""

	def save(self, url: str, scraper_type: str, status: str = "success",
			error_message: str = None, metadata: Dict = None) -> ScrapingSession:
		"""Create and save a new scraping session"""
		try:
			session = ScrapingSession(
				url=url,
				scraper_type=scraper_type,
				status=status,
				error_message=error_message,
				extra_data=metadata,  # Using extra_data instead of metadata
				timestamp=datetime.utcnow()
			)

			self.db_session.add(session)
			self.db_session.commit()
			self.db_session.refresh(session)

			logger.info(f"Created scraping session {session.id} for {url}")
			return session

		except Exception as e:
			self.db_session.rollback()
			logger.error(f"Failed to save scraping session: {str(e)}")
			raise

	def find_by_id(self, id: int) -> Optional[ScrapingSession]:
		"""Find scraping session by ID"""
		return self.db_session.query(ScrapingSession).filter(ScrapingSession.id == id).first()

	def find_by_url(self, url: str) -> List[ScrapingSession]:
		"""Find scraping sessions by URL"""
		return self.db_session.query(ScrapingSession).filter(ScrapingSession.url == url).all()

	def find_recent(self, limit: int = 10) -> List[ScrapingSession]:
		"""Find recent scraping sessions"""
		return (self.db_session.query(ScrapingSession)
				.order_by(ScrapingSession.timestamp.desc())
				.limit(limit).all())

class ElementRepository(BaseRepository):
	"""Repository for extracted elements"""

	def save(self, data: Any) -> Any:
		"""Generic save method (not used for elements, use save_batch instead)"""
		raise NotImplementedError("Use save_batch method for elements")

	def save_batch(self, session_id: int, css_selector: str, elements: List[str]) -> List[ExtractedElements]:
		"""Save a batch of extracted elements"""
		try:
			element_records = []
			for position, element_text in enumerate(elements):
				element_record = ExtractedElements(
					session_id=session_id,
					css_selector=css_selector,
					element_text=element_text,
					position=position
				)
				element_records.append(element_record)
				self.db_session.add(element_record)

			self.db_session.commit()
			logger.info(f"Saved {len(element_records)} elements for session {session_id}")
			return element_records

		except Exception as e:
			self.db_session.rollback()
			logger.error(f"Failed to save elements: {str(e)}")
			raise

	def find_by_id(self, id: int) -> Optional[ExtractedElements]:
		return self.db_session.query(ExtractedElements).filter(ExtractedElements.id == id).first()

	def find_by_session(self, session_id: int) -> List[ExtractedElements]:
		"""Find all elements for a session"""
		return (self.db_session.query(ExtractedElements)
				.filter(ExtractedElements.session_id == session_id)
				.order_by(ExtractedElements.position).all())

class LinkRepository(BaseRepository):
	"""Repository for extracted links"""

	def save(self, data: Any) -> Any:
		"""Generic save method (not used for links, use save_batch instead)"""
		raise NotImplementedError("Use save_batch method for links")

	def save_batch(self, session_id: int, links: List[str]) -> List[ExtractedLinks]:
		"""Save a batch of extracted links"""
		try:
			link_records = []
			for link_url in links:
				# Basic external link detection
				is_external = not (link_url.startswith('/') or 'localhost' in link_url)

				link_record = ExtractedLinks(
					session_id=session_id,
					url=link_url,
					is_external=is_external
				)
				link_records.append(link_record)
				self.db_session.add(link_record)

			self.db_session.commit()
			logger.info(f"Saved {len(link_records)} links for session {session_id}")
			return link_records

		except Exception as e:
			self.db_session.rollback()
			logger.error(f"Failed to save links: {str(e)}")
			raise

	def find_by_id(self, id: int) -> Optional[ExtractedLinks]:
		return self.db_session.query(ExtractedLinks).filter(ExtractedLinks.id == id).first()

	def find_by_session(self, session_id: int) -> List[ExtractedLinks]:
		"""Find all links for a session"""
		return (self.db_session.query(ExtractedLinks)
				.filter(ExtractedLinks.session_id == session_id).all())

class EmailRepository(BaseRepository):
	"""Repository for extracted emails"""

	def save(self, data: Any) -> Any:
		"""Generic save method (not used for emails, use save_batch instead)"""
		raise NotImplementedError("Use save_batch method for emails")

	def save_batch(self, session_id: int, emails: List[str]) -> List[ExtractedEmails]:
		"""Save a batch of extracted emails"""
		try:
			email_records = []
			for email in emails:
				email_record = ExtractedEmails(
					session_id=session_id,
					email=email
				)
				email_records.append(email_record)
				self.db_session.add(email_record)

			self.db_session.commit()
			logger.info(f"Saved {len(email_records)} emails for session {session_id}")
			return email_records

		except Exception as e:
			self.db_session.rollback()
			logger.error(f"Failed to save emails: {str(e)}")
			raise

	def find_by_id(self, id: int) -> Optional[ExtractedEmails]:
		return self.db_session.query(ExtractedEmails).filter(ExtractedEmails.id == id).first()

	def find_by_session(self, session_id: int) -> List[ExtractedEmails]:
		"""Find all emails for a session"""
		return (self.db_session.query(ExtractedEmails)
				.filter(ExtractedEmails.session_id == session_id).all())

class ImageRepository(BaseRepository):
	"""Repository for extracted images"""

	def save(self, data: Any) -> Any:
		"""Generic save method (not used for images, use save_batch instead)"""
		raise NotImplementedError("Use save_batch method for images")

	def save_batch(self, session_id: int, images: List[str]) -> List[ExtractedImages]:
		"""Save a batch of extracted images"""
		try:
			image_records = []
			for image_url in images:
				image_record = ExtractedImages(
					session_id=session_id,
					image_url=image_url
				)
				image_records.append(image_record)
				self.db_session.add(image_record)

			self.db_session.commit()
			logger.info(f"Saved {len(image_records)} images for session {session_id}")
			return image_records

		except Exception as e:
			self.db_session.rollback()
			logger.error(f"Failed to save images: {str(e)}")
			raise

	def find_by_id(self, id: int) -> Optional[ExtractedImages]:
		return self.db_session.query(ExtractedImages).filter(ExtractedImages.id == id).first()

	def find_by_session(self, session_id: int) -> List[ExtractedImages]:
		"""Find all images for a session"""
		return (self.db_session.query(ExtractedImages)
				.filter(ExtractedImages.session_id == session_id).all())
