from core import RuneUtils
from abc import ABC
from abc import abstractmethod
import sympy
from enum import Enum
from core import ProcessedText
import os

# Autokey modes
AutokeyMode = Enum('AutokeyMode', [ 'PLAINTEXT', 'CIPHERTEXT', 'ALT_START_PLAINTEXT', 'ALT_START_CIPHERTEXT', 'ALT_MOBIUS_START_PLAINTEXT', 'ALT_MOBIUS_START_CIPHERTEXT' ])

class MathUtils(object):
    """
        Math utilities.
    """

    # Fibonacci primes cache
    _FIBO_PRIMES_CACHE = None

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

    @staticmethod
    def sqrt(num):
        """
            Square root of the given number.
        """

        # Use sympy
        return sympy.sqrt(num)

    @staticmethod
    def is_square(num):
        """
            Indicates if the given number is a square.
        """

        # Rule out negatives
        if num < 0:
            return False

        # See if the square root is an integer
        return sympy.sqrt(num).is_Integer

    @staticmethod
    def gen_primes(first_value=2, indices_apart=1):
        """
            A generator for primes.
        """

        # Generate primes forever
        assert indices_apart > 0, Exception(f'Invalid argument for indices apart between primes: {indices_apart}')
        curr_prime = first_value
        while True:
            yield curr_prime
            for i in range(indices_apart):
                curr_prime = MathUtils.find_next_prime(curr_prime)

    @classmethod
    def get_fibo_primes(cls):
        """
            Gets primes indecex by the Fibonacci sequence.
            Since generating those is CPU-intenstive, it was pre-generated in a file "fibo_primes.txt".
        """

        # Get from cache
        if cls._FIBO_PRIMES_CACHE is None:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fibo_primes.txt')
            with open(path, 'r') as fp:
                cls._FIBO_PRIMES_CACHE = list(map(int, [ elem for elem in fp.read().split('\n') if len(elem) > 0 ]))

        # Create an iterator
        return iter(cls._FIBO_PRIMES_CACHE)

    @abstractmethod
    def matrix_to_spiral_stream(matrix, repeat=False):
        """
            Creates a repeating stream from a given square matrix.
            Can optionally repeat the pattern indefinitely.
        """

        # Define directions
        dirs = [ (1, 0), (0, 1), (-1, 0), (0, -1) ]
        size = matrix.rows

        # Optionally repeat forever
        while True:

            # Find the midpoint
            x, y = (size - 1) // 2, (size - 1) // 2

            # Start right
            count = 0
            dir_index = 0
            steps_left = 1
            visited = 0
            dir_changes_even = False
            curr_step_size = 1

            # Return entire matrix
            while visited < size * size:

                # Yield the current point
                yield matrix.row(y)[x]
                visited += 1

                # Change direction if we are out of steps
                if steps_left == 0:
                    dir_index = (dir_index + 1) % len(dirs)
                    if dir_changes_even:
                        curr_step_size += 1
                    steps_left = curr_step_size
                    dir_changes_even = not dir_changes_even

                # Walk direction
                x, y = (x + dirs[dir_index][0], y + dirs[dir_index][1])
                steps_left -= 1

            # Break out unless repeating
            if not repeat:
                break

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
        self._shift = shift % RuneUtils.size() 

    def transform(self, processed_text):
        """
            Trandforms runes.
        """

        # Performs the shift transformation
        processed_text.set_runes([ RuneUtils.rune_at(RuneUtils.get_rune_index(rune) + self._shift) for rune in processed_text.get_runes() ])

class AtbashTransformer(TransformerBase):
    """
        Atbash transformer.
    """

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Performs Atbash transformation
        processed_text.set_runes([ RuneUtils.rune_at(RuneUtils.size() - RuneUtils.get_rune_index(rune) - 1) for rune in processed_text.get_runes() ])

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
        self._key_indices = [ RuneUtils.get_rune_index(rune) for rune in key ]

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
                new_index = RuneUtils.get_rune_index(rune)
            else:
                new_index = (RuneUtils.get_rune_index(rune) - running_key_indices[key_index]) % RuneUtils.size()
                key_index += 1

                # Extend the keystream from either plaintext or ciphertext
                if extend_to_plaintext:
                    running_key_indices.append(new_index)
                else:
                    running_key_indices.append(RuneUtils.get_rune_index(ciphertext[ciphertext_extension_index]))
                    ciphertext_extension_index += 1

                # Using GP mode we extend the running keystream with the GP value of the lastly added value
                if self._use_gp:
                    running_key_indices[-1] = GP_PRIMES[running_key_indices[-1]] % RuneUtils.size()

                # Update whether to extend the keystream to plaintext if needed
                if self._mode in (AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT):
                    extend_to_plaintext = not extend_to_plaintext

            # Add the new rune
            result.append(RuneUtils.rune_at(new_index))

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
        self._key_indices = [ RuneUtils.get_rune_index(rune) for rune in key ]
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
                new_index = RuneUtils.get_rune_index(rune)
            else:
                new_index = (RuneUtils.get_rune_index(rune) - self._key_indices[key_index]) % RuneUtils.size()
                key_index = (key_index + 1) % len(self._key_indices)
            result.append(RuneUtils.rune_at(new_index))

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
                new_index = RuneUtils.get_rune_index(rune)
            else:
                val = curr_prime
                for i in range(self._tot_calls):
                    val = MathUtils.totient(val)
                if not self._add:
                    val *= -1
                new_index = (RuneUtils.get_rune_index(rune) + val) % RuneUtils.size()
                curr_prime = MathUtils.find_next_prime(curr_prime)
            result.append(RuneUtils.rune_at(new_index))

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
                new_index = RuneUtils.get_rune_index(rune)
            else:
                val = fib_a
                for i in range(self._tot_calls):
                    val = MathUtils.totient(val)
                if not self._add:
                    val *= -1
                new_index = (RuneUtils.get_rune_index(rune) + val) % RuneUtils.size()
                fib_a, fib_b = fib_b, fib_a + fib_b
            result.append(RuneUtils.rune_at(new_index))

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
                new_index = RuneUtils.get_rune_index(rune)
            else:
                tot = MathUtils.totient(curr_prime)
                if self._use_prime_as_base:
                    val = (MathUtils.mobius(tot) * curr_prime) % RuneUtils.size()
                else:
                    val = (MathUtils.mobius(tot) * tot) % RuneUtils.size()
                if not self._add:
                    val *= -1
                new_index = (RuneUtils.get_rune_index(rune) + val) % RuneUtils.size()
                curr_prime = MathUtils.find_next_prime(curr_prime)
            result.append(RuneUtils.rune_at(new_index))

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
        Keystream is assumed to be infinite or sufficiently long - but generally will give up and only transform the first N runes if finite.
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
        orig_runes = processed_text.get_runes()
        try:
            for rune in orig_runes:
                rune_index += 1
                if rune_index in self._interrupt_indices:
                    result.append(rune)
                else:
                    val = next(self._keystream)
                    if not self._add:
                        val *= -1
                    result.append(RuneUtils.rune_at((RuneUtils.get_rune_index(rune) + val) % RuneUtils.size()))

            # Set the result
            processed_text.set_runes(result)
        except StopIteration:

            # Extend results as much as possible
            result = (result + orig_runes)[:len(orig_runes)]
            processed_text.set_runes(result)

