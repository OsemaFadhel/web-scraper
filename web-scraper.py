from bs4 import BeautifulSoup
import requests
import sys
import json

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

header = (
	bcolors.HEADER + "=== Web Scraper ===\n"
	"This script extracts data from web pages.\n"
	+ bcolors.ENDC
)

options = (
	bcolors.OKBLUE + "1. Extract elements by CSS selector\n"
	+ bcolors.OKCYAN + "2. Extract all links from a page\n"
	+ bcolors.ENDC
)

class WebScraper:
	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update({
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
		})

	def fetch_page(self, url):
		try:
			page = self.session.get(url)
			page.raise_for_status()  # Raise an error for bad responses
			return page.content
		except requests.RequestException as e:
			print(f"Error fetching the page: {e}")
			return None

	def parse_html(self, html_content):
		try:
			soup = BeautifulSoup(html_content, "html.parser")
			return soup
		except Exception as e:
			print(f"Error parsing HTML content: {e}")
			return None

	def extract_elements(self, url, css_selector):
		try:
			html_content = self.fetch_page(url)
			if html_content is None:
				print("Unable to retrieve the page content.")
				return []

			# Parse the HTML content
			soup = self.parse_html(html_content)
			if soup is None:
				print("Unable to parse HTML content.")
				return []

			elements = soup.select(css_selector)
			return [element.get_text() for element in elements]
		except Exception as e:
			print(f"Error extracting elements: {e}")
			return []

	def extract_links(self, url):
		try:
			html_content = self.fetch_page(url)
			if html_content is None:
				print("Unable to retrieve the page content.")
				return []

			soup = self.parse_html(html_content)
			if soup is None:
				print("Unable to parse HTML content.")
				return []

			links = soup.find_all('a', href=True)
			for link in links:
				link['href'] = requests.compat.urljoin(url, link['href'])
			print(f"Found {len(links)} links on the page.")
			return [link['href'] for link in links]

		except Exception as e:
			print(f"Error extracting links: {e}")
			return []

	def save_to_json(self, data, filename):
		try:
			with open(filename, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
			print(f"Data saved to {filename}")
		except IOError as e:
			print(f"Error saving data to JSON: {e}")

	def choice_save(self, data):
		"""Prompt user to save data to JSON file."""
		save_choice = input(bcolors.OKGREEN + "Do you want to save the extracted data to a JSON file? (y/n): " + bcolors.ENDC).strip().lower()
		if save_choice == 'y':
			filename = input(bcolors.OKGREEN + "Enter the filename (default: output.json): " + bcolors.ENDC).strip() or "output.json"
			self.save_to_json(data, filename)
		else:
			print("Data not saved.")

	def run(self):
		print(header)
		while True:
			print(options)
			try:
				choice = input(bcolors.OKGREEN + "Choose an option (1 or 2, or 'q' to quit): "  + bcolors.ENDC).strip()
				if choice == '1':
					url = input(bcolors.OKGREEN + "Enter the URL: " + bcolors.ENDC).strip()
					css_selector = input(bcolors.OKGREEN + "Enter the CSS selector: " + bcolors.ENDC).strip()
					elements = self.extract_elements(url, css_selector)
					if elements:
						print(f"Extracted {len(elements)} elements:")
						for element in elements:
							print(element)
						self.choice_save(elements)
					else:
						print("No elements found or an error occurred.")
				elif choice == '2':
					url = input(bcolors.OKGREEN + "Enter the URL: " + bcolors.ENDC).strip()
					links = self.extract_links(url)
					if links:
						print(f"Extracted {len(links)} links:")
						for link in links:
							print(link)
						self.choice_save(links)
					else:
						print("No links found or an error occurred.")
				elif choice.lower() == 'q':
					print("Exiting the scraper. Goodbye!")
					sys.exit(0)
				else:
					print("Invalid option. Please try again.")
			except KeyboardInterrupt:
				print("\nExiting the scraper. Goodbye!")
				sys.exit(0)

def main():
	app = WebScraper()
	app.run()

if __name__ == "__main__":
	main()
