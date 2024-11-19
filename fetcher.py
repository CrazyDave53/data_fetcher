import json
import requests  # Use requests to fetch data from URLs

# Simple Fetcher Class to handle individual suppliers
class SupplierFetcher:
    def __init__(self, supplier_url, supplier_name, supplier_mapping):
        self.supplier_url = supplier_url
        self.supplier_name = supplier_name
        self.supplier_mapping = supplier_mapping

    def fetch(self):
        # For now, assume the URL returns a JSON response
        try:
            response = requests.get(self.supplier_url)
            response.raise_for_status()  # Will raise an error for bad status codes
            return response.json()  # Return raw JSON data
        except requests.RequestException as e:
            return []  # Return an empty list in case of error

# HotelDataFetcher Class to manage fetching data
class HotelDataFetcher:
    def __init__(self, config_path):
        self.config_path = config_path
        self.fetchers = []

    def load_fetchers(self):
        # Load the configuration from the given path
        with open(self.config_path, 'r') as file:
            config = json.load(file)

        # Create fetchers for each supplier
        self.fetchers = [SupplierFetcher(supplier["url"], supplier["name"], supplier["mapping_file"]) for supplier in config["suppliers"]]

    def fetch_all_data(self):
        # Aggregate results from all suppliers
        all_data = []
        for fetcher in self.fetchers:
            data = fetcher.fetch()  # Fetch data from each supplier
            all_data.append({"supplier": fetcher.supplier_name, "hotels": data})
        return all_data