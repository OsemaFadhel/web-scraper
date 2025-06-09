from bs4 import BeautifulSoup

def parse_html(content):
	try:
		return BeautifulSoup(content, "html.parser")
	except Exception as e:
		print(f"Error parsing HTML: {e}")
		return None
