import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from typing import Optional
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConfig:
	"""Database configuration management"""

	@staticmethod
	def get_sqlite_url(db_name: str = "web_scraper.db") -> str:
		"""Get SQLite database URL"""
		db_path = os.path.join(os.getcwd(), "data", db_name)
		os.makedirs(os.path.dirname(db_path), exist_ok=True)
		return f"sqlite:///{db_path}"

	@staticmethod
	def get_mysql_url() -> str:
		"""Get MySQL database URL from environment variables"""
		host = os.getenv('MYSQL_HOST', 'localhost')
		port = os.getenv('MYSQL_PORT', '3306')
		user = os.getenv('MYSQL_USER', 'root')
		password = os.getenv('MYSQL_PASSWORD', '')
		database = os.getenv('MYSQL_DATABASE', 'web_scraper')

		return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

	@staticmethod
	def get_postgresql_url() -> str:
		"""Get PostgreSQL database URL from environment variables"""
		host = os.getenv('POSTGRES_HOST', 'localhost')
		port = os.getenv('POSTGRES_PORT', '5432')
		user = os.getenv('POSTGRES_USER', 'postgres')
		password = os.getenv('POSTGRES_PASSWORD', '')
		database = os.getenv('POSTGRES_DATABASE', 'web_scraper')

		return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

class DatabaseManager:
	"""Manages database connections and sessions"""

	def __init__(self, db_type: str = "sqlite", db_name: Optional[str] = None):
		self.db_type = db_type.lower()
		self.engine = None
		self.SessionLocal = None
		self._initialize_database(db_name)

	def _initialize_database(self, db_name: Optional[str] = None):
		"""Initialize database connection based on type"""
		try:
			if self.db_type == "sqlite":
				url = DatabaseConfig.get_sqlite_url(db_name or "web_scraper.db")
				self.engine = create_engine(
					url,
					connect_args={"check_same_thread": False},
					echo=False
				)
			elif self.db_type == "mysql":
				url = DatabaseConfig.get_mysql_url()
				self.engine = create_engine(
					url,
					poolclass=QueuePool,
					pool_size=10,
					max_overflow=20,
					echo=False
				)
			elif self.db_type == "postgresql":
				url = DatabaseConfig.get_postgresql_url()
				self.engine = create_engine(
					url,
					poolclass=QueuePool,
					pool_size=10,
					max_overflow=20,
					echo=False
				)
			else:
				raise ValueError(f"Unsupported database type: {self.db_type}")

			self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
			logger.info(f"Database connection established: {self.db_type}")

		except Exception as e:
			logger.error(f"Failed to initialize database: {str(e)}")
			raise

	def get_session(self):
		"""Get a database session"""
		return self.SessionLocal()

	def create_tables(self):
		"""Create all database tables"""
		from .models import Base
		try:
			Base.metadata.create_all(bind=self.engine)
			logger.info("Database tables created successfully")
		except Exception as e:
			logger.error(f"Failed to create tables: {str(e)}")
			raise

	def drop_tables(self):
		"""Drop all database tables (use with caution)"""
		from .models import Base
		try:
			Base.metadata.drop_all(bind=self.engine)
			logger.info("Database tables dropped successfully")
		except Exception as e:
			logger.error(f"Failed to drop tables: {str(e)}")
			raise

	def test_connection(self) -> bool:
		"""Test database connection"""
		try:
			from sqlalchemy import text
			with self.engine.connect() as connection:
				connection.execute(text("SELECT 1"))
			return True
		except Exception as e:
			logger.error(f"Database connection test failed: {str(e)}")
			return False
