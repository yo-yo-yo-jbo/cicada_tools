from research_utils import ResearchUtils

from abc import ABC
from abc import abstractmethod

def measurement(measurement_instance):
    """
        Acts as a decorator for measurements, although it doesn't act as a decorator per-se but more like a function attribute.
        The proper way is wrapping each attempt with a measurement decorator, e.g. @measurement(IocMeasurement(threshold=1.6))
    """

    def measurement_decorator(func):
        """
            The decorator for the measurement functionality.
        """

        # Add measurements to function
        if not hasattr(func, '_measurements'):
            func._measurements = []
        func._measurements.append(measurement_instance)
        return func

    # Act as a decorator
    return measurement_decorator

class MeasurementBase(ABC):
    """
        Base class for measurements.
    """

    @abstractmethod
    def measure(self, processed_text):
        """
            Measures a processed text.
        """
        pass

class IocMeasurement(MeasurementBase):
    """
        Measures monogram IoC.
    """

    def __init__(self, threshold):
        """
            Creates an instance.
        """

        # Saves the threshold
        self._threshold = threshold

    def measure(self, processed_text):
        """
            Measures a processed text.
        """

        # Measure
        return processed_text.get_rune_ioc() >= self._threshold

class PrefixWordsMeasurement(MeasurementBase):
    """
        Measures the number of prefix words that match a dictionary.
    """

    def __init__(self, threshold):
        """
            Creates an instance.
        """

        # Saves the threshold and a reference to the English dictionary
        self._threshold = threshold
        self._dictionary = ResearchUtils.get_rune_english_dictionary()

    def measure(self, processed_text):
        """
            Measures a processed text.
        """

        # Measure
        return processed_text.get_first_non_wordlist_word_index(self._dictionary) >= self._threshold 

