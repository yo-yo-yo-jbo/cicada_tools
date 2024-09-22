from core import RUNES
from abc import ABC
from abc import abstractmethod
import sympy
from enum import Enum
from core import ProcessedText

# Autokey modes
AutokeyMode = Enum('AutokeyMode', [ 'PLAINTEXT', 'CIPHERTEXT', 'ALT_START_PLAINTEXT', 'ALT_START_CIPHERTEXT', 'ALT_MOBIUS_START_PLAINTEXT', 'ALT_MOBIUS_START_CIPHERTEXT' ])

class MathUtils(object):
    """
        Math utilities.
    """

    @staticmethod
    def find_next_prime(prev_prime):
        """
            Finds the next prime number.
        """

        # Return the next prime
        return sympy.nextprime(prev_prime)

    @staticmethod
    def mobius(n):
        """
            Defines Mobius function.
        """

        # Use sympy
        return sympy.mobius(n)

    @staticmethod
    def totient(n):
        """
            Defines the Totient function.
        """

        # Use sympy
        return sympy.totient(n)

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

class AutokeyTransformer(TransformerBase):
    """
        Autokey cipher decryption.
    """

    def __init__(self, key, mode, use_gp=False, interrupt_indices=set()):
        """
            Creates an instance.
            The key should be in runes.
            The mode is one of the aforementioned AutokeyMode values.
            The GP boolean indicates whether to use primes on the index as an intermediate step in keystream extension.
        """

        # Save the key indices
        assert len(key) > 0, Exception('Empty key')
        self._key_indices = [ RUNES.index(rune) for rune in key ]

        # Save the interrupters
        self._interrupt_indices = interrupt_indices

        # Save the mode
        self._mode = mode
        self._use_gp = False

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Save state based on mode
        extend_to_plaintext = self._mode in (AutokeyMode.PLAINTEXT, AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_MOBIUS_START_PLAINTEXT)

        # Performs an autokey decryption
        result = []
        key_index = 0
        rune_index = -1
        ciphertext_extension_index = 0
        mob_value = None
        running_key_indices = self._key_indices[:]
        ciphertext = processed_text.get_runes()
        for rune in ciphertext:
            rune_index += 1

            # Handle Mobius function and change state accrdingly
            if self._mode in (AutokeyMode.ALT_MOBIUS_START_PLAINTEXT, AutokeyMode.ALT_MOBIUS_START_CIPHERTEXT):
                mob_value = MathUtils.mobius(rune_index + 1)
                extend_to_plaintext = (AutokeyMode.ALT_MOBIUS_START_PLAINTEXT and mob_value == 1) or (AutokeyMode.ALT_MOBIUS_START_CIPHERTEXT and mob_value == 0)

            # Treat mobius value of 0 just like an interrupt index
            if rune_index in self._interrupt_indices or mob_value == 0:
                new_index = RUNES.index(rune)
            else:
                new_index = (RUNES.index(rune) - running_key_indices[key_index]) % len(RUNES)
                key_index += 1

                # Extend the keystream from either plaintext or ciphertext
                if extend_to_plaintext:
                    running_key_indices.append(new_index)
                else:
                    running_key_indices.append(RUNES.index(ciphertext[ciphertext_extension_index]))
                    ciphertext_extension_index += 1

                # Using GP mode we extend the running keystream with the GP value of the lastly added value
                if self._use_gp:
                    running_key_indices[-1] = GP_PRIMES[running_key_indices[-1]] % len(RUNES)

                # Update whether to extend the keystream to plaintext if needed
                if self._mode in (AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT):
                    extend_to_plaintext = not extend_to_plaintext

            # Add the new rune
            result.append(RUNES[new_index])

        # Set the result
        processed_text.set_runes(result)

