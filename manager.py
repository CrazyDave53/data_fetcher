from fetcher import HotelDataFetcher
from hotel import HotelData
from process_data import SkeletonLoader, DataProcessor

class HotelManager:
    def __init__(self, config_path: str, skeleton_path: str):
        """
        Initialize the HotelManager with configuration and skeleton paths.
        """
        self.fetcher = HotelDataFetcher(config_path)
        self.hotels = {}  # Dictionary to store Hotel instances by their IDs
        self.skeleton_path = skeleton_path  # Path to the skeleton JSON
    
    def fetch_and_process(self):
        """
        Fetch data from suppliers and process it.
        """
        self.fetcher.load_fetchers()  # Load supplier fetchers
        all_data = self.fetcher.fetch_all_data()  # Fetch data from all suppliers
        self._process_and_update_hotels(all_data)  # Process and update hotel data
    
    def _process_and_update_hotels(self, raw_data: list):
        """
        Process raw data and create or update Hotel instances.
        """
        for hotel_data in raw_data:
            hotel_id = hotel_data.get("id")
            if not hotel_id:
                print("Skipping entry without an ID")
                continue
            
            if hotel_id not in self.hotels:
                # Create a new Hotel instance if it doesn't exist
                self.hotels[hotel_id] = HotelData(hotel_data, self.skeleton_path)
            else:
                # Update the existing Hotel instance
                self.hotels[hotel_id]._aggregate(hotel_data)

    def get_hotel(self, hotel_id: str) -> HotelData:
        """
        Retrieve a Hotel instance by its ID.
        """
        return self.hotels.get(hotel_id)

    def get_all_hotels(self) -> list:
        """
        Retrieve all Hotel instances.
        """
        return list(self.hotels.values())