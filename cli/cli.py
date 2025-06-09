import requests, json, sys, os
from scraper.element_extractor import ElementExtractor
from scraper.link_extractor import LinkExtractor
from scraper.sitemap_generator import SitemapGenerator
from scraper.email_extractor import EmailExtractor
from scraper.image_extractor import ImageExtractor
from database.service import DatabaseService
from visualization import DataVisualizer, ReportGenerator

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
	"This script extracts data from web pages\n"
	+ bcolors.ENDC
)

options = (
	bcolors.OKCYAN + "1. Extract elements by CSS selector\n"
	+ bcolors.OKCYAN + "2. Extract all links from a page\n"
	+ bcolors.OKCYAN + "3. Extract emails from a page\n"
	+ bcolors.OKCYAN + "4. Extract all images from a page\n"
	+ bcolors.OKCYAN + "5. Generate sitemap from links\n"
	+ bcolors.OKBLUE + "6. View scraping history\n"
	+ bcolors.OKBLUE + "7. View database statistics\n"
	+ bcolors.OKBLUE + "8. Configure database settings\n"
	+ bcolors.WARNING + "9. Generate data visualizations\n"
	+ bcolors.WARNING + "q. Quit\n"
	+ bcolors.ENDC
)

url_input = (
	bcolors.OKGREEN + "Enter the URL of the page to scrape: " + bcolors.ENDC
)

def exit_message():
	print(bcolors.OKGREEN + "\nExiting the scraper. Goodbye!" + bcolors.ENDC)
	sys.exit(0)

