from fetcher import HotelDataFetcher
from hotel import HotelData
from process_data import SkeletonLoader, DataProcessor, MappingProcessor
import json
from typing import Dict, Any


class HotelManager:
    def __init__(self, config_path: str, skeleton_path: str):
        self.fetcher = HotelDataFetcher(config_path)
        self.hotels = {}  # Dictionary to store Hotel instances by their IDs
        self.skeleton = SkeletonLoader.load(skeleton_path)
        self.strategy = SkeletonLoader.get_strategies()

    def fetch_and_process(self):
        self.fetcher.load_fetchers()
        all_data = self.fetcher.fetch_all_data()

        for supplier_data in all_data:
            print("Type of supplier_data: ", type(supplier_data))
            supplier_name = supplier_data.get("supplier")
            mapping_path = f"mappings/{supplier_name}_mapping.json"

            with open(mapping_path, "r") as file:
                mapping = json.load(file)

            for raw_entry in supplier_data["hotels"]:
                transformed_data = MappingProcessor.apply_mapping(raw_entry, mapping)
                self._process_and_update_hotels(transformed_data)

    def _process_and_update_hotels(self, raw_data: Dict[str, Any]):
        hotel_id = raw_data.get("id")
        if not hotel_id:
            return  # Skip entries without an ID
        if hotel_id not in self.hotels:
            self.hotels[hotel_id] = HotelData(raw_data, self.skeleton, self.strategy)
        else:
            self.hotels[hotel_id]._update(raw_data)

# Test

hotel_manager = HotelManager("config.json", "skeleton.json")
hotel_manager.fetch_and_process()
#print all hotels
for hotel_id, hotel in hotel_manager.hotels.items():
    print(f"Hotel ID: {hotel_id}")
    print(hotel.data)
    # Save the processed data to a file
    with open(f"hotel_{hotel_id}.json", "w") as file:
        json.dump(hotel.data, file, indent=2)