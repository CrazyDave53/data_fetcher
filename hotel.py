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
        for key, value in strategies.items():
            print(f"Field hotel: {key}, Strategies: {value}")
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
            strategies = self.strategies.get(field_path + '.strategy', [])
            candidates = self.history[field_path]
            print("Field Path: ", field_path)
            print("Candidates: ", candidates)
            print("History: ", self.history[field_path])
            print("Strategies: ", strategies)
            print("Value: ", value)

            # Apply each strategy in sequence
            for strategy in strategies:
                candidates = strategy.aggregate(candidates, self.history[field_path])

            print("Candidates after strategy: ", candidates)
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

            elif isinstance(current_raw, list):
                # Process lists directly (images, etc.)
                field_path = ".".join(current_path)
                if field_path in self.strategies:
                    # Apply strategies to each item in the list
                    updated_list = []
                    for item in current_raw:
                        updated_list.append(apply_strategies(field_path, item))
                    current_data[current_path[-1]] = updated_list
                else:
                    # No strategies, just copy the list over
                    current_data[current_path[-1]] = current_raw


            else:
                # Base case for non-dict values
                field_path = ".".join(current_path)
                current_data[current_path[-1]] = apply_strategies(field_path, current_raw)

        traverse_and_update(raw_data, self.data, [])