class WebScraperCLI:
	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update({
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
		})

		# Initialize database service
		self.db_service = None
		self.db_enabled = False
		self._initialize_database()

	def _initialize_database(self):
		"""Initialize database service with default SQLite configuration"""
		try:
			self.db_service = DatabaseService(db_type="sqlite")
			if self.db_service.test_connection():
				self.db_enabled = True
				print(bcolors.OKGREEN + "✓ Database initialized successfully (SQLite)" + bcolors.ENDC)
			else:
				print(bcolors.WARNING + "⚠ Database connection failed, running in file-only mode" + bcolors.ENDC)
		except Exception as e:
			print(bcolors.WARNING + f"⚠ Database initialization failed: {str(e)}" + bcolors.ENDC)
			print(bcolors.WARNING + "Running in file-only mode" + bcolors.ENDC)

	def run(self):
		print(header)
		if self.db_enabled:
			print(bcolors.OKGREEN + "Database integration: ENABLED" + bcolors.ENDC)
		else:
			print(bcolors.WARNING + "Database integration: DISABLED (file-only mode)" + bcolors.ENDC)
		print()

		choice_actions = {
			'1': self.handle_extract_elements,
			'2': self.handle_extract_links,
			'3': self.handle_extract_emails,
			'4': self.handle_extract_images,
			'5': self.handle_generate_sitemap,
			'6': self.handle_view_history,
			'7': self.handle_view_statistics,
			'8': self.handle_configure_database,
			'9': self.handle_visualizations,
		}

		while True:
			print(options)
			try:
				choice = input(bcolors.OKGREEN + "Choose an option (1 - 9, or 'q' to quit): " + bcolors.ENDC).strip()
				if choice.lower() == 'q':
					exit_message()
				elif choice in choice_actions:
					choice_actions[choice]()
				else:
					print("Invalid option. Please try again.")
			except KeyboardInterrupt:
				exit_message()

	def _get_save_options(self):
		"""Get save options from user"""
		save_options = {
			'save_to_db': False,
			'save_to_json': False,
			'json_filename': None
		}

		if self.db_enabled:
			db_choice = input(bcolors.OKGREEN + "Save to database? (y/n): " + bcolors.ENDC).strip().lower()
			save_options['save_to_db'] = db_choice == 'y'

		json_choice = input(bcolors.OKGREEN + "Save to JSON file? (y/n): " + bcolors.ENDC).strip().lower()
		if json_choice == 'y':
			save_options['save_to_json'] = True
			filename = input(bcolors.OKGREEN + "Enter filename (or press Enter for auto-generated): " + bcolors.ENDC).strip()
			if filename:
				save_options['json_filename'] = filename

		return save_options

	def handle_extract_elements(self):
		url = input(url_input).strip()
		css_selector = input(bcolors.OKGREEN + "Enter the CSS selector: " + bcolors.ENDC).strip()

		extractor = ElementExtractor(self.session, css_selector, self.db_service)
		save_options = self._get_save_options()

		result = extractor.scrape_and_save(url, **save_options)

		if result['success']:
			elements = result['data']
			print(f"Extracted {len(elements)} elements:")
			for element in elements:
				print(element)

			if result.get('session_id'):
				print(bcolors.OKGREEN + f"✓ Data saved to database (Session ID: {result['session_id']})" + bcolors.ENDC)
			if result.get('json_filename'):
				print(bcolors.OKGREEN + f"✓ Data saved to {result['json_filename']}" + bcolors.ENDC)
		else:
			print(bcolors.FAIL + f"✗ Extraction failed: {result['error']}" + bcolors.ENDC)

	def handle_extract_links(self):
		url = input(url_input).strip()

		extractor = LinkExtractor(self.session, self.db_service)
		save_options = self._get_save_options()

		result = extractor.scrape_and_save(url, **save_options)

		if result['success']:
			links = result['data']
			print(f"Extracted {len(links)} links:")
			for link in links:
				print(link)

			if result.get('session_id'):
				print(bcolors.OKGREEN + f"✓ Data saved to database (Session ID: {result['session_id']})" + bcolors.ENDC)
			if result.get('json_filename'):
				print(bcolors.OKGREEN + f"✓ Data saved to {result['json_filename']}" + bcolors.ENDC)
		else:
			print(bcolors.FAIL + f"✗ Extraction failed: {result['error']}" + bcolors.ENDC)

	def handle_extract_emails(self):
		url = input(url_input).strip()

		extractor = EmailExtractor(self.session, self.db_service)
		save_options = self._get_save_options()

		result = extractor.scrape_and_save(url, **save_options)

		if result['success']:
			emails = result['data']
			print(f"Extracted {len(emails)} emails:")
			for email in emails:
				print(email)

			if result.get('session_id'):
				print(bcolors.OKGREEN + f"✓ Data saved to database (Session ID: {result['session_id']})" + bcolors.ENDC)
			if result.get('json_filename'):
				print(bcolors.OKGREEN + f"✓ Data saved to {result['json_filename']}" + bcolors.ENDC)
		else:
			print(bcolors.FAIL + f"✗ Extraction failed: {result['error']}" + bcolors.ENDC)

	def handle_extract_images(self):
		url = input(url_input).strip()

		extractor = ImageExtractor(self.session, self.db_service)
		save_options = self._get_save_options()

		result = extractor.scrape_and_save(url, **save_options)

		if result['success']:
			images = result['data']
			print(f"Extracted {len(images)} images:")
			for img in images:
				print(img)

			if result.get('session_id'):
				print(bcolors.OKGREEN + f"✓ Data saved to database (Session ID: {result['session_id']})" + bcolors.ENDC)
			if result.get('json_filename'):
				print(bcolors.OKGREEN + f"✓ Data saved to {result['json_filename']}" + bcolors.ENDC)
		else:
			print(bcolors.FAIL + f"✗ Extraction failed: {result['error']}" + bcolors.ENDC)

	def handle_generate_sitemap(self):
		"""Prompt user to generate a sitemap from extracted links."""
		url = input(bcolors.OKGREEN + "Enter the URL of the page to scrape links for sitemap: " + bcolors.ENDC).strip()
		extractor = LinkExtractor(self.session)
		links = extractor.scrape(url)
		if links:
			print(f"Extracted {len(links)} links for the sitemap.")
			filename = input(bcolors.OKGREEN + "Enter the filename for the sitemap (default: sitemap.xml): " + bcolors.ENDC).strip() or "sitemap.xml"
			generator = SitemapGenerator()
			generator.generate(links, filename)
		else:
			print("No links found or an error occurred.")

	def handle_view_history(self):
		"""View scraping history from database"""
		if not self.db_enabled:
			print(bcolors.WARNING + "Database not available. Cannot view history." + bcolors.ENDC)
			return

		try:
			history = self.db_service.get_extraction_history(limit=20)
			if not history:
				print("No scraping history found.")
				return

			print(f"\n{bcolors.HEADER}Recent Scraping History:{bcolors.ENDC}")
			print("-" * 80)
			for session in history:
				status_color = bcolors.OKGREEN if session['status'] == 'success' else bcolors.FAIL
				print(f"ID: {session['id']} | {session['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
				print(f"URL: {session['url']}")
				print(f"Type: {session['scraper_type']} | Status: {status_color}{session['status']}{bcolors.ENDC}")
				if session['error_message']:
					print(f"Error: {session['error_message']}")
				print("-" * 80)
		except Exception as e:
			print(bcolors.FAIL + f"Failed to retrieve history: {str(e)}" + bcolors.ENDC)

	def handle_view_statistics(self):
		"""View database statistics"""
		if not self.db_enabled:
			print(bcolors.WARNING + "Database not available. Cannot view statistics." + bcolors.ENDC)
			return

		try:
			stats = self.db_service.get_statistics()
			print(f"\n{bcolors.HEADER}Database Statistics:{bcolors.ENDC}")
			print(f"Total Sessions: {stats['total_sessions']}")
			print(f"Successful Sessions: {bcolors.OKGREEN}{stats['successful_sessions']}{bcolors.ENDC}")
			print(f"Failed Sessions: {bcolors.FAIL}{stats['failed_sessions']}{bcolors.ENDC}")
			print(f"Total Elements: {stats['total_elements']}")
			print(f"Total Links: {stats['total_links']}")
			print(f"Total Emails: {stats['total_emails']}")
			print(f"Total Images: {stats['total_images']}")
		except Exception as e:
			print(bcolors.FAIL + f"Failed to retrieve statistics: {str(e)}" + bcolors.ENDC)

	def handle_configure_database(self):
		"""Configure database settings"""
		print(f"\n{bcolors.HEADER}Database Configuration:{bcolors.ENDC}")
		print("1. SQLite (default)")
		print("2. MySQL")
		print("3. PostgreSQL")
		print("4. Test current connection")
		print("5. Back to main menu")

		choice = input(bcolors.OKGREEN + "Choose database type: " + bcolors.ENDC).strip()

		if choice == '1':
			self._configure_sqlite()
		elif choice == '2':
			self._configure_mysql()
		elif choice == '3':
			self._configure_postgresql()
		elif choice == '4':
			self._test_database_connection()
		elif choice == '5':
			return
		else:
			print("Invalid choice.")

	def _configure_sqlite(self):
		"""Configure SQLite database"""
		db_name = input(bcolors.OKGREEN + "Enter database filename (default: web_scraper.db): " + bcolors.ENDC).strip()
		if not db_name:
			db_name = "web_scraper.db"

		try:
			self.db_service = DatabaseService(db_type="sqlite", db_name=db_name)
			if self.db_service.test_connection():
				self.db_enabled = True
				print(bcolors.OKGREEN + f"✓ SQLite database configured: {db_name}" + bcolors.ENDC)
			else:
				print(bcolors.FAIL + "✗ Failed to connect to SQLite database" + bcolors.ENDC)
		except Exception as e:
			print(bcolors.FAIL + f"✗ SQLite configuration failed: {str(e)}" + bcolors.ENDC)

	def _configure_mysql(self):
		"""Configure MySQL database"""
		print(bcolors.WARNING + "MySQL configuration requires environment variables:" + bcolors.ENDC)
		print("MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE")

		proceed = input(bcolors.OKGREEN + "Continue with MySQL configuration? (y/n): " + bcolors.ENDC).strip().lower()
		if proceed != 'y':
			return

		try:
			self.db_service = DatabaseService(db_type="mysql")
			if self.db_service.test_connection():
				self.db_enabled = True
				print(bcolors.OKGREEN + "✓ MySQL database configured successfully" + bcolors.ENDC)
			else:
				print(bcolors.FAIL + "✗ Failed to connect to MySQL database" + bcolors.ENDC)
		except Exception as e:
			print(bcolors.FAIL + f"✗ MySQL configuration failed: {str(e)}" + bcolors.ENDC)

	def _configure_postgresql(self):
		"""Configure PostgreSQL database"""
		print(bcolors.WARNING + "PostgreSQL configuration requires environment variables:" + bcolors.ENDC)
		print("POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE")

		proceed = input(bcolors.OKGREEN + "Continue with PostgreSQL configuration? (y/n): " + bcolors.ENDC).strip().lower()
		if proceed != 'y':
			return

		try:
			self.db_service = DatabaseService(db_type="postgresql")
			if self.db_service.test_connection():
				self.db_enabled = True
				print(bcolors.OKGREEN + "✓ PostgreSQL database configured successfully" + bcolors.ENDC)
			else:
				print(bcolors.FAIL + "✗ Failed to connect to PostgreSQL database" + bcolors.ENDC)
		except Exception as e:
			print(bcolors.FAIL + f"✗ PostgreSQL configuration failed: {str(e)}" + bcolors.ENDC)

	def _test_database_connection(self):
		"""Test current database connection"""
		if not self.db_service:
			print(bcolors.WARNING + "No database service configured" + bcolors.ENDC)
			return

		if self.db_service.test_connection():
			print(bcolors.OKGREEN + "✓ Database connection successful" + bcolors.ENDC)
		else:
			print(bcolors.FAIL + "✗ Database connection failed" + bcolors.ENDC)

	def handle_visualizations(self):
		"""Generate data visualizations and analytics"""
		if not self.db_enabled:
			print(bcolors.WARNING + "Database not available. Visualizations require database access." + bcolors.ENDC)
			return

		print(f"\n{bcolors.HEADER}Data Visualization Options:{bcolors.ENDC}")
		print("1. Generate all visualizations")
		print("2. Create analytics dashboard")
		print("3. Generate domain analysis chart")
		print("4. Create extraction timeline")
		print("5. Generate data volume charts")
		print("6. Create success rate analysis")
		print("7. Generate comprehensive HTML report")
		print("8. Back to main menu")

		choice = input(bcolors.OKGREEN + "Choose visualization option: " + bcolors.ENDC).strip()

		try:
			visualizer = DataVisualizer(self.db_service)

			if choice == '1':
				self._generate_all_visualizations(visualizer)
			elif choice == '2':
				self._create_dashboard(visualizer)
			elif choice == '3':
				self._create_domain_analysis(visualizer)
			elif choice == '4':
				self._create_timeline(visualizer)
			elif choice == '5':
				self._create_volume_charts(visualizer)
			elif choice == '6':
				self._create_success_analysis(visualizer)
			elif choice == '7':
				self._generate_html_report(visualizer)
			elif choice == '8':
				return
			else:
				print("Invalid choice.")
		except ImportError as e:
			print(bcolors.FAIL + f"✗ Visualization dependencies not installed: {str(e)}" + bcolors.ENDC)
			print(bcolors.WARNING + "Please install required packages: pip install matplotlib seaborn plotly pandas" + bcolors.ENDC)
		except Exception as e:
			print(bcolors.FAIL + f"✗ Visualization failed: {str(e)}" + bcolors.ENDC)

	def _generate_all_visualizations(self, visualizer):
		"""Generate all available visualizations"""
		print(bcolors.OKGREEN + "Generating all visualizations..." + bcolors.ENDC)

		visualizations = visualizer.generate_all_visualizations()

		if visualizations:
			print(bcolors.OKGREEN + f"✓ Generated {len(visualizations)} visualizations:" + bcolors.ENDC)
			for name, path in visualizations.items():
				print(f"  - {name}: {path}")

			# Open visualizations folder
			open_folder = input(bcolors.OKGREEN + "Open visualizations folder? (y/n): " + bcolors.ENDC).strip().lower()
			if open_folder == 'y':
				os.system(f"xdg-open {visualizer.output_dir}")
		else:
			print(bcolors.WARNING + "No visualizations generated. Check if you have scraped data." + bcolors.ENDC)

	def _create_dashboard(self, visualizer):
		"""Create analytics dashboard"""
		print(bcolors.OKGREEN + "Creating analytics dashboard..." + bcolors.ENDC)

		dashboard_path = visualizer.create_scraping_overview_dashboard()

		if dashboard_path:
			print(bcolors.OKGREEN + f"✓ Dashboard created: {dashboard_path}" + bcolors.ENDC)

			open_dashboard = input(bcolors.OKGREEN + "Open dashboard in browser? (y/n): " + bcolors.ENDC).strip().lower()
			if open_dashboard == 'y':
				os.system(f"xdg-open {dashboard_path}")
		else:
			print(bcolors.WARNING + "Dashboard creation failed." + bcolors.ENDC)

	def _create_domain_analysis(self, visualizer):
		"""Create domain analysis chart"""
		print(bcolors.OKGREEN + "Creating domain analysis chart..." + bcolors.ENDC)

		chart_path = visualizer.create_domain_analysis_chart()

		if chart_path:
			print(bcolors.OKGREEN + f"✓ Domain analysis chart created: {chart_path}" + bcolors.ENDC)

			open_chart = input(bcolors.OKGREEN + "Open chart in browser? (y/n): " + bcolors.ENDC).strip().lower()
			if open_chart == 'y':
				os.system(f"xdg-open {chart_path}")
		else:
			print(bcolors.WARNING + "Domain analysis chart creation failed or no data available." + bcolors.ENDC)

	def _create_timeline(self, visualizer):
		"""Create extraction timeline"""
		print(bcolors.OKGREEN + "Creating extraction timeline..." + bcolors.ENDC)

		timeline_path = visualizer.create_extraction_timeline()

		if timeline_path:
			print(bcolors.OKGREEN + f"✓ Timeline created: {timeline_path}" + bcolors.ENDC)

			open_timeline = input(bcolors.OKGREEN + "Open timeline image? (y/n): " + bcolors.ENDC).strip().lower()
			if open_timeline == 'y':
				os.system(f"xdg-open {timeline_path}")
		else:
			print(bcolors.WARNING + "Timeline creation failed or no data available." + bcolors.ENDC)

	def _create_volume_charts(self, visualizer):
		"""Create data volume charts"""
		print(bcolors.OKGREEN + "Creating data volume charts..." + bcolors.ENDC)

		charts = visualizer.create_data_volume_charts()

		if charts:
			print(bcolors.OKGREEN + f"✓ Created {len(charts)} volume charts:" + bcolors.ENDC)
			for name, path in charts.items():
				print(f"  - {name}: {path}")

			open_charts = input(bcolors.OKGREEN + "Open chart images? (y/n): " + bcolors.ENDC).strip().lower()
			if open_charts == 'y':
				for path in charts.values():
					os.system(f"xdg-open {path}")
		else:
			print(bcolors.WARNING + "Volume charts creation failed or no data available." + bcolors.ENDC)

	def _create_success_analysis(self, visualizer):
		"""Create success rate analysis"""
		print(bcolors.OKGREEN + "Creating success rate analysis..." + bcolors.ENDC)

		analysis_path = visualizer.create_success_rate_analysis()

		if analysis_path:
			print(bcolors.OKGREEN + f"✓ Success analysis created: {analysis_path}" + bcolors.ENDC)

			open_analysis = input(bcolors.OKGREEN + "Open analysis image? (y/n): " + bcolors.ENDC).strip().lower()
			if open_analysis == 'y':
				os.system(f"xdg-open {analysis_path}")
		else:
			print(bcolors.WARNING + "Success analysis creation failed or no data available." + bcolors.ENDC)

	def _generate_html_report(self, visualizer):
		"""Generate comprehensive HTML report"""
		print(bcolors.OKGREEN + "Generating comprehensive HTML report..." + bcolors.ENDC)

		report_generator = ReportGenerator(visualizer)
		report_path = report_generator.generate_html_report()

		if report_path:
			print(bcolors.OKGREEN + f"✓ HTML report generated: {report_path}" + bcolors.ENDC)

			open_report = input(bcolors.OKGREEN + "Open report in browser? (y/n): " + bcolors.ENDC).strip().lower()
			if open_report == 'y':
				os.system(f"xdg-open {report_path}")
		else:
			print(bcolors.WARNING + "HTML report generation failed." + bcolors.ENDC)

def main():
	cli = WebScraperCLI()
	cli.run()

if __name__ == "__main__":
	main()
