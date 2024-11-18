from typing import Type, Dict
from abc import ABC, abstractmethod
from collections import Counter




class AggregationStrategy(ABC):

    def _string_compare(self, a, b):
        # Clean up the strings
        a = a.lower().strip().replace(" ", "")
        b = b.lower().strip().replace(" ", "")

        return a == b

    @abstractmethod
    def aggregate(self, candidates: list, history: list):
        """
        Aggregate a list of candidates using the strategy.
        :param candidates: The current list of candidates.
        :param history: The history of all values seen for this field.
        :return: A new list of candidates after applying the strategy.
        """
        pass

class ModeValueStrategy(AggregationStrategy):
    def aggregate(self, candidates: list, history: list):
        """
        Return the most common values from the history.
        """
        from collections import Counter
        counts = Counter(history)
        max_count = max(counts.values())
        # Only return values if it is in candidates
        return [val for val, count in counts.items() if count == max_count and val in candidates]

class LongestValueStrategy(AggregationStrategy):
    def aggregate(self, candidates: list, history: list):
        """
        Return the longest values from the candidates.
        """
        max_length = max(len(str(val)) for val in candidates)
        return [val for val in candidates if len(str(val)) == max_length]
    
class RangeValueStrategy(AggregationStrategy):
    def aggregate(self, candidates: list, history: list):
        """
        Return the range of values from the candidates.
        """
        return [str(min(candidates)) + " - " + str(max(candidates))]

class ConcatenateValueStrategy(AggregationStrategy):
    def aggregate(self, candidates: list, history: list):
        """
        Concatenate all values from the candidates.
        """
        # Remove duplicates
        candidates = list(set(candidates))
        return [", ".join(str(val) for val in candidates)]

class RemoveDuplicatesStrategy(AggregationStrategy):
    def aggregate(self, candidates: list, history: list):
        """
        Remove duplicates from the candidates.
        """
        def remove_duplicates(candidates):
            result = []
            for val in candidates:
                appeared = False
                for res in result:
                    if self._string_compare(val, res):
                        appeared = True
                        break
                if not appeared:
                    result.append(val)
            return result
        # Remove duplicates
        combined_history = []
        for hist in history:
            combined_history.extend(hist)
        return [remove_duplicates(combined_history)]
        

    
class CombineValueStrategy(AggregationStrategy):
    def aggregate(self, candidates: list, history: list):
        """
        Combine all values from the candidates.
        """
        return ["".join(str(val) for val in candidates)]
    
    
# Registry mapping strategy names to strategy classes
STRATEGY_REGISTRY: Dict[str, Type[AggregationStrategy]] = {
    "mode": ModeValueStrategy,
    "longest": LongestValueStrategy,
    "range": RangeValueStrategy,
    "concat": ConcatenateValueStrategy,
    "remove_duplicates": RemoveDuplicatesStrategy,
}



