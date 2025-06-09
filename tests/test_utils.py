import unittest
from utils.file_utils import save_to_json
from utils.html_utils import parse_html

class TestUtils(unittest.TestCase):
	def test_save_to_json(self):
		data = {"key": "value"}
		filename = "test_output.json"
		save_to_json(data, filename)
		with open(filename, "r") as f:
			content = f.read()
		self.assertIn("key", content)

	def test_parse_html(self):
		html_content = "<html><body><p>Test</p></body></html>"
		soup = parse_html(html_content)
		self.assertIsNotNone(soup)
		self.assertEqual(soup.find("p").text, "Test")

if __name__ == "__main__":
	unittest.main()
