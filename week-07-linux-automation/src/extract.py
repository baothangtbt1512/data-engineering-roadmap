import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "https://dummyjson.com")

def extract_products():
    url = f"{API_BASE_URL}/products?limit=100"
    print(f"[EXTRACT] Fetching data from: {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json().get("products", [])
        
        # Lưu vào tệp trung gian staging
        os.makedirs("data", exist_ok=True)
        with open("data/raw_extracted.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"[EXTRACT] Successfully extracted {len(data)} items to data/raw_extracted.json")
        sys.exit(0)
    except Exception as e:
        print(f"[EXTRACT ERROR] Failed extraction: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    extract_products()