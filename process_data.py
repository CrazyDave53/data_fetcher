import json
from typing import Dict, Any
from aggregating_strategy import AggregationStrategy, STRATEGY_REGISTRY

from typing import Dict, Any

class MappingProcessor:
    @staticmethod
    def apply_mapping(raw_data: Dict[str, Any], mapping: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a mapping to raw_data, transforming it to match the structure of the skeleton.
        """
        def get_nested_value(data, keys):
            """
            Extract a nested value from raw_data based on a dot-separated path.
            Handles lists of dictionaries.
            """
            if not keys:
                return None

            try:
                keys = keys.split('.')
                for key in keys:
                    if isinstance(data, list):
                        # Handle lists of dictionaries
                        data = [item.get(key) for item in data if isinstance(item, dict)]
                    elif isinstance(data, dict):
                        data = data.get(key, None)
                    else:
                        return None

                return data
            except Exception:
                return None

        def set_nested_value(output, keys, value):
            """
            Create a nested structure in `output` based on the dot-separated `keys` path.
            Handles lists of dictionaries.
            """
            keys = keys.split('.')
            for key in keys[:-1]:
                output = output.setdefault(key, {})
            output[keys[-1]] = value

        transformed_data = {}
        for skeleton_key, supplier_key in mapping.items():
            if isinstance(supplier_key, dict):
                # Recursively apply mapping for nested structures
                transformed_data[skeleton_key] = MappingProcessor.apply_mapping(raw_data, supplier_key)
            elif isinstance(supplier_key, str):
                # Handle standard mappings
                value = get_nested_value(raw_data, supplier_key)
                if value is not None:
                    set_nested_value(transformed_data, skeleton_key, value)
            elif isinstance(supplier_key, list) and all(isinstance(item, str) for item in supplier_key):
                # Handle mappings that result in lists (e.g., images with multiple paths)
                extracted_list = [
                    get_nested_value(raw_data, path)
                    for path in supplier_key
                ]
                extracted_list = [item for item in extracted_list if item is not None]
                set_nested_value(transformed_data, skeleton_key, extracted_list)

        return transformed_data




class SkeletonLoader:
    """ A utility class for loading and caching the skeleton """
    _skeleton = None  # Class-level cache for the skeleton
    _strategies = None  # Class-level cache for strategies

    @classmethod
    def load(cls, skeleton_path: str) -> Dict[str, Any]:
        """ Load the skeleton from a file """
        if cls._skeleton is None:
            with open(skeleton_path, 'r') as file:
                cls._skeleton = json.load(file)
        return cls._skeleton

    @classmethod
    def get_strategies(cls) -> Dict[str, Any]:
        """ Extract strategies recursively from the skeleton """
        if cls._skeleton is None:
            raise ValueError("Skeleton has not been loaded yet!")
        
        if cls._strategies is None:
            strategies = {}
            cls._traverse_and_collect(cls._skeleton, strategies, [])
            cls._strategies = strategies
        return cls._strategies

    @classmethod
    def _traverse_and_collect(cls, current: Any, strategies: Dict[str, list], path: list):
        if isinstance(current, dict):
            for key, value in current.items():
                if isinstance(value, list) and all(isinstance(item, str) for item in value):
                    # Handle the case where value is a list of strategies (strings)
                    field_path = ".".join(path + [key])
                    strategies[field_path] = [STRATEGY_REGISTRY[strategy]() for strategy in value]
                elif isinstance(value, dict):
                    # Recursively traverse nested dictionaries
                    cls._traverse_and_collect(value, strategies, path + [key])

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
