import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from scraper.element_extractor import ElementExtractor
from scraper.link_extractor import LinkExtractor
from scraper.email_extractor import EmailExtractor
from scraper.image_extractor import ImageExtractor
from scraper.sitemap_generator import SitemapGenerator
import requests

class TestScraper(unittest.TestCase):
	def setUp(self):
		self.session = requests.Session()
		self.session.headers.update({"User-Agent": "TestAgent"})
		self.test_url = "https://example.com"

	def test_element_extractor(self):
		extractor = ElementExtractor(self.session, "p")
		result = extractor.scrape(self.test_url)
		self.assertIsInstance(result, list)

	def test_link_extractor(self):
		extractor = LinkExtractor(self.session)
		result = extractor.scrape(self.test_url)
		self.assertIsInstance(result, list)

	def test_email_extractor(self):
		extractor = EmailExtractor(self.session)
		result = extractor.scrape(self.test_url)
		self.assertIsInstance(result, list)

	def test_image_extractor(self):
		extractor = ImageExtractor(self.session)
		result = extractor.scrape(self.test_url)
		self.assertIsInstance(result, list)

	def test_sitemap_generator(self):
		generator = SitemapGenerator()
		links = ["https://example.com/page1", "https://example.com/page2"]
		generator.generate(links, "test_sitemap.xml")
		with open("test_sitemap.xml", "r") as f:
			content = f.read()
		self.assertIn("<urlset", content)

if __name__ == "__main__":
	unittest.main()