class AutokeyMobiusTransformer(TransformerBase):

    def __init__(self, keys, mode, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Save the keys
        assert len(keys) == 3, Exception('Expecting three keys')
        self._keys = keys[:]

        # Save the interrupters and the mode
        self._interrupt_indices = interrupt_indices
        self._mode = mode

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Split by runes
        rune_chunks = [ '' ] * 3
        interrupt_indices = [ set() ] * 3
        rune_index = 0
        for rune in processed_text.get_runes():
            
            # Use 1-based indexing
            rune_index += 1

            # Append to the right ciphertext chunk and map Mobius function from { -1, 0, 1 } to { 0, 1, 2 }
            fixed_index = MathUtils.mobius(rune_index) + 1
            rune_chunks[fixed_index] += rune

            # Save interrupt indices
            if rune_index - 1 in self._interrupt_indices:
                interrupt_indices[fixed_index].add(len(rune_chunks[fixed_index]) - 1)

        # Run each transformer seperately
        pt_chunks = [ None ] * 3
        for i in range(3):
            transformer = AutokeyTransformer(self._keys[i], self._mode, interrupt_indices[i])
            pt_chunks[i] = ProcessedText(rune_chunks[i])
            transformer.transform(pt_chunks[i])

        # Merge results
        results = []
        pt_runes = [ pt.get_runes() for pt in pt_chunks ]
        rune_index = 0
        for rune in processed_text.get_runes():
            rune_index += 1
            fixed_index = MathUtils.mobius(rune_index) + 1
            results.append(pt_runes[fixed_index].pop(0)) 
        processed_text.set_runes(results)

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
            transforms runes.
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
        You can also call the totient function recusrively, if needed, or not call it at all.
    """

    def __init__(self, add=True, interrupt_indices=set(), tot_calls=1):
        """
            Creates an instance.
        """

        # Save the action and the number of totient calls
        self._add = add
        self._tot_calls = tot_calls

        # Save the interrupters
        self._interrupt_indices = interrupt_indices

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Substract or adds the totient of each prime
        result = []
        curr_prime = 2
        rune_index = -1
        for rune in processed_text.get_runes():
            rune_index += 1
            if rune_index in self._interrupt_indices:
                new_index = RUNES.index(rune)
            else:
                val = curr_prime
                for i in range(self._tot_calls):
                    val = MathUtils.totient(val)
                if not self._add:
                    val *= -1
                new_index = (RUNES.index(rune) + val) % len(RUNES)
                curr_prime = MathUtils.find_next_prime(curr_prime)
            result.append(RUNES[new_index])

        # Set the result
        processed_text.set_runes(result)

class TotientFibTransformer(TransformerBase):
    """
        Substructs or adds the totient of the Fibonacci sequence from each index.
        You can also call the totient function recusrively, if needed, or not call it at all.
    """

    def __init__(self, add=True, interrupt_indices=set(), tot_calls=1):
        """
            Creates an instance.
        """

        # Save the action and the number of totient calls
        self._add = add
        self._tot_calls = tot_calls

        # Save the interrupters
        self._interrupt_indices = interrupt_indices

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Substract or adds the totient of each element in the Fibonacci sequence 
        result = []
        fib_a, fib_b = 1, 1
        rune_index = -1
        for rune in processed_text.get_runes():
            rune_index += 1
            if rune_index in self._interrupt_indices:
                new_index = RUNES.index(rune)
            else:
                val = fib_a
                for i in range(self._tot_calls):
                    val = MathUtils.totient(val)
                if not self._add:
                    val *= -1
                new_index = (RUNES.index(rune) + val) % len(RUNES)
                fib_a, fib_b = fib_b, fib_a + fib_b
                print(f'! {fib_a} !')
            result.append(RUNES[new_index])

        # Set the result
        processed_text.set_runes(result)

class MobiusTotientPrimeTransformer(TransformerBase):
    """
        Substructs or adds to Mobius function of the totient of primes (i.e. p-1), times a either the totient or the prime, from each index.
    """

    def __init__(self, add=True, use_prime_as_base=False, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Save the action
        self._add = add
        self._use_prime_as_base = use_prime_as_base

        # Save the interrupters
        self._interrupt_indices = interrupt_indices

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Substract or adds the value of each prime
        result = []
        curr_prime = 2
        rune_index = -1
        for rune in processed_text.get_runes():
            rune_index += 1
            if rune_index in self._interrupt_indices:
                new_index = RUNES.index(rune)
            else:
                tot = MathUtils.totient(curr_prime)
                if self._use_prime_as_base:
                    val = (MathUtils.mobius(tot) * curr_prime) % len(RUNES)
                else:
                    val = (MathUtils.mobius(tot) * tot) % len(RUNES)
                if not self._add:
                    val *= -1
                new_index = (RUNES.index(rune) + val) % len(RUNES)
                curr_prime = MathUtils.find_next_prime(curr_prime)
            result.append(RUNES[new_index])

        # Set the result
        processed_text.set_runes(result)

class ReverseTransformer(TransformerBase):
    """
        Reverses the processed text.
    """

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Reverses runes
        processed_text.set_runes(processed_text.get_runes()[::-1])

class KeystreamTransformer(TransformerBase):
    """
        Uses a keystream to either add or substruct from each rune value.
        Keystream is assumed to be infinite or sufficiently long.
    """

    def __init__(self, add=True, keystream=None, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Save the keystream and the action
        self._keystream = keystream
        self._add = add

        # Save the interrupters
        self._interrupt_indices = interrupt_indices

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Runs the keystream
        result = []
        rune_index = -1
        try:
            for rune in processed_text.get_runes():
                rune_index += 1
                if rune_index in self._interrupt_indices:
                    result.append(rune)
                else:
                    val = next(self._keystream)
                    if not self._add:
                        val *= -1
                    result.append(RUNES[val % len(RUNES)])

            # Set the result
            processed_text.set_runes(result)
        except StopIteration:
            pass

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

class TransformerSequence(TransformerBase):
    """
        Builds a transformer sequence.
    """

    def __init__(self, *transformers):
        """
            Creates an instance.
        """

        # Save all transformers
        self._transformers = transformers

    def transform(self, processed_text):
        """
            transforms runes.
        """

        # Runs all transformers sequentially
        for transformer in self._transformers:
            transformer.transform(processed_text)

