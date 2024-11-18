from typing import Type, Dict
from abc import ABC, abstractmethod
from collections import Counter
# For image comparison
import requests
from PIL import Image
from io import BytesIO
from skimage.metrics import structural_similarity as ssim
import numpy as np


class AggregationStrategy(ABC):

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
        def _compare_images(url_1, url_2):
            print("Comparing images...")
            print("URL 1: ", url_1)
            print("URL 2: ", url_2)
            # Fetch images from URLs
            img_a = Image.open(requests.get(url_1, stream=True).raw)
            img_b = Image.open(requests.get(url_2, stream=True).raw)

            # Convert both images to RGB (to avoid issues with transparency or different formats)
            img_a = img_a.convert("RGB")
            img_b = img_b.convert("RGB")

            # Compare the sizes first (optional but faster)
            if img_a.size != img_b.size:
                return False  # Images have different sizes, so they're not the same

            # Compare pixel values
            return list(img_a.getdata()) == list(img_b.getdata())  # Compare pixel data directly


        def _compare(a, b):
            print("Comparing...")
            print("A: ", a)
            print("B: ", b)
            # a and b are strings
            if a == b:
                return True
            if isinstance(a, str) and isinstance(b, str):
                # Clean up the strings
                a = a.lower().strip().replace(" ", "")
                b = b.lower().strip().replace(" ", "")
                return a == b
            # a and b are image dictionaries
            if isinstance(a, dict) and isinstance(b, dict) and "url" in a and "url" in b:
                # Load the images from the URLs
                try:
                    return _compare_images(a["url"], b["url"])
                except:
                    return a == b
            return a == b
                
        def _remove_duplicates(candidates):
            result = []
            for val in candidates:
                appeared = False
                for res in result:
                    if _compare(val, res):
                        appeared = True
                        break
                if not appeared:
                    result.append(val)
            return result
        
        
        # Remove duplicates
        combined_history = []
        for hist in history:
            combined_history.extend(hist)
        return [_remove_duplicates(combined_history)]
        

    
class CombineValueStrategy(AggregationStrategy):
    def aggregate(self, candidates: list, history: list):
        """
        Combine all values from the candidates.
        """
        return ["".join(str(val) for val in candidates)]
    
class RemoveInvalidImageStrategy(AggregationStrategy):
    def aggregate(self, candidates: list, history: list):
        """
        Remove invalid images from the candidates.
        """
        def _is_valid_image(image):
            try:
                response = requests.get(image["url"])
                if response.status_code == 200:
                    return True
                return False
            except:
                return False
        
        result = []

        for arr in candidates:
            valid_images = [img for img in arr if _is_valid_image(img)]
            result.append(valid_images)

        return result
    
    
# Registry mapping strategy names to strategy classes
STRATEGY_REGISTRY: Dict[str, Type[AggregationStrategy]] = {
    "mode": ModeValueStrategy,
    "longest": LongestValueStrategy,
    "range": RangeValueStrategy,
    "concat": ConcatenateValueStrategy,
    "remove_duplicates": RemoveDuplicatesStrategy,
    "combine": CombineValueStrategy,
    "remove_invalid_image": RemoveInvalidImageStrategy
}



