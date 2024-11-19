from fetcher import HotelDataFetcher
from hotel import HotelData
from process_data import SkeletonLoader, DataProcessor, MappingProcessor
import json
from typing import Dict, Any
import argparse
import sys


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

    def get_appropriate_hotels(self, hotel_ids, destination_ids):
        appropriate_hotels = []
        for hotel_id, hotel_data in self.hotels.items():
            if hotel_ids and hotel_id not in hotel_ids:
                continue
            if destination_ids and hotel_data.data.get("destination_id") not in destination_ids:
                continue
            appropriate_hotels.append(hotel_data.data)
        return appropriate_hotels
    
    def get_hotel_by_ids(self, hotel_ids):
        appropriate_hotels = []
        for hotel_id, hotel_data in self.hotels.items():
            if hotel_id in hotel_ids:
                appropriate_hotels.append(hotel_data.data)
        return appropriate_hotels
    
    def get_hotel_by_destination_ids(self, destination_ids):
        appropriate_hotels = []
        for hotel_id, hotel_data in self.hotels.items():
            if hotel_data.data.get("destination_id") in destination_ids:
                appropriate_hotels.append(hotel_data.data)
        return appropriate_hotels
    
    def get_all_hotels(self):
        return [hotel_data.data for hotel_data in self.hotels.values()]



def main():
    parser = argparse.ArgumentParser()
    
    num_args = len(sys.argv)

    hotel_ids = None
    destination_ids = None

    if num_args > 1:
        parser.add_argument("hotel_ids", type=str, help="Hotel IDs")
        parser.add_argument("destination_ids", type=str, help="Destination IDs")
        
        # Parse the arguments
        args = parser.parse_args()
    
        hotel_ids = args.hotel_ids
        destination_ids = args.destination_ids
    
    if hotel_ids == 'none':
        hotel_ids = None
    if destination_ids == 'none':
        destination_ids = None

    hotel_ids = hotel_ids.split(",") if hotel_ids else []
    destination_ids = destination_ids.split(",") if destination_ids else []
    destination_ids = [int(destination_id) for destination_id in destination_ids]

    manager = HotelManager("config.json", "skeleton.json")
    manager.fetch_and_process()
    appropriate_hotels = []
    if hotel_ids and destination_ids:
        appropriate_hotels = manager.get_appropriate_hotels(hotel_ids, destination_ids)
    elif hotel_ids:
        appropriate_hotels = manager.get_hotel_by_ids(hotel_ids)
    elif destination_ids:
        appropriate_hotels = manager.get_hotel_by_destination_ids(destination_ids)
    else:
        appropriate_hotels = manager.get_all_hotels()

    # Print the appropriate hotels json
    print(json.dumps(appropriate_hotels, indent=4))

if __name__ == "__main__":
    main()