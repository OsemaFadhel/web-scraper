class SitemapGenerator:
	def generate(self, links, filename="sitemap"):
		urlset = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
		for link in links:
			urlset += f"  <url>\n    <loc>{link}</loc>\n  </url>\n"
		urlset += "</urlset>\n"

		filename = f"{filename}.xml"
		with open(filename, "w", encoding="utf-8") as f:
			f.write(urlset)
		print(f"Sitemap saved to {filename}")
