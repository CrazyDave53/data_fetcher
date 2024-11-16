import json
from typing import Dict, Any

class SkeletonLoader:
    """ A utility class for loading and caching the skeleton """
    _skeleton = None  # Class-level cache for the skeleton

    @classmethod
    def load(cls, skeleton_path: str) -> Dict[str, Any]:
        """ Loads the skeleton from a file, cached for subsequent calls """
        if cls._skeleton is None:
            print("Loading skeleton from file...")
            with open(skeleton_path, 'r') as file:
                cls._skeleton = json.load(file)
        return cls._skeleton


class DataProcessor:
    """ A utility class for processing raw data against a skeleton """

    @staticmethod
    def process(raw_data: Dict[str, Any], skeleton: Dict[str, Any]) -> Dict[str, Any]:
        """ Process the raw data according to the skeleton """
        processed_data = {}
        
        for key, value in skeleton.items():
            if isinstance(value, dict):
                # Recursively process nested dictionaries
                processed_data[key] = DataProcessor.process(raw_data.get(key, {}), value)
            elif isinstance(value, list):
                # Handle lists
                processed_data[key] = raw_data.get(key, [])
            else:
                # Directly assign the value from raw data or None if missing
                processed_data[key] = raw_data.get(key, None)
        
        return processed_data