class Page15FuncPrimesTransformer(KeystreamTransformer):
    """
        Treats abs(3301 - p) for all primes p as a keystream transformer.
        That function was derived from Page 15's square matrix, which works on primes indexed by the Fibonacci sequence.
    """

    def __init__(self, add=True, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Call super
        super().__init__(add=add, keystream=map(lambda x:abs(3301-x), MathUtils.gen_primes()), interrupt_indices=interrupt_indices)

class FiboPrimesTransformer(KeystreamTransformer):
    """
        Uses the primes indexed by Fibonacci sequence (2, 3, 5, 17, 11, 17, 23) as a keystream.
        This information was derived from Page 15's square matrix, which works on primes indexed by the Fibonacci sequence.
    """

    def __init__(self, add=True, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Call super
        super().__init__(add=add, keystream=MathUtils.get_fibo_primes(), interrupt_indices=interrupt_indices)

class Page15FiboPrimesTransformer(KeystreamTransformer):
    """
        Treats abs(3301 - primes[fib[i]]) as a keystream.
        This information was derived from Page 15's square matrix, which works on primes indexed by the Fibonacci sequence.
    """

    def __init__(self, add=True, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Call super
        super().__init__(add=add, keystream=map(lambda x:abs(3301-x), MathUtils.get_fibo_primes()), interrupt_indices=interrupt_indices)

class SpiralSquareKeystreamTransformer(KeystreamTransformer):
    """
        Given a square matrix, uses its values as a keystream in a clockwise spiral shape from its center.
        This pattern was erived from Page 15's square matrix.
    """

    def __init__(self, matrix, add=True, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Call super
        super().__init__(add=add, keystream=MathUtils.matrix_to_spiral_stream(matrix, repeat=True), interrupt_indices=interrupt_indices)

class Primes11IndicesApartTransformer(KeystreamTransformer):
    """
        The first few pages of Liber Primus part 1 (solved pages) have page numbers that are 107, 167, 229.
        That corresponds to primes that are 11-indices apart, and can be turned into a keystream.
    """

    def __init__(self, start_value=107, add=True, interrupt_indices=set()):
        """
            Creates an instance.
        """

        # Call super
        super().__init__(add=add, keystream=MathUtils.gen_primes(first_value=start_value, indices_apart=11), interrupt_indices=interrupt_indices)

class HillCipherTransformer(TransformerBase):
    """
        Runs Hill Cipher on runes.
    """

    def __init__(self, matrix, padding='ᚠ', inverse=True):
        """
            Creates an instance.
        """

        # Saves the matrix and the padding
        self._matrix = matrix.inv_mod(RuneUtils.size()) if inverse else matrix
        assert len(padding) == 1, Exception('Invalid padding length')
        assert RuneUtils.is_rune(padding[0]), Exception(f'Padding must be a rune: {padding}')
        self._padding = padding[0]

    def transform(self, processed_text):
        """
            Transforms runes.
        """
        
        # Iterate runes in groups
        result = []
        runes = processed_text.get_runes()
        for i in range(0, len(runes), self._matrix.rows):

            # Get the chunk and optionally extend with padding
            chunk = (''.join(runes[i:i+self._matrix.rows]) + (self._padding * self._matrix.rows))[:self._matrix.rows]
            chunk = [ RuneUtils.get_rune_index(rune) for rune in chunk ]

            # Work on transposed matrix
            new_chunk = self._matrix * sympy.Matrix(chunk)
            new_chunk = [ RuneUtils.rune_at(num % RuneUtils.size()) for num in new_chunk ]
            result.extend(new_chunk)

        # Set the result
        processed_text.set_runes(result[:len(runes)])

class ModInvTransformer(TransformerBase):
    """
        Performs modular inverse of each rune.
    """

    def transform(self, processed_text):
        """
            Transforms runes.
        """

        # Iterate runes
        result = []
        for rune in processed_text.get_runes():
            
            # Performs modular inverse
            curr_index = RuneUtils.get_rune_index(rune)
            new_index = pow(curr_index, -1, RuneUtils.size()) if curr_index != 0 else 0
            result.append(RuneUtils.rune_at(new_index))

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

