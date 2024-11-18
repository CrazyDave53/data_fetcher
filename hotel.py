import json
from typing import Dict, Any
from process_data import SkeletonLoader, DataProcessor
from aggregating_strategy import AggregationStrategy
from collections import defaultdict

class HotelData:
    def __init__(self, raw_data: Dict[str, Any], skeleton: Dict[str, Any], strategies: Dict[str, Any]):
        self.data = {}
        self.id = raw_data.get("id")
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
            """
            self.history[field_path].append(value)  # Track history
            strategies = self.strategies.get(field_path, [])
            candidates = self.history[field_path]
            for strategy in strategies:
                # Strategy aggregation logic goes here
                candidates = strategy.aggregate(candidates, self.history[field_path])
            return candidates[0] if candidates else None

        def traverse_and_update(current_raw, current_data, current_path):
            """
            Traverse raw data recursively and update fields in `self.data` as a nested structure.
            """
            if isinstance(current_raw, dict):
                for key, value in current_raw.items():
                    if isinstance(value, dict):
                        # Create or reuse nested structures
                        current_data[key] = current_data.get(key, {})
                        traverse_and_update(value, current_data[key], current_path + [key])
                    else:
                        # Apply strategies for this field
                        field_path = ".".join(current_path + [key])
                        current_data[key] = apply_strategies(field_path, value)
            else:
                # Base case for non-dict values
                field_path = ".".join(current_path)
                current_data[current_path[-1]] = apply_strategies(field_path, current_raw)

        traverse_and_update(raw_data, self.data, [])

