import json
from typing import Dict, Any
from process_data import SkeletonLoader, DataProcessor
from aggregating_strategy import AggregationStrategy
from collections import defaultdict

class HotelData:
    def __init__(self, raw_data: Dict[str, Any], skeleton: Dict[str, Any], strategies: Dict[str, Any]):
        self.data = {}
        self.history = defaultdict(list)  # Track history for each field
        self.strategies = strategies  # Field-to-strategy mappings
        if raw_data:
            self._update(raw_data)

    def _update(self, raw_data: Dict[str, Any]):
        """
        Update the hotel data with new raw data.
        """
        def apply_strategies(field_path, value):
            """
            Apply strategies to a specific field and return the processed value.
            :param field_path: The dot-separated path to the field.
            :param value: The raw value for the field.
            """
            self.history[field_path].append(value)  # Track history
            strategies = self.strategies.get(field_path, [])
            candidates = self.history[field_path]
            for strategy in strategies:
                candidates = strategy.aggregate(candidates, self.history[field_path])
            return candidates[0] if candidates else None

        def traverse_and_update(current_raw, current_path):
            """
            Traverse raw data recursively and update fields using strategies.
            :param current_raw: The current part of the raw data.
            :param current_path: The current path in the raw data, represented as a list of keys.
            """
            if isinstance(current_raw, dict):
                result = {}
                for key, value in current_raw.items():
                    result[key] = traverse_and_update(value, current_path + [key])
                return result
            else:
                # Apply strategies for this field
                field_path = ".".join(current_path)
                return apply_strategies(field_path, current_raw)

        self.data = traverse_and_update(raw_data, [])
