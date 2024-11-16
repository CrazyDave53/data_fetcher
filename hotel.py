import json
from typing import Dict, Any
from process_data import SkeletonLoader, DataProcessor

class HotelData:
    def __init__(self, raw_data: Dict[str, Any], skeleton_path: str):
        self.skeleton = SkeletonLoader.load(skeleton_path)  # Load skeleton (only once)
        if raw_data:
            self.data = self._update(raw_data)

    def _update(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Update the hotel data based on raw data and skeleton """
        self.data = DataProcessor.process(raw_data, self.skeleton)
        return DataProcessor.process(raw_data, self.skeleton)

    def get_name(self) -> str:
        return self.data.get("name", "")
    
    def get_id(self) -> str:
        return self.data.get("id", "")
    
    def get_destination_id(self) -> str:
        return self.data.get("destination_id", "")
    
    def _aggregate(self, raw_data: Dict[str, Any]):
        """ Aggregate additional data into the hotel """
        pass