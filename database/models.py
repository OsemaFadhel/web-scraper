from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ScrapingSession(Base):
	"""Represents a scraping session with metadata"""
	__tablename__ = 'scraping_sessions'

	id = Column(Integer, primary_key=True, autoincrement=True)
	url = Column(String(2048), nullable=False)
	scraper_type = Column(String(100), nullable=False)  # element, link, email, image
	timestamp = Column(DateTime, default=datetime.utcnow)
	status = Column(String(50), default='success')  # success, failed, partial
	error_message = Column(Text, nullable=True)
	extra_data = Column(JSON, nullable=True)  # Store additional scraping parameters (renamed from metadata)

	# Relationships
	scraped_data = relationship("ScrapedData", back_populates="session", cascade="all, delete-orphan")

class ScrapedData(Base):
	"""Stores the actual scraped data"""
	__tablename__ = 'scraped_data'

	id = Column(Integer, primary_key=True, autoincrement=True)
	session_id = Column(Integer, ForeignKey('scraping_sessions.id'), nullable=False)
	data_type = Column(String(50), nullable=False)  # text, link, email, image_url
	content = Column(Text, nullable=False)
	additional_info = Column(JSON, nullable=True)  # Store extra attributes like alt text for images
	created_at = Column(DateTime, default=datetime.utcnow)

	# Relationships
	session = relationship("ScrapingSession", back_populates="scraped_data")

class ExtractedElements(Base):
	"""Specialized table for element extraction results"""
	__tablename__ = 'extracted_elements'

	id = Column(Integer, primary_key=True, autoincrement=True)
	session_id = Column(Integer, ForeignKey('scraping_sessions.id'), nullable=False)
	css_selector = Column(String(500), nullable=False)
	element_text = Column(Text, nullable=False)
	element_html = Column(Text, nullable=True)
	position = Column(Integer, nullable=True)  # Order on page
	created_at = Column(DateTime, default=datetime.utcnow)

class ExtractedLinks(Base):
	"""Specialized table for link extraction results"""
	__tablename__ = 'extracted_links'

	id = Column(Integer, primary_key=True, autoincrement=True)
	session_id = Column(Integer, ForeignKey('scraping_sessions.id'), nullable=False)
	url = Column(String(2048), nullable=False)
	link_text = Column(Text, nullable=True)
	is_external = Column(Boolean, default=False)
	is_valid = Column(Boolean, default=True)
	created_at = Column(DateTime, default=datetime.utcnow)

class ExtractedEmails(Base):
	"""Specialized table for email extraction results"""
	__tablename__ = 'extracted_emails'

	id = Column(Integer, primary_key=True, autoincrement=True)
	session_id = Column(Integer, ForeignKey('scraping_sessions.id'), nullable=False)
	email = Column(String(320), nullable=False)  # Max email length per RFC 5321
	context = Column(Text, nullable=True)  # Surrounding text context
	is_validated = Column(Boolean, default=False)
	created_at = Column(DateTime, default=datetime.utcnow)

class ExtractedImages(Base):
	"""Specialized table for image extraction results"""
	__tablename__ = 'extracted_images'

	id = Column(Integer, primary_key=True, autoincrement=True)
	session_id = Column(Integer, ForeignKey('scraping_sessions.id'), nullable=False)
	image_url = Column(String(2048), nullable=False)
	alt_text = Column(Text, nullable=True)
	title = Column(Text, nullable=True)
	width = Column(Integer, nullable=True)
	height = Column(Integer, nullable=True)
	file_size = Column(Integer, nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow)
