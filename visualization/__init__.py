"""
Data Visualization Module for Web Scraper
Provides comprehensive charts, graphs, and analytics for extracted data
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple, Any

class DataVisualizer:
	"""Main visualization class for generating charts and graphs"""

	def __init__(self, db_service=None, output_dir="visualizations"):
		self.db_service = db_service
		self.output_dir = output_dir
		self.ensure_output_directory()

		# Set style for matplotlib
		try:
			plt.style.use('seaborn-v0_8')
		except:
			# Fallback to default style if seaborn style not available
			plt.style.use('default')
		sns.set_palette("husl")

	def ensure_output_directory(self):
		"""Create output directory if it doesn't exist"""
		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)

	def get_scraping_data(self) -> pd.DataFrame:
		"""Get all scraping data from database using the service layer"""
		if not self.db_service:
			return pd.DataFrame()

		try:
			# Get all sessions from the database service
			sessions = self.db_service.get_extraction_history(limit=1000)  # Get more data for better visualization

			if not sessions:
				return pd.DataFrame()

			# Convert to DataFrame
			df_data = []
			for session in sessions:
				# Count results based on session type
				result_count = 0
				if session.get('metadata') and isinstance(session['metadata'], dict):
					result_count = session['metadata'].get('result_count', 0)

				df_data.append({
					'url': session['url'],
					'extraction_type': session['scraper_type'],
					'result_count': result_count,
					'success': session['status'] == 'success',
					'timestamp': session['timestamp'],
					'error_message': session.get('error_message', ''),
					'session_id': session['id']
				})

			df = pd.DataFrame(df_data)

			if df.empty:
				return df

			# Convert timestamp to datetime
			df['timestamp'] = pd.to_datetime(df['timestamp'])
			df['date'] = df['timestamp'].dt.date
			df['hour'] = df['timestamp'].dt.hour

			# Extract domain from URL
			df['domain'] = df['url'].apply(lambda x: urlparse(x).netloc if x else '')

			return df
		except Exception as e:
			print(f"Error getting scraping data: {e}")
			return pd.DataFrame()

	def create_scraping_overview_dashboard(self) -> Optional[str]:
		"""Create comprehensive dashboard with multiple charts"""
		df = self.get_scraping_data()
		if df.empty:
			print("No data available for visualization")
			return None

		try:
			# Create subplots
			fig = make_subplots(
				rows=2, cols=2,
				subplot_titles=(
					'Extractions by Type',
					'Success Rate by Domain',
					'Daily Extraction Volume',
					'Hourly Activity Pattern'
				),
				specs=[[{"type": "pie"}, {"type": "bar"}],
					[{"type": "scatter"}, {"type": "bar"}]]
			)

			# 1. Extraction types pie chart
			type_counts = df['extraction_type'].value_counts()
			fig.add_trace(
				go.Pie(labels=type_counts.index, values=type_counts.values, name="Types"),
				row=1, col=1
			)

			# 2. Success rate by domain
			domain_success = df.groupby('domain').agg({
				'success': ['count', 'sum']
			}).round(2)
			domain_success.columns = ['total', 'successful']
			domain_success['success_rate'] = (domain_success['successful'] / domain_success['total'] * 100).round(1)
			domain_success = domain_success.sort_values('total', ascending=False).head(10)

			if not domain_success.empty:
				fig.add_trace(
					go.Bar(
						x=domain_success.index,
						y=domain_success['success_rate'],
						name="Success Rate %"
					),
					row=1, col=2
				)

			# 3. Daily extraction volume
			daily_counts = df.groupby('date').size().reset_index(name='count')
			fig.add_trace(
				go.Scatter(
					x=daily_counts['date'],
					y=daily_counts['count'],
					mode='lines+markers',
					name="Daily Volume"
				),
				row=2, col=1
			)

			# 4. Hourly activity pattern
			hourly_counts = df.groupby('hour').size()
			fig.add_trace(
				go.Bar(
					x=hourly_counts.index,
					y=hourly_counts.values,
					name="Hourly Activity"
				),
				row=2, col=2
			)

			fig.update_layout(
				title_text="Web Scraping Analytics Dashboard",
				showlegend=False,
				height=800
			)

			output_file = os.path.join(self.output_dir, "scraping_dashboard.html")
			fig.write_html(output_file)
			return output_file
		except Exception as e:
			print(f"Error creating dashboard: {e}")
			return None

	def create_extraction_timeline(self) -> Optional[str]:
		"""Create timeline chart of extractions"""
		df = self.get_scraping_data()
		if df.empty:
			return None

		plt.figure(figsize=(15, 8))

		# Group by date and extraction type
		timeline_data = df.groupby(['date', 'extraction_type']).size().unstack(fill_value=0)

		# Create stacked area chart
		timeline_data.plot(kind='area', stacked=True, alpha=0.7, figsize=(15, 8))

		plt.title('Extraction Timeline by Type', fontsize=16, fontweight='bold')
		plt.xlabel('Date', fontsize=12)
		plt.ylabel('Number of Extractions', fontsize=12)
		plt.legend(title='Extraction Type', bbox_to_anchor=(1.05, 1), loc='upper left')
		plt.xticks(rotation=45)
		plt.tight_layout()

		output_file = os.path.join(self.output_dir, "extraction_timeline.png")
		plt.savefig(output_file, dpi=300, bbox_inches='tight')
		plt.close()
		return output_file

	def create_domain_analysis_chart(self) -> Optional[str]:
		"""Create domain analysis with interactive chart"""
		df = self.get_scraping_data()
		if df.empty:
			return None

		# Analyze domains
		domain_stats = df.groupby('domain').agg({
			'url': 'count',
			'result_count': 'sum',
			'success': 'mean'
		}).round(3)
		domain_stats.columns = ['total_requests', 'total_results', 'success_rate']
		domain_stats = domain_stats.sort_values('total_requests', ascending=False).head(15)

		# Create interactive chart
		fig = go.Figure()

		# Add bar chart for total requests
		fig.add_trace(go.Bar(
			name='Total Requests',
			x=domain_stats.index,
			y=domain_stats['total_requests'],
			yaxis='y',
			offsetgroup=1
		))

		# Add line chart for success rate
		fig.add_trace(go.Scatter(
			name='Success Rate',
			x=domain_stats.index,
			y=domain_stats['success_rate'] * 100,
			yaxis='y2',
			mode='lines+markers',
			line=dict(color='red', width=3)
		))

		fig.update_layout(
			title='Domain Analysis: Requests vs Success Rate',
			xaxis=dict(title='Domain', tickangle=45),
			yaxis=dict(title='Total Requests', side='left'),
			yaxis2=dict(title='Success Rate (%)', side='right', overlaying='y'),
			hovermode='x unified',
			height=600
		)

		output_file = os.path.join(self.output_dir, "domain_analysis.html")
		fig.write_html(output_file)
		return output_file

	def create_data_volume_charts(self) -> Dict[str, str]:
		"""Create various data volume visualization charts"""
		df = self.get_scraping_data()
		if df.empty:
			return {}

		charts = {}

		# 1. Results per extraction type
		plt.figure(figsize=(12, 6))
		type_results = df.groupby('extraction_type')['result_count'].sum().sort_values(ascending=False)

		plt.subplot(1, 2, 1)
		bars = plt.bar(type_results.index, type_results.values, color=plt.cm.Set3(range(len(type_results))))
		plt.title('Total Results by Extraction Type', fontweight='bold')
		plt.xlabel('Extraction Type')
		plt.ylabel('Total Results')
		plt.xticks(rotation=45)

		# Add value labels on bars
		for bar in bars:
			height = bar.get_height()
			plt.text(bar.get_x() + bar.get_width()/2., height,
					f'{int(height):,}', ha='center', va='bottom')

		# 2. Average results per request
		plt.subplot(1, 2, 2)
		avg_results = df.groupby('extraction_type')['result_count'].mean().sort_values(ascending=False)
		bars = plt.bar(avg_results.index, avg_results.values, color=plt.cm.Pastel1(range(len(avg_results))))
		plt.title('Average Results per Request', fontweight='bold')
		plt.xlabel('Extraction Type')
		plt.ylabel('Average Results')
		plt.xticks(rotation=45)

		# Add value labels on bars
		for bar in bars:
			height = bar.get_height()
			plt.text(bar.get_x() + bar.get_width()/2., height,
					f'{height:.1f}', ha='center', va='bottom')

		plt.tight_layout()
		output_file = os.path.join(self.output_dir, "data_volume_charts.png")
		plt.savefig(output_file, dpi=300, bbox_inches='tight')
		plt.close()
		charts['Data Volume Charts'] = output_file

		# 3. Heatmap of activity by day and hour
		if len(df) > 10:  # Only create if we have enough data
			plt.figure(figsize=(12, 8))

			# Create pivot table for heatmap
			df['day_of_week'] = df['timestamp'].dt.day_name()
			heatmap_data = df.pivot_table(
				values='result_count',
				index='day_of_week',
				columns='hour',
				aggfunc='sum',
				fill_value=0
			)

			# Reorder days
			day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
			heatmap_data = heatmap_data.reindex([day for day in day_order if day in heatmap_data.index])

			sns.heatmap(heatmap_data, annot=True, fmt='g', cmap='YlOrRd', cbar_kws={'label': 'Total Results'})
			plt.title('Activity Heatmap: Results by Day and Hour', fontsize=14, fontweight='bold')
			plt.xlabel('Hour of Day')
			plt.ylabel('Day of Week')
			plt.tight_layout()

			heatmap_file = os.path.join(self.output_dir, "activity_heatmap.png")
			plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
			plt.close()
			charts['Activity Heatmap'] = heatmap_file

		return charts

	def create_success_rate_analysis(self) -> Optional[str]:
		"""Create success rate analysis chart"""
		df = self.get_scraping_data()
		if df.empty:
			return None

		fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

		# 1. Overall success rate pie chart
		success_counts = df['success'].value_counts()
		success_labels = ['Success', 'Failed']
		colors = ['#2ecc71', '#e74c3c']

		wedges, texts, autotexts = ax1.pie(
			success_counts.values,
			labels=success_labels,
			colors=colors,
			autopct='%1.1f%%',
			startangle=90
		)
		ax1.set_title('Overall Success Rate', fontweight='bold')

		# 2. Success rate by extraction type
		type_success = df.groupby('extraction_type')['success'].mean() * 100
		bars = ax2.bar(type_success.index, type_success.values, color=plt.cm.Set2(range(len(type_success))))
		ax2.set_title('Success Rate by Extraction Type', fontweight='bold')
		ax2.set_ylabel('Success Rate (%)')
		ax2.set_xticklabels(type_success.index, rotation=45)

		# Add percentage labels
		for bar in bars:
			height = bar.get_height()
			ax2.text(bar.get_x() + bar.get_width()/2., height,
					f'{height:.1f}%', ha='center', va='bottom')

		# 3. Success rate trend over time
		daily_success = df.groupby('date')['success'].mean() * 100
		ax3.plot(daily_success.index, daily_success.values, marker='o', linewidth=2, markersize=6)
		ax3.set_title('Success Rate Trend Over Time', fontweight='bold')
		ax3.set_ylabel('Success Rate (%)')
		ax3.set_xlabel('Date')
		ax3.tick_params(axis='x', rotation=45)
		ax3.grid(True, alpha=0.3)

		# 4. Error analysis (if there are errors)
		error_df = df[df['success'] == False]
		if not error_df.empty and 'error_message' in error_df.columns:
			error_counts = error_df['error_message'].value_counts().head(5)
			if not error_counts.empty:
				bars = ax4.barh(range(len(error_counts)), error_counts.values, color='#e74c3c')
				ax4.set_yticks(range(len(error_counts)))
				ax4.set_yticklabels([msg[:30] + '...' if len(msg) > 30 else msg for msg in error_counts.index])
				ax4.set_title('Most Common Errors', fontweight='bold')
				ax4.set_xlabel('Frequency')

				# Add count labels
				for i, bar in enumerate(bars):
					width = bar.get_width()
					ax4.text(width, bar.get_y() + bar.get_height()/2.,
							f'{int(width)}', ha='left', va='center')
			else:
				ax4.text(0.5, 0.5, 'No error data available', ha='center', va='center', transform=ax4.transAxes)
				ax4.set_title('Error Analysis', fontweight='bold')
		else:
			ax4.text(0.5, 0.5, 'No failed extractions found', ha='center', va='center', transform=ax4.transAxes)
			ax4.set_title('Error Analysis', fontweight='bold')

		plt.tight_layout()
		output_file = os.path.join(self.output_dir, "success_rate_analysis.png")
		plt.savefig(output_file, dpi=300, bbox_inches='tight')
		plt.close()
		return output_file

	def generate_all_visualizations(self) -> Dict[str, str]:
		"""Generate all available visualizations"""
		visualizations = {}

		print("🎨 Generating visualizations...")

		# Generate dashboard
		print("  📊 Creating interactive dashboard...")
		dashboard = self.create_scraping_overview_dashboard()
		if dashboard:
			visualizations['Interactive Dashboard'] = dashboard

		# Generate timeline
		print("  📈 Creating extraction timeline...")
		timeline = self.create_extraction_timeline()
		if timeline:
			visualizations['Extraction Timeline'] = timeline

		# Generate domain analysis
		print("  🌐 Creating domain analysis...")
		domain_analysis = self.create_domain_analysis_chart()
		if domain_analysis:
			visualizations['Domain Analysis'] = domain_analysis

		# Generate volume charts
		print("  📊 Creating data volume charts...")
		volume_charts = self.create_data_volume_charts()
		visualizations.update(volume_charts)

		# Generate success analysis
		print("  ✅ Creating success rate analysis...")
		success_analysis = self.create_success_rate_analysis()
		if success_analysis:
			visualizations['Success Rate Analysis'] = success_analysis

		return visualizations

	def get_enhanced_scraping_data(self) -> pd.DataFrame:
		"""Get enhanced scraping data with actual result counts from session data"""
		if not self.db_service:
			return pd.DataFrame()

		try:
			# Get all sessions
			sessions = self.db_service.get_extraction_history(limit=1000)

			if not sessions:
				return pd.DataFrame()

			# Get detailed data for each session
			df_data = []
			for session in sessions:
				session_data = self.db_service.get_session_data(session['id'])

				if session_data:
					# Calculate actual result count based on data
					result_count = 0
					if 'data' in session_data:
						data = session_data['data']
						if 'elements' in data:
							result_count = len(data['elements'])
						elif 'links' in data:
							result_count = len(data['links'])
						elif 'emails' in data:
							result_count = len(data['emails'])
						elif 'images' in data:
							result_count = len(data['images'])

					df_data.append({
						'url': session['url'],
						'extraction_type': session['scraper_type'],
						'result_count': result_count,
						'success': session['status'] == 'success',
						'timestamp': session['timestamp'],
						'error_message': session.get('error_message', ''),
						'session_id': session['id']
					})

			df = pd.DataFrame(df_data)

			if df.empty:
				return df

			# Convert timestamp to datetime
			df['timestamp'] = pd.to_datetime(df['timestamp'])
			df['date'] = df['timestamp'].dt.date
			df['hour'] = df['timestamp'].dt.hour

			# Extract domain from URL
			df['domain'] = df['url'].apply(lambda x: urlparse(x).netloc if x else '')

			return df
		except Exception as e:
			print(f"Error getting enhanced scraping data: {e}")
			return pd.DataFrame()

	def create_quick_stats_summary(self) -> Dict[str, Any]:
		"""Create a quick statistics summary"""
		df = self.get_enhanced_scraping_data()
		if df.empty:
			return {}

		stats = {
			'total_extractions': len(df),
			'successful_extractions': df['success'].sum(),
			'success_rate': round(df['success'].mean() * 100, 1) if len(df) > 0 else 0,
			'total_results': df['result_count'].sum(),
			'avg_results_per_extraction': round(df['result_count'].mean(), 1) if len(df) > 0 else 0,
			'unique_domains': df['domain'].nunique(),
			'extraction_types': df['extraction_type'].unique().tolist(),
			'most_active_domain': df['domain'].value_counts().index[0] if not df['domain'].value_counts().empty else 'N/A',
			'most_used_extraction_type': df['extraction_type'].value_counts().index[0] if not df['extraction_type'].value_counts().empty else 'N/A'
		}

		return stats


