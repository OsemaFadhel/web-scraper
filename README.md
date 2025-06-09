# Web Scraper

A simple yet powerful Python web scraper for extracting data from web pages.

![Python](https://img.shields.io/badge/python-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active%20development-yellow.svg)

## 🚀 Features

### **Current Features**
- **CSS Selector Extraction**: Extract specific elements using CSS selectors
- **Link Extraction**: Extract all links from web pages with automatic URL resolution
- **Session Management**: Persistent HTTP sessions with custom User-Agent
- **JSON Export**: Save extracted data to JSON format
- **Error Handling**: Robust error handling for network and parsing issues
- **Colored Output**: Beautiful terminal output with color-coded messages

### **Built-in Capabilities**
- Automatic relative URL resolution
- HTTP error handling with proper status codes
- HTML parsing with BeautifulSoup4
- UTF-8 encoding support for international content

## 📋 Requirements

- Python
- BeautifulSoup4
- Requests

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/web-scraper.git
   cd web-scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install beautifulsoup4 requests
   ```

3. **Run the scraper:**
   ```bash
   python web-scraper.py
   ```

## 🎯 Usage

### **Interactive Mode**
Run the script and choose from available options:

```bash
python web-scraper.py
```

**Available Options:**
1. **Extract elements by CSS selector** - Target specific HTML elements
2. **Extract all links from a page** - Get all hyperlinks with resolved URLs

### **Basic Examples**

```python
from web_scraper import WebScraper

scraper = WebScraper()

# Extract all paragraph text
paragraphs = scraper.extract_elements("https://example.com", "p")

# Extract all links
links = scraper.extract_links("https://example.com")

# Save data to JSON
scraper.save_to_json(links, "extracted_links.json")
```

## 🔧 Configuration

The scraper uses a default User-Agent string that can be customized in the [`WebScraper`](web-scraper.py) class:

```python
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

## 🚀 Planned Features

### **High Priority**
- [x] **Email Address Extraction** - Extract email addresses from web pages
- [x] **Image URL Extraction** - Download and extract image URLs
- [ ] **Table Data Extraction** - Parse HTML tables into structured data
- [ ] **Form Detection** - Identify and analyze web forms
- [x] **Sitemap Generation** - Generate sitemaps from crawled links

### **Enhanced Functionality**
- [ ] **Multi-threading** - Concurrent page processing for faster scraping
- [ ] **Rate Limiting** - Configurable delays between requests
- [ ] **Proxy Support** - Route requests through proxy servers
- [ ] **Cookie Handling** - Advanced session management with cookies
- [ ] **Authentication** - Support for basic and form-based authentication

### **Data Processing**
- [ ] **CSV Export** - Export data to CSV format
- [ ] **XML Export** - Export data to XML format
- [ ] **Database Integration** - Save data directly to databases (SQLite, MySQL, PostgreSQL)
- [ ] **Data Validation** - Validate extracted data integrity
- [ ] **Duplicate Removal** - Automatic deduplication of extracted data

### **Advanced Features**
- [ ] **JavaScript Rendering** - Support for dynamic content with Selenium
- [ ] **Content Analysis** - Text analysis and keyword extraction
- [ ] **Recursive Crawling** - Follow links automatically with depth control
- [ ] **Regular Expression Support** - Pattern-based text extraction
- [ ] **Custom Headers** - Configurable HTTP headers per request

### **User Interface**
- [ ] **Command Line Arguments** - CLI interface for automation
- [ ] **Configuration File** - YAML/JSON configuration support
- [ ] **Progress Tracking** - Real-time progress indicators
- [ ] **Logging System** - Comprehensive logging with different levels
- [ ] **GUI Interface** - Graphical user interface with tkinter/PyQt

### **Reporting & Analytics**
- [ ] **Statistics Dashboard** - Scraping statistics and analytics
- [ ] **Error Reporting** - Detailed error logs and reporting
- [ ] **Performance Metrics** - Speed and efficiency tracking
- [ ] **Data Visualization** - Charts and graphs for extracted data

## 📊 File Structure

```
web-scraper/
├── web-scraper.py          # Main scraper implementation
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── examples/              # Usage examples (planned)
    ├── basic_usage.py
    ├── advanced_features.py
    └── batch_processing.py
```

## 🤝 Contributing

**Contributions are welcome!** This project is in active development and we'd love your help.

### **How to Contribute**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **Development Areas**
- 🔧 **Core Features**: Implement planned functionality from the roadmap
- 🎨 **User Interface**: Improve CLI interface and add GUI options
- 📊 **Data Processing**: Add new export formats and data validation
- 🚀 **Performance**: Optimize scraping speed and memory usage
- 🔍 **Advanced Scraping**: JavaScript rendering and dynamic content
- 📚 **Documentation**: Improve guides, examples, and tutorials

### **Getting Started with Development**
```bash
git clone https://github.com/yourusername/web-scraper.git
cd web-scraper
pip install beautifulsoup4 requests
python web-scraper.py
```

### **Code Style**
- Follow PEP 8 Python style guidelines
- Add docstrings for all functions and classes
- Include error handling for new features
- Write tests for new functionality

## 🐛 Issues & Feature Requests

- **Bug Reports**: Use GitHub Issues with detailed reproduction steps
- **Feature Requests**: Describe your use case and proposed solution
- **Questions**: Use GitHub Discussions for general questions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Built with [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- Powered by [Requests](https://docs.python-requests.org/) for HTTP handling
- Inspired by the need for simple, effective web scraping tools

## 🚨 Disclaimer

This tool is for educational and authorized testing purposes only. Always respect website terms of service and robots.txt files. The developers are not responsible for any misuse of this tool.

---

**⭐ If you find this project useful, please give it a star!**
