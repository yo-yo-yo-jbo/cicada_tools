#!/usr/bin/env python3
import LiberPrimus

import sympy
import os

class CicadaException(Exception):
    pass

class Cicada(object):

    RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
    LATIN = [ 'F', 'V', 'TH', 'O', 'R', 'C', 'G', 'W', 'H', 'N', 'I', 'J', 'EO',
         'P', 'X', 'S', 'T', 'B', 'E', 'M', 'L', 'NG', 'OE', 'D', 'A', 'AE',
         'Y', 'IA', 'EA' ]
    PUNCT = { '.': '.\n', '-': ' ', '%': '\n\n', '/': '', '&' : '\n', '\n' : '' }

    @staticmethod
    def press_enter(clear=True):
        """
            Waits for user interaction.
        """

        # Get input
        print('\n\n')
        input('PRESS ENTER TO CONTINUE')
        if clear:
            os.system('clear')

    @staticmethod
    def heuristically_english(word):
        """
            Concludes whether the given word is heuristically English.
        """

        # We should see a vowel every 5 letters on average
        letters = [ i for i in word if i.isupper() ]
        if len(letters) == 0:
            return False
        vowels = len([ i for i in letters if i in 'AEIOUY' ])
        return vowels / len(letters) >= 0.2

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

    @staticmethod
    def totient(num):
        """
            Gets the totient of a number.
        """

        # Use sympy
        return sympy.totient(num)

    @staticmethod
    def runes_to_latin(runes, atbash=False, shifts=0, fib_substruction=False, totient_substruction=False, prime_substruction=False, interrupt_indexes=None):
        """
            Translates runes to latin.
        """

        # Iterate all runes
        s = ''
        curr_prime = 2
        text_index = -1
        rune_index = 0
        curr_fib_a = 1
        curr_fib_b = 1
        for rune in runes:

            # Find the index
            text_index += 1
            idx = Cicada.RUNES.find(rune)
            if idx >= 0:
    
                # Skip interrupts
                rune_index += 1
                if interrupt_indexes is not None and text_index in interrupt_indexes:
                    s += Cicada.LATIN[idx]
                    s += '[!]'
                    continue

                # Translate and optionally run atbash shifts and prime substructions
                if atbash:
                    idx = len(Cicada.RUNES) - idx - 1
                if prime_substruction:
                    idx = (len(Cicada.RUNES) + (idx - curr_prime + 1)) % len(Cicada.RUNES)
                    curr_prime = Cicada.find_next_prime(curr_prime)
                if totient_substruction:
                    idx = (len(Cicada.RUNES) + (idx - Cicada.totient(text_index))) % len(Cicada.RUNES)
                if fib_substruction:
                    idx = (len(Cicada.RUNES) + (idx - curr_fib_a)) % len(Cicada.RUNES)
                    curr_fib_a, curr_fib_b = curr_fib_b, curr_fib_a + curr_fib_b
                idx = (idx + shifts) % len(Cicada.RUNES)
                s += Cicada.LATIN[idx]
                continue

            # Add non-runes
            s += Cicada.PUNCT[rune] if rune in Cicada.PUNCT else rune

        # Return result
        return s

    @staticmethod
    def hill_decrypt_to_runes(cipher, key, add_padding=False, encrypt=False):
        """
            Hill cipher decryption from runes to runes.
        """

        # Validate key is square
        key_len = len(key.row(0))
        if key_len * key_len != len(key):
            raise CicadaException('Key is not square')
        
        # Get just the runes from ther ciphertext
        runes = [ Cicada.RUNES.find(c) for c in cipher if c in Cicada.RUNES ]
        if len(runes) % key_len != 0:
            if add_padding:
                padding = (key_len - (len(runes) % key_len)) * Cicada.RUNES[0]
                cipher += padding
                runes += [ 0 ] * len(padding)
            else:
                raise CicadaException('Ciphertext does not divide by key')

        # Inverse key for decryption
        inv_key = key if encrypt else key.inv_mod(len(Cicada.RUNES))

        # Decrypt
        plaintext = []
        for idx in range(0, len(runes), key_len):
            chunk = inv_key * sympy.Matrix(runes[idx:idx+key_len])
            chunk = [ i % len(Cicada.RUNES) for i in chunk ]
            plaintext += chunk

        # Replace encrypted runes with plaintext
        plaintext_index = 0
        text = ''
        for c in cipher:
            if c not in Cicada.RUNES:
                text += c
            else:
                text += Cicada.RUNES[plaintext[plaintext_index]]
                plaintext_index += 1

        # Return the runes
        return text

    @staticmethod
    def autokey_decrypt_to_runes(cipher, key):
        """
            Autokey cipher decryption from runes to runes.
        """

        # Build passphrase and extract only runes
        runes = ''.join([ c for c in cipher if c in Cicada.RUNES ])
        passphrase = key[:]

        # Decrypt
        plain = ''
        for rune_index in range(len(runes)):
            plain += Cicada.RUNES[(len(Cicada.RUNES) + Cicada.RUNES.find(runes[rune_index]) - Cicada.RUNES.find(passphrase[rune_index])) % len(Cicada.RUNES)]
            passphrase += plain[-1]

        # Replace encrypted runes with plaintext
        plaintext_index = 0
        text = ''
        for c in cipher:
            if c not in Cicada.RUNES:
                text += c
            else:
                text += plain[plaintext_index]
                plaintext_index += 1

        # Return the runes
        return text

    @staticmethod
    def vigenere_decrypt(cipher, key, interrupt_indexes=None):
        """
            Vigenere cipher decryption.
        """

        # Calculate key indexes
        mapping = Cicada.LATIN if key[0] in Cicada.LATIN else [ rune for rune in Cicada.RUNES ]
        key_indexes = [ mapping.index(letter) for letter in key ]
        if any([ True for index in key_indexes if index < 0 ]):
            raise CicadaException(f'Invalid key {key}')

        # Iterate all letters
        s = ''
        key_idx = 0
        for idx in range(len(cipher)):
           
            # Skip non-runes 
            if not cipher[idx] in Cicada.RUNES:
                s += Cicada.PUNCT[cipher[idx]] if cipher[idx] in Cicada.PUNCT else cipher[idx]
                continue

            # Skip interrupts
            if interrupt_indexes is not None and idx in interrupt_indexes:
                s += Cicada.runes_to_latin(cipher[idx])
                s += '[!]'
                continue

            # Decrypt rune
            new_idx = (len(Cicada.RUNES) + Cicada.RUNES.find(cipher[idx]) - key_indexes[key_idx]) % len(Cicada.RUNES)
            s += Cicada.LATIN[new_idx]
            key_idx = (key_idx + 1) % len(key)

        # Return result
        return s

    @staticmethod
    def ioc(runes):
        """
            Calculates the IoC.
        """

        # Just take runes
        rune_text = ''.join([ rune for rune in runes if rune in Cicada.RUNES ])
        if len(rune_text) == 0:
            return 0.0

        # Calculate the IoC
        s = sum([ rune_text.count(rune) * (rune_text.count(rune) - 1) for rune in Cicada.RUNES ])
        d = len(rune_text) * (len(rune_text) - 1) / len(Cicada.RUNES)
        return s/d

def tests():
    """
        Translate well-known pages.
    """

    # Iterate Liber Primus pages
    page_index = 0
    for page in LiberPrimus.LiberPrimusPages.PAGES:
        page_index += 1
        plain = page[1].decrypt(page[0])
        if not Cicada.heuristically_english(plain):
            raise CicadaException('Plaintext does not seem to be English')
        print(f'PAGE {page_index} (ioc={Cicada.ioc(page[0])}):\n\n{plain}')
        Cicada.press_enter()

def solve():
    """
        Wishful thinking.
    """

    # Get all unsolved pages
    pages = LiberPrimus.LiberPrimusPages.get_unsolved_pages()

    # Try to solve each page
    idx = 0
    for page in pages:
        idx += 1
        
        # Iterate all key options
        for key in LiberPrimus.PotentialSecrets.MAGIC_SQUARES:
            decrypted = Cicada.hill_decrypt_to_runes(page, key, add_padding=True)
            decrypted = Cicada.runes_to_latin(decrypted)
            print(f'PAGE {idx}\n\n')
            print(decrypted)
            Cicada.press_enter()

if __name__ == '__main__':
    solve()