class ReportGenerator:
	"""Generate comprehensive HTML reports with embedded visualizations"""

	def __init__(self, visualizer: DataVisualizer):
		self.visualizer = visualizer

	def generate_html_report(self) -> Optional[str]:
		"""Generate comprehensive HTML report"""
		df = self.visualizer.get_scraping_data()
		if df.empty:
			return None

		# Generate statistics
		stats = self._calculate_statistics(df)

		# Generate HTML content
		html_content = self._create_html_template(stats, df)

		# Save report
		report_path = os.path.join(self.visualizer.output_dir, "scraping_report.html")
		with open(report_path, 'w', encoding='utf-8') as f:
			f.write(html_content)

		return report_path

	def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
		"""Calculate summary statistics"""
		return {
			'total_extractions': len(df),
			'successful_extractions': df['success'].sum(),
			'success_rate': (df['success'].mean() * 100).round(1),
			'total_results': df['result_count'].sum(),
			'avg_results_per_extraction': df['result_count'].mean().round(1),
			'unique_domains': df['domain'].nunique(),
			'extraction_types': df['extraction_type'].unique().tolist(),
			'date_range': f"{df['date'].min()} to {df['date'].max()}",
			'top_domains': df['domain'].value_counts().head(5).to_dict(),
			'extraction_type_counts': df['extraction_type'].value_counts().to_dict()
		}

	def _create_html_template(self, stats: Dict[str, Any], df: pd.DataFrame) -> str:
		"""Create HTML report template"""
		return f"""
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Web Scraping Analytics Report</title>
	<style>
		body {{
			font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
			margin: 0;
			padding: 20px;
			background-color: #f5f5f5;
		}}
		.container {{
			max-width: 1200px;
			margin: 0 auto;
			background-color: white;
			padding: 30px;
			border-radius: 10px;
			box-shadow: 0 0 20px rgba(0,0,0,0.1);
		}}
		h1 {{
			color: #2c3e50;
			text-align: center;
			margin-bottom: 30px;
			border-bottom: 3px solid #3498db;
			padding-bottom: 10px;
		}}
		h2 {{
			color: #34495e;
			border-left: 4px solid #3498db;
			padding-left: 15px;
			margin-top: 30px;
		}}
		.stats-grid {{
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
			gap: 20px;
			margin: 20px 0;
		}}
		.stat-card {{
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
			color: white;
			padding: 20px;
			border-radius: 10px;
			text-align: center;
			box-shadow: 0 4px 15px rgba(0,0,0,0.1);
		}}
		.stat-number {{
			font-size: 2.5em;
			font-weight: bold;
			margin-bottom: 5px;
		}}
		.stat-label {{
			font-size: 0.9em;
			opacity: 0.9;
		}}
		table {{
			width: 100%;
			border-collapse: collapse;
			margin: 20px 0;
			box-shadow: 0 2px 15px rgba(0,0,0,0.1);
		}}
		th, td {{
			padding: 12px;
			text-align: left;
			border-bottom: 1px solid #ddd;
		}}
		th {{
			background-color: #3498db;
			color: white;
		}}
		tr:hover {{
			background-color: #f5f5f5;
		}}
		.success {{
			color: #27ae60;
			font-weight: bold;
		}}
		.failed {{
			color: #e74c3c;
			font-weight: bold;
		}}
		.chart-placeholder {{
			background-color: #ecf0f1;
			padding: 40px;
			text-align: center;
			border-radius: 10px;
			margin: 20px 0;
			border: 2px dashed #bdc3c7;
		}}
		.footer {{
			text-align: center;
			margin-top: 40px;
			padding-top: 20px;
			border-top: 1px solid #ecf0f1;
			color: #7f8c8d;
		}}
	</style>
</head>
<body>
	<div class="container">
		<h1>🕷️ Web Scraping Analytics Report</h1>
		<p style="text-align: center; color: #7f8c8d; font-size: 1.1em;">
			Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
		</p>

		<h2>📊 Summary Statistics</h2>
		<div class="stats-grid">
			<div class="stat-card">
				<div class="stat-number">{stats['total_extractions']:,}</div>
				<div class="stat-label">Total Extractions</div>
			</div>
			<div class="stat-card">
				<div class="stat-number">{stats['success_rate']}%</div>
				<div class="stat-label">Success Rate</div>
			</div>
			<div class="stat-card">
				<div class="stat-number">{stats['total_results']:,}</div>
				<div class="stat-label">Total Results</div>
			</div>
			<div class="stat-card">
				<div class="stat-number">{stats['unique_domains']}</div>
				<div class="stat-label">Unique Domains</div>
			</div>
		</div>

		<h2>🎯 Extraction Types</h2>
		<table>
			<thead>
				<tr>
					<th>Extraction Type</th>
					<th>Count</th>
					<th>Percentage</th>
				</tr>
			</thead>
			<tbody>
				{''.join([f"<tr><td>{type_name}</td><td>{count}</td><td>{(count/stats['total_extractions']*100):.1f}%</td></tr>"
						for type_name, count in stats['extraction_type_counts'].items()])}
			</tbody>
		</table>

		<h2>🌐 Top Domains</h2>
		<table>
			<thead>
				<tr>
					<th>Domain</th>
					<th>Extractions</th>
					<th>Percentage</th>
				</tr>
			</thead>
			<tbody>
				{''.join([f"<tr><td>{domain}</td><td>{count}</td><td>{(count/stats['total_extractions']*100):.1f}%</td></tr>"
						for domain, count in stats['top_domains'].items()])}
			</tbody>
		</table>

		<h2>📈 Recent Activity</h2>
		<table>
			<thead>
				<tr>
					<th>URL</th>
					<th>Type</th>
					<th>Results</th>
					<th>Status</th>
					<th>Date</th>
				</tr>
			</thead>
			<tbody>
				{''.join([f'''<tr>
					<td>{row['url'][:60] + '...' if len(row['url']) > 60 else row['url']}</td>
					<td>{row['extraction_type']}</td>
					<td>{row['result_count']}</td>
					<td class="{'success' if row['success'] else 'failed'}">
						{'✓ Success' if row['success'] else '✗ Failed'}
					</td>
					<td>{row['timestamp'].strftime('%Y-%m-%d %H:%M')}</td>
				</tr>''' for _, row in df.head(10).iterrows()])}
			</tbody>
		</table>

		<h2>📊 Data Visualizations</h2>
		<div class="chart-placeholder">
			<h3>📈 Interactive Charts Available</h3>
			<p>Run the visualization commands in the CLI to generate:</p>
			<ul style="text-align: left; display: inline-block;">
				<li>Interactive Dashboard (scraping_dashboard.html)</li>
				<li>Domain Analysis Chart (domain_analysis.html)</li>
				<li>Extraction Timeline (extraction_timeline.png)</li>
				<li>Data Volume Charts (data_volume_charts.png)</li>
				<li>Success Rate Analysis (success_rate_analysis.png)</li>
				<li>Activity Heatmap (activity_heatmap.png)</li>
			</ul>
		</div>

		<div class="footer">
			<p>Report generated by Web Scraper Analytics • Data range: {stats['date_range']}</p>
		</div>
	</div>
</body>
</html>
		"""
