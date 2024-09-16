from core import RUNES
from abc import ABC
from abc import abstractmethod
import sympy

class TransformerBase(ABC):
    """
        Base class for transformers.
    """

    @abstractmethod
    def transform(self, processed_text):
        """
            Transforms a processed text.
        """
        pass

class ShiftTransformer(TransformerBase):
    """
        Shift (Caesar) transformer.
    """

    def __init__(self, shift):
        """
            Creates an instance.
        """

        # Saves the shift value
        self._shift = shift % len(RUNES)

    def transform(self, processed_text):
        """
            Trandforms runes.
        """

        # Performs the shift transformation
        processed_text.set_runes([ RUNES[(RUNES.index(rune) + self._shift) % len(RUNES)] for rune in processed_text.get_runes() ])

class AtbashTransformer(TransformerBase):
    """
        Atbash transformer.
    """

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Performs Atbash transformation
        processed_text.set_runes([ RUNES[len(RUNES) - RUNES.index(rune) - 1] for rune in processed_text.get_runes() ])

class VigenereTransformer(TransformerBase):
    """
        Vigenere cipher decryption.
    """

    def __init__(self, key, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Save the key indices
        assert len(key) > 0, Exception('Empty key')
        self._key_indices = [ RUNES.index(rune) for rune in key ]
        assert len([ i for i in self._key_indices if i < 0 ]) == 0, Exception('Invalid key')

        # Save the interrupters
        self._interrupt_indices = interrupt_indices

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Performs Vigenere decryption
        result = []
        key_index = 0
        rune_index = -1
        for rune in processed_text.get_runes():
            rune_index += 1
            if rune_index in self._interrupt_indices:
                new_index = RUNES.index(rune)
            else:
                new_index = (RUNES.index(rune) - self._key_indices[key_index]) % len(RUNES)
                key_index = (key_index + 1) % len(self._key_indices)
            result.append(RUNES[new_index])

        # Set the result
        processed_text.set_runes(result)

class TotientPrimeTransformer(TransformerBase):
    """
        Substructs or adds the totient of primes (i.e. p-1) from each index.
    """

    def __init__(self, add=True, interrupt_indices=set()):
        """
            Creates an instance..
        """

        # Save the action
        self._add = add

        # Save the interrupters
        self._interrupt_indices = interrupt_indices

    @staticmethod
    def find_next_prime(prev_prime):
        """
            Finds the next prime number.
        """

        # Just iterate
        if prev_prime == 2:
            return 3
        candidate = prev_prime + 2
        while not sympy.isprime(candidate):
            candidate += 2
        return candidate

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Substract the totient of each prime
        result = []
        curr_prime = 2
        rune_index = -1
        for rune in processed_text.get_runes():
            rune_index += 1
            if rune_index in self._interrupt_indices:
                new_index = RUNES.index(rune)
            else:
                val = curr_prime - 1
                if not self._add:
                    val *= -1
                new_index = (RUNES.index(rune) + val) % len(RUNES)
                curr_prime = self.__class__.find_next_prime(curr_prime)
            result.append(RUNES[new_index])

        # Set the result
        processed_text.set_runes(result)

class UnsolvedTransformer(TransformerBase):
    """
        Marks the processed text as unsolved.
    """

    def transform(self, processed_text):
        """
            Sets the processed text as unsolved.
        """

        # Sets as unsolved
        processed_text.set_unsolved()

