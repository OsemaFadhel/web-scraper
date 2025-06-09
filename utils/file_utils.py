import json

def save_to_json(data, filename):
	try:
		with open(filename, 'w', encoding='utf-8') as f:
			json.dump(data, f, ensure_ascii=False, indent=4)
		print(f"Data saved to {filename}")
	except IOError as e:
		print(f"Error saving data to JSON: {e}")
