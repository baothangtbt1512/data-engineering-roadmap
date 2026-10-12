import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Dict, Any, List
from src.config import logger, API_BASE_URL

class ApiExtractor:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = self._get_resilient_session()

    def _get_resilient_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,  # Đợi 1s -> 2s -> 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def fetch_data(self, endpoint: str, limit: int = 50) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}?limit={limit}"
        logger.info(f"Extracting data from endpoint: {url}")
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            records = data.get(endpoint, [])
            logger.info(f"Successfully fetched {len(records)} records from {endpoint}")
            return records
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            raise