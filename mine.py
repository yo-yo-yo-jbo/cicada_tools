#!/usr/bin/env python3
import sympy
import os

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
    def runes_to_latin(runes, atbash=False, shifts=0, totient_substruction = False, prime_substruction=False, interrupt_indexes=None):
        """
            Translates runes to latin.
        """

        # Iterate all runes
        s = ''
        curr_prime = 2
        text_index = -1
        rune_index = 0
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
                idx = (idx + shifts) % len(Cicada.RUNES)
                s += Cicada.LATIN[idx]
                continue

            # Add non-runes
            s += Cicada.PUNCT[rune] if rune in Cicada.PUNCT else rune

        # Return result
        return s

    @staticmethod
    def vigenere_decrypt(cipher, key, interrupt_indexes=None):
        """
            Vigenere cipher decryption.
        """

        # Calculate key indexes
        mapping = Cicada.LATIN if key[0] in Cicada.LATIN else [ rune for rune in Cicada.RUNES ]
        key_indexes = [ mapping.index(letter) for letter in key ]
        if any([ True for index in key_indexes if index < 0 ]):
            raise Exception(f'Invalid key {key}')

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

cipher = '''
ᛋᚻᛖᚩᚷᛗᛡᚠ-ᛋᚣᛖᛝᚳ.ᚦᛄᚷᚫ-ᚠᛄᛟ-/
ᚩᚾᚦ-ᚾᛖᚹᛒᚪᛋᛟᛇᛁᛝᚢ-ᚾᚫᚷᛁᚦ-ᚻᛒᚾᛡ-/
ᛈᛒᚾ-ᛇᛄᚦ-ᚪᛝᚣᛉ-ᛒᛞᛈ-ᛖᛡᚠᛉᚷᚠ-/
ᛋᛈᛏᚠᛈᚢᛝᚣᛝᛉᛡ-ᚣᚻ-ᛒᚢ-ᚷᚩᛈ-ᛝᚫᚦ-ᛁ/
ᚫᚻᛉᚦᛈᚷ-ᚣᚠᛝᚳᛄ-ᚦᚪᛗᛁᛝᛁᛡᚣ-ᚻᛇ-ᛏᚻᚫ/
ᛡ-ᛉᚣ-ᛖᚢᛝ-ᚳᚠᚾ-ᛇᚦᛄᛁᚦ-ᚦᛈ-ᚣᛝᛠ-ᚣᚾ/
ᛖᚣ-ᛞᛉᛝᚹ-ᛒᚳᛉᛞᛒᚠ-ᛗᛏᚾᛖ-ᛠᛄᚾᛚᚷ/
ᛒ-ᛉᚷᚦ.ᚣᛁᛞᚪ-ᛝᚷᛗᛄᚱᚩᛚᛇ-ᚣᛏᛈᛁᚦᛞᛄ-/
ᛟᚻᛚ-ᛠ-ᚠᛉᚫᛈᚷᛉ-ᚠᛚᚹᛇᛏᚫ-ᚠᚷᚾ-ᛗᛇᛚᚾ-/
ᛝᛗᚠᚱᛡ-ᚪᛋ-ᛠᛗᛝᛉᛉᛇᛞᛒ-ᛟᛞᛗᚩ-ᛠ/
ᛇᚻ-ᛞᛝᚷ-ᛟᛝᛚᚢᚱᚾᛏ-ᚫᛋᚣᚢᚻᚱᛏ-ᚻᚳ-ᛋᛟ/
ᛏᛟᛝᚢᚱ-ᛋ-ᚠᚩᛖᚹᛠᛟᛚᚠᚫ-ᛗᚱᛝ-ᛞᚪᛗᚱ-ᚹ/
%
ᚪᛁᛗᛋᚾ-ᛋᛟᚱᚢᚹᛋᛚᛡ.ᛟᚪᚫᛝᛋᛞᛈᛏ-ᚳᚱᚦ/
ᛡ-ᚱᛒᚩᛞᚦᚠ-ᚣᛉᛁᛏ.ᛟᛁ-ᚠᛚᚩ-ᚠᛠ-ᚱᚩᛟᛗᚻ/
ᛗᚷᛈᚻ-ᚫᚻᚾᚩᚻᚣ-ᛟᛋᛚ-ᚾᚷ-ᚫᚣ-ᛟᚳᛒᛚᛄ-ᛝ/
ᛚᛟ-ᚫᛄᛠᚹ-ᛠᚦᚩ-ᛒᛟᚣ-ᚳᚠᚳᛄ-ᛚᚫ.ᚾ-ᚦᛈ-/
ᚢᛉ-ᛟᛉᚷ-ᛈᚠᛋᛇᚫᛟ-ᛝᛈᛇᚩᛖᚪ-ᚷᚫᛡᛝᚦᚩ/
-ᛈᚪᛟᚦᚱᛝᚫ-ᚳᛋᛒᛇᚣᚻ-ᛏᛉᛖᛚᚱ.ᚷᚹᚣ-ᛄᚠ/
ᛁᚾᛡᚳᚣᛠᛁᛡ-ᚩᚦ-ᛖᚳᚫᚳᛉᛡᛠ-ᚩᛚᚳ-ᚠᚱ/
ᛞᛝᛖᚢ-ᛞᚳᛚᛠᛋᛉᚳᚷᛡ.ᚹᛋᚦ-ᚠᛞᛝ-ᛁᛡ/
ᛗᚪᚫᚷ-ᚹᛋ-ᚾᛞ-ᚳᛈᚦᛉᛈᛠᛠ-ᚹᚢ-ᛠᚹ-ᚠᚹ/
ᛄᚣ-ᛉᛞᚹᚳᚷᚳᛟ-ᛞᛉᛟ-ᚱᛡᚷ-ᚾᛈᚪᚣᛈ-ᚳ/
ᚣᚻ-ᚠᛖᛄᛠᚾ-ᛟᚫ-ᚢᚪ-ᚻᚱ-ᛖᛠᚦᚠᛄᚪ-ᛚᛉ/
ᛋᛏ-ᛗᚠᛚᚠᛏ-ᚷᛁᚦ-ᚢᛚᚷ-ᛉᛠᛏᛋᛚᛄᛈ-ᛚᛉᛁ/
%
ᛟᛗ-ᚢ.ᚻᛏ-ᛒᛇᛚᛞᚻᛒᛗ-ᛠᚱᛒ-ᚾᚻᛒᛖᚷᛇ-/
ᛞᛚᚹᛇᛡᛈᚩ-ᚻᛖᛠ-ᚹᛁᚱᛁᚻ-ᚢᚦᚻᚣ-ᚾᛉᛒᚷᛄ/
ᛈᚢ-ᛝᛠᚠᚾᛁᛖᛞᛡᛝᚱ-ᛞᛒᛄᛡᛟᛗᛁ-ᚠᛏ-ᛄ/
ᛞᛁᚦᚱᛚᛋ-ᛖᛇᚩᚷᛒᛏᛞ-ᚦᚪᚾᚳᚣ-ᛡᛋᚦᛞ-ᛝᚠᛚ/
ᛖᚷᚻᚳ-ᛖᚩᛁᛏᚾᛉ-ᛈᛏᚠᚻᚱᛞᛖᚠᛏ-ᚫᚹᚻ-ᛒ/
ᚳ-ᚠ-ᛈᚪᛚᚢᛠᚾᛚᛄ-ᛄᚳᛚᚹᛠᛞᚢᛞᛇ-ᛠᛉ/
ᛞᚹᚻᛠ-ᚦᛡᚫᚳᛚᛏᚹᛖᛁᚳ-ᛈᛟᛞᚳ-ᚾᚻᚪ-ᚱᛁᚷ/
ᚦᛠᛖᛏᚷ-ᚦᚻᚩᛡᚹᚫᛄᛖ-ᛝᛠᛞ-ᚩᚫ-ᚪᛚ-ᛒᛄ/
ᚳᚢᛉᛏᚪᛒᛄᛈ-ᚠᛠ-ᚻᛞᚾᛡᚢᛈᛋᚢᚹ./
&
$
%
ᛚᛄ-ᛇᚻᛝᚳᚦᛏᚫᛄᛏᛉᚻ-ᛏᚢᛟ.ᛋᛈᚱᚷ/
-ᚣᚾᚪᚷᛇᛝᚾ-ᚹᚠᚣᚾᛒᛠᛡ-ᛈᚾᚣᚪᛋᛗ/
ᛒ-ᛡᛠᛡᛁ-ᚩᛒᚱᚾᛚᛠ-ᚱᛚᛚᛖᛒᚹᚾᚻᛗᚠ/
ᛟᛒ-ᛝ-ᚱᚪᛡᚷᛟᛇᛏᛗᛉ-ᛞᛇ-ᛗᚣᚻᛠ-ᛁᛚᛋ-ᚾ/
ᚹᚳᚠᛈᛗᛈᛚ-ᛠᛋᚦᚠᛟᛡ-ᚦᛖᚣ-ᚳᛄᛚᚳᛡᛗ-/
ᛒᛞᚳᛇ-ᛄᛁᛏᛟ-ᛞᛠᛖᛡᚾᛏ./
&
ᛈᛞᚦ.ᛇᛞᛇ-ᚫᛚᚳ-ᛡᛇ-ᛠᚻ-ᚹᛗᚣᚦ/
ᚢ-ᚻᛏᚦᚱᚻᛝ-ᛚᛝᛋ-ᚾᚫᛠᚷᛋᛚ-ᛋᛉ/
ᚩᚻᚹᛞᛗᛖᛗᚪᚠ-ᚳᚣᚳᚫᚾ-ᛏᚦᚷ-ᛁᛄᛁ/
-ᚳᛞᛡᛉ-ᚻᚫᚫᛠᚷ-ᛠᛝ-ᚠᛏᚩᚱᛞᚳᛇ-ᚠᚢ/
ᛉᛠᛒᚩ-ᛉᛁᚣᚷᛋᛋᛒᛠ-ᚩᛁᛈ-ᛁᛄᛁᚩᛖ-ᚻᛠᚻ/
%
ᛚᛡ-ᚣᛈᛉᛁᚹᛗᚳᛁ-ᛚᚷᚠᚾᛡᚳᛉ-ᛈᚩᚱᛡ-ᚻ-ᛄ/
ᛗ-ᛟᛉᛝ-ᚢᛗᛇᛠᚷᛝ-ᛝᚹᚳ-ᛚᛝᚢ-ᛉᛄᚠᛟ/
ᚢ-ᚷᛠ-ᛗᛉ-ᚪᚹ-ᛚᚢᛉᚫ-ᛗᛞᛝᚻᚱᚣ-ᚻᚪ-ᚷᛁ/
ᚠᚷᚳ-ᚫᛝᛄᛇᛉᛡ-ᚾᚦᛒᚢᛄᚱ.ᚹ-ᚷᛚᛟᚷ-ᚦᛇᚠ-/
ᚦᛠᛁ-ᛋᚷ-ᚷᚣ-ᛠᛡᛈ-ᛡᚫᛚ.ᚦᛠᛉᚫ-ᛖᛗ/
ᛖᛏᛟᛏ-ᛠᚳᚠ-ᚳᛠᚷ-ᚦ-ᛈᛁᚳᚾ.ᛇᚣᛝᛄᛝ/
ᛗᚹᚳᚾ-ᛒᚣᛠ-ᚩᛟᚷᚱ-ᛗᚱᛗᛈᛡᚹ-ᚫᛟᚦᛟ-ᛈ/
ᛉᛄᛚ-ᚱᛚᚱᛒᚪᛈᛏᛉᛚᛏ-ᛗᛉᛁᚹ.ᛄᛋᛟᛗᚾᚱ/
ᛖᛒᛋ-ᚳᛏᛚᛟ-ᛋᛒᚠᛉᚦᚪᛠᚢ-ᛇᛉ-ᚱᚷᛏᛇᛠ/
ᛁᛄᛒᛟ-ᛉᚷᛄᛝ-ᛠᚦ-ᚱᛝᛒ-ᚾᚢᚪᛝᛒᛈᛋᛠ-ᛈ/
ᚹᚩᚻᛖ-ᚫᛇᚷᚾᚫᛋᛇ-ᚩᛈᛗ-ᛖᛉᛡᛒᚹ-ᚢᛖᛁᛞ-/
ᛈᚪᛇᚷᛋᚳᚷᛞᛈᚣ-ᛡᛚᚦᚱ-ᚳᚢᚠᛇᚦ-ᛉᛖᛚ-ᚢ/
%
ᚱᚫ-ᛉᚻᛄᚫᛗᛚᚠ-ᚳᛝᛞ-ᛁᛝᚩ-ᚳᛋᛟᛖᚣᛟᚻᚢ-/
ᚷᛞᚹᚪ-ᛖᛋᚷᛝᚠᛉ-ᛞᛉᛄ-ᛠᚻᛁ-ᚦᛈᛉᚣ-ᛡ-/
ᛇᛞᛇᛝᛇᛝ-ᛖᛠᛞᚱ-ᛚᛇᛏ-ᛉᛏᚣ-ᚱᛇ-ᛈᛝᛇ/
ᛈᚩᛁᛚᛖᚠ-ᛇᚫᚪ-ᚣᛝᚠᚣ-ᚠᛞᚾᛚ-ᛉᛏᚾᚫᛋ.ᛁᚩ/
ᚳᚢ-ᚣᛠᚾᛏᚷᚳᚪ-ᛉᛡᛇ-ᚦᛄᚣᛄᛚᛟᛖᛚ-ᚣ./
ᛈᛡ-ᛖᚹᛟ-ᛇᚾᚪ-ᚻᛞᛇᛋ-ᚦᚣᛇᚦᛄᚦᚱᚢ-ᚳᛠ/
ᚪ-ᚢᛄᛡᛈ-ᚣᚫᛇᛋ-ᚻᛠᛏᚣᛞᚣᚫᚠᚻᚩ-ᛟᛗ/
ᛉᛟᛄᚷ-ᚢᛡᚱᛡᚳ-ᛁᚠᛟ-ᛁᛄᛈᛒ-ᛖᛝᚣᚦᚩᚫᚣ-/
ᛠᛉᛡᛖᛚ-ᛁᚱᚣᛞᛠᛄ-ᚫᚳ-ᛗᚷᛁᚫᚢᚪᚫ-ᛄᚪ/
ᚻᛈ-ᚠᛞᛚᛁᛠᛈᛟᚣᚩ-ᚢᛒᚷᛝᛟᚢᛝᛋᚢᚳ-ᛏ/
ᛞ.ᚫᛈᚩᛄ-ᛒᚻᚱᛁᚷᚻᛄ-ᚣᚹᛗᛇᚾᚫ-ᛞᛝᛇ-ᛟᛄ/
ᛝᚳᛖᛠ-ᛉᚪᚱᚣ-ᚪᚢᛏ-ᚳᛈᚳ-ᚩᛇᛟ-ᚫᛈ-ᛏ/
%
ᛉᚳᛏᚻᛞᛇ-ᛉᛒᛠ-ᚫᚾᛄ-ᛠᚪᛒ-ᛖᛠᚹ-ᛡᛚ-/
ᚹᛁᛡᛋᛈᛚᚦᚪᛋᛄ-ᛡᛞᚣᚱᛞᛟ-ᚦᚱᛉᛟᚹ-ᚣᛞᛏ-/
ᚷᛚᛡᚻᚹᛗᚱ-ᛝᚠᚳ-ᚱᚫᛁᛒᚷᛈᚣ-ᛞᚪᚱᚪᛉᛟ-ᚢ/
ᚩᛁᛠ./
&
ᚪᛏᛉᛒ-ᛗ-ᚷᛡᛋᛒ-ᛉᛇ.ᚷᚾᛠᚫᚷᛝᛞ-/
ᛉᛖᛏᚩᚷᛡ-ᛝᚻᛏ-ᚳᛁᚣ-ᛄᛏ-ᛟᚩᚻᚱᛄ-/
ᚳᛖᛡᚩ-ᛞᚪᛏᚣᚢᚾᚱᛇ-ᚫᚫᛁᛖᚠᛝᚦᚻ-/
ᛉᛁᛟᛋᛁ-ᛗᚪ-ᚢᛄᚳᛋᚹᚾᚣ-ᚩᛈᛉᚱ-ᛚᚫᛟᛏᛡ-ᛄ/
ᛈᛗ-ᛞᛋᚠᛗ-ᛟᚹ-ᛞᛚᛏ-ᚷᚱ-ᚩᚢᛋᚻᚪ-ᚣᛇᛡᛚ/
ᚢᚻ-ᛈᚹᛄᛚᚷᛒ-ᛗᚢᛄᛗ-ᛇᚾᛇ.ᚫᛚᚪᛚᚷᚪ-ᛋ/
%
ᚻᛝ-ᛚᚦᛒ-ᛋᚳᚢᚳᚩᛡ-ᛚᚳᛄ-ᛉᚪᚾᛇᛉ.ᛠ/
ᛗᛈᚢ-ᛗᚠᛚᛠᛝ-ᛒᛉᛁ-ᛚᚦᚱ-ᛠᛡᛁᚳ-ᚩᛉᛖ/
ᛞᛡ-ᛏᛋᛗᛠᛄᛈ-ᛠᛟ-ᛡᚫᚦᚹᚻᛈᛇᚪᚷᛈᚻ/
ᛠ-ᚳᛚᛠᛈ-ᛡᚣᚾᛁ-ᛚᛡᛁᚳ-ᚫᛇᚾ-ᚫᚳᛡᚱᛡᛚ/
ᛞ-ᛒᛟᛝᛡ-ᛉᛗᛝ-ᚳᚻᛟᛠᚾᛈᚳᚦ-ᛁᛇᚦ-ᛇᚢᚩ/
-ᚦᛈᚪ-ᛡᛚᛟᚹᛡᛈ-ᛄᛗ-ᚷᛒᛈᛋᚾᛇ-ᛏᚩᚷᚢᚾᚫ/
ᛖ-ᚾᚣᛁᛖ-ᛞᛝ-ᛞᛝ-ᛚᚢᛚᛉ-ᚪᚾᛝ-ᛇᚪᛄ-ᚻ-ᛞ/
ᚹᛈᚫᚹᚫ-ᛇᛁᛚᛝ-ᚦᚾᚳ.ᛒᛁᛏ-ᛠᚳᚩᛇᛖᛝ-ᚳᚻ/
ᛟᚻᚫᛄ-ᛟᛉ-ᛁᚳᛖᛏᛋᚹᛖᚾᛡᚣᛄᛗ-ᛖᚳᚪ./
&
ᛞᚩ-ᛟᛏᚦᚫ.ᚳᚹᛄ-ᛉᛠ-ᚷᛠᛗ./
&
$
%
ᛉᛁᛉᛗ-ᚢᛉᛗᚳᚦᛈᚩᛒ.ᛡᚾᛏ-ᛠᛉ/
-ᛈᚱᚣ-ᚩᚳᛠᛗᛝᚷᛉᛚᚢ-ᛝᛁᛏᚩ-/
ᛄᚠᛝ-ᛋᛚᚾᛞ.ᚩᛗ-ᛇᚫ-ᚱᛞᚹᛏᛄᚦ-/
ᚣᚦᛋ-ᚫᚣᛖᛋᛉᛟᛒ-ᛠᚱᛇ-ᛈᛝᚢᛈ-ᚩᚦᛉ-ᚪᚻ/
ᛟᚱᛝᚢᛖᚱ-ᚣᛚᛉᛚ-ᛡᛚᚱ-ᛈᚹᛇᚾ-ᛠᚪᚱᛉᛝ-/
ᚣᛋᚻᚢᛚ-ᛋᚣ-ᚷᚾᚢ-ᛇᚫᚾᚾ-ᚩᚫᛖᛞ-ᚪᚩᛄᛡᚢ/
ᚪᛉ-ᚱᛉᛡᛟᛄ-ᛗᛁᛇᛚᛠᚻᚦᛗᛠᚣ.ᚷᛒᚳᛈ/
ᛉᚳ-ᚾᛟᛟᛋᚷᛗᛈᛖᛏᛚᚾᛄ-ᛄᚳᛝᚩ-ᛁᚹᛚᛠᛒ-/
ᚠᚪᛖ-ᛏᛝ-ᚾᛈᛠᚩᛏᚦ-ᚻᛝᛉᛈᚻᛈᚳᛈᚱᚢ-ᛚ/
ᚠᛖᛟ-ᚷᚪᛒᚠᛁᚫᚠᚢᛟ-ᛗᚠᚣᛝᛄᚳ-ᚻᛏᚠᛚᚫ-ᛖ/
ᚦᛋᛚᚩᚢ-ᚫᚩᚪᛗᛟᚢᚹᛇ.ᛒᚾᛋᛚᛝᛄᛟᚾ-ᛗᛚᛒ-/
ᛟᛏ-ᚾᛞᛒᚩᚾᚦᛡᚻᛟ-ᚱᛈᚾᚠᛈᛞ-ᛋᚩᛁᛠᚣᚾ-ᛇ/
%
ᚣᚹᚫᚷᛄ-ᛝᛗᚪᚹᛈ-ᚪᚢᚾ-ᛈᛡᛗᛖᛞᛟ.ᛁ-ᛉ/
ᛡᛗ-ᚠᛈᚩ-ᚦᛉᛞ-ᚩᛞ-ᛋᛈᛉᛡᚷ-ᛟᚻᚠᚦᛉᛄ/
ᛟᛋᚦᚣᚦ-ᛏᚻᛋᚣ-ᚻᛠᚷᛚᚫᚱᛏ-ᚢᛋᛟ-ᚦᚠᚠᚣ/
ᛟᛡ-ᛇᚳᚣᛒᛚᛝ-ᛠᚱᚻᛞ-ᛄᚣᛏᚫ-ᚻᛞᚳᛋ-ᛉ/
ᚠᛞ-ᚦᛗ-ᚳᛇᛝ-ᚫᚾᛡᛠᚹᛁᛡ-ᛒᛗᛝ-ᚷᛈᛁᚳ-ᛠ/
ᛚᚷᛉᚣᚣᚱᛄ-ᛉᛁᛄᚢ-ᛖᚣ-ᚪᛝᛈ-ᛡᚫᚳ-ᛖᛠ/
ᚹᛒᚦᛟᚠᛗ-ᚫᚱᚠᚩᛏ-ᛝᛉᛞ-ᛗᛖᛡ-ᚩᛈᛋ-ᛇᛞ-/
ᛇᛟᚫᚾ-ᚷᛗᚣᛁᚫᛁᛄ-ᛈᛄᚩᛡᚷ-ᛈᚳᛄ-ᛚᛖᛡᚻᛚ/
ᚷᚱᛇ-ᛟᚣ-ᛠᚣᛗᚹᚾᚹ-ᚠᛁᛄᚢᛗᚫᚾᚳᛗᛠᛁ./
ᚩᛇ-ᛒᛚᛞ-ᚾᚹᚠᚾᛒᚱ-ᛋᛟᚦᛡ-ᚪᛡᛏᚷᚷᚹ-ᚪᛋᛡᚦ/
ᛋᚦᛋᚠᛗᚷᛞᛠ-ᛝᛈᚩᚪᚣᛝᛈᛋ-ᛟᚾᛇᚪᛖ-ᚻᚢ/
ᚷ-ᚩ-ᚢᚦᛏ-ᛒᚷᚣᛝᚠᚣᛁᚻ-ᚹᛡᛠᚱᚫᚹᛡᛞᚪᚦ/
%
ᚳ-ᛉᚢ-ᛈᛏᛋᚢᛖ-ᚷᚦᛡᛚ-ᛖᛋᛠᛝᛉᛈᛉ-ᚾ/
ᛟ-ᛞᛟᛒ-ᚾᚹᚢᛁᛇᛚᛞ-ᛁ-ᚦᚣᚷ-ᛟᛈᛡ-ᛖᚪ.ᚠᛋᛉ/
ᛞ-ᛖᚷᚦᛠ-ᚾᛋ-ᛞᛟᛗᛖ-ᛗᚾᛉ-ᚹᛒᛠᛈᛟ-ᛗ/
ᛉᚫ-ᛄᚩᛞᚻᛡᚷᚠ-ᚣᛗ-ᛁᚷᛉᚻᚹ-ᚾ-ᛋᛗᚷᛠ-/
ᚣᛚᚱᛄᛗᛉᚣ-ᛇᚱᚢᛟ-ᚣᚦᚢᛟᚩ-ᚱᚢᚹ-ᛁᛒᚳ./
ᛠᛏᛞ-ᛚᛖᛋᛄ-ᚳᛟ-ᚷᛞᛡ-ᚢᚹᛝᚻᚫᚢᛈ-ᛏᛈ/
ᚩᚣ-ᚾᛇᚦᛟᛏᛇᚳᚠ-ᛒᚪᚾ-ᛗᚦᛝ-ᛟᛠᚢᛁᚪ-ᚾᚻᛝ/
ᛉᚩ-ᛇᛁᛡᚠᛟᛒᚦᚠ-ᛋᛒ-ᚠᛞᛇ-ᚩᚦᛏ-7-ᚷ-ᛚᛄᛖᚫ/
.ᚣᛁᚫᚹᚻ-ᚫᛏ.ᛁᛉ-ᛉᚻᛞᚩᛠ-ᚫᛋᛝᛚᛝ-ᛖᚩ/
ᚻᛗᚩᛟᛒᚦ-ᚱᛚᛋ-ᚳᚻ-ᚪᛡᚾᛇᚱᛉᚦ-ᚣᛉᚻ-ᛡᚾ/
ᚢ-ᛗᛉᚹ-ᛖᛈᛖ-ᚩᚳᛈᚳᛞᚪᛉᚢᛗᛝᛟ-ᛋᚾᛟ/
ᛉ-ᚠᚱᚳᛒᚢᛄᚱᚫᛝ-ᛒᛋᛟᛠᛡᚪᛚ-ᛏᛟᚾᚫᛟᚪ-ᛁ-/
%
ᛡᛋᚳᛖ-ᚹᛒ.ᚾᛚᛝ-ᚦᚾᛁᛠ-ᛒᛡᚱᚠᛖᛁᚹ-ᚾᚠᛗᚢ/
ᚷᚾ-ᛄᛚᚳᚱ.ᛝᚣᛉᛋᚪᛟᚱᛉᚳ-ᛒᚫ-ᚠᚢᚪᛖᚪᚹ-/
ᛚᚾ-ᛄᛉ-ᚻᚦᛉ-ᛗᛚᚾᛖ-ᛏᛝᚦᚪᚩᚢᛗᚣ-ᚠᛝᚪ-/
ᚻᛡᛇᛡ-ᛚᛏᛁ-ᛇᛁ-ᚳᚢᚢᛖ-ᚳᛒ-ᚫᛇᚠᚦᚳᛚᚩᛉᛚ/
ᚩᛚ-ᚠᚳᛠ-ᚪᚠᛟᚫᚠ-ᚾᚳ-ᚢᛒᚱ-ᚾᛇᚩᛉ-ᛁᚳᛟ-ᛞ/
ᛉᛠᛝᚠᚱᛡᚳᛇ-ᛉᛟᛈᛗᛞᚳᚦᚹᛈ.ᛡᚻ-ᚾᚦ/
ᛇᛏᚹᛖᚢ-ᚫᛇᚦ-ᛝᛟᛏᚳᚷᛒᛠ-ᚪᚳᛒᚪᚩᚹᚫ-ᛉ/
ᚢ-ᚫᛖᛒ.ᛇᛏᚢᚩ-ᛟᛞᚠᚢᛋ.ᛡᛄᛗᚦᛠᛏᚪ-ᛒ/
ᚹᚣ-ᛏᛄᚻᚦᚫ-ᛚᚪᚱᚫᛟᚦᚩᚾᛟᛁᛖ-ᛡᚠᚷ-ᛋᚠᚦᛏ-/
ᛠᛡᛠᛁᚢᛡᛇᛝᛞ-ᛉᛏᚠᛒᚻᚢᛋᚳᚱᛇᚹ-ᛇᛈ/
ᛋᚢᛚᚪᛈᚢᚳᛖᚠᛞᛉ-ᚦᛠᛇᛝᚻ-ᚣᚱᛗ-ᛟᚾᛚ./
ᛈᚹᛞᚱᛄ-ᚪᛝᛞ-ᛁᚦᛏᚷᚢᚹᚳᚻᛖᚩᚪᛖ-ᛉᚪᚢ-/
%
ᚳᛁ-ᚱᚳᚹ-ᛠᛇᛏ-ᚦᚳᚻᚢ.ᛡᚹᛟ-ᚷᛇᛈ-ᚢᛈᚦ-/
ᚷᚣᚢᚪᛗ-ᚹᚳᛖᛝᚱᛠᛞᛏᚻ-ᛄᛁᛈᚻᚠᛉᛝᛈ/
ᚾ-ᛒᚳᚪᚷᛋᛟ-ᛉᛠᛈᚪᚩᚷᚠᚳᛡᛄ-ᛠᚢᚠᛋᛚ-/
ᚣᛚ-ᚢᛒ-ᛉ.ᚱᚣᚾ-ᛁᛠ-ᛚᚹᛋ-ᚠᚦᚪᛠ-ᛈᚷ.ᛏ/
ᚷᛡᛟᛠᛡᛒ-ᛉᛄᛒ-ᛖᚾ-ᛞᚠᛠᛗ-ᚦᚪᛗᚠᚪ./
ᚻᛡ-ᛗᛁᛏᛟ-ᚻᚣᚹᛏ-ᚠᛒᛁ-ᚫᛖ-ᛝᛒ-ᛚᛏᛠᛉ-ᛟ/
ᛋᚾᛉ-ᚹᛏᛠᛏ-ᛖᚢᛡᛖ-ᛉᚾᛇ-ᛟᚳᚾᚠᚩᚾᚠ-ᚳ/
ᚪ-ᚷᚱᚩ-ᛠᚦᚹᚣ-ᛒᛁ-ᛝᛇᛟ-ᚣ-ᚷᛗᚩ-ᛁᚷᛄ-ᚩᛇ-ᚢ/
ᛁᛉᛝᚪᚱᛉ-ᛏᛄᛞᛈ-ᚾᛝᚷᛏᚢ-ᛚᚷᚳᛏ-ᚢᛒᛇ-/
ᛈᚩᚣᚢᛏ-ᛡᚫᛏᚹᛏᛇ-ᛡᚫᚫ-ᚦᛏᛝ.ᛠᚳᛁᛉ/
ᚻᚦᚣ-ᚻᛚᚾᛋᚱᛡᚫᛚᚫ-ᛖᚷᚻ-ᛞᚾᚻᛠ-ᚠᚪᚹᛖᚠ/
ᛄ-ᛒᛇᚱᚹᛏᛉᚾᛠᛖᛁ-ᚠᚾᛡᚳ.ᛋᛟᚹ-ᛈᚷᛝᛟ-/
%
ᚷᚦᚠᛄᚷᚳ-ᛒᛁᛗᛚᛇᛠᚹ-ᚾᚫᚹᚷ.ᚩᚻᚪᛏᚾᛄ-ᚣ/
ᛝᛏᛡᛝ-ᚢ-ᚩᚠᚣ-ᛗᚢᛒ-ᛏᚠᛈ.ᚱᚩ-ᛉᚩᛝᛒ-ᛖ/
ᛏᚩᛉ-ᚣᛗᚠᛉ-ᛖᚩᚫᚷᚣᛚ-ᚩᛇ-ᚠᛋᚫᛇᛗ-ᛡᛟᚹ/
ᚾᚩᚢᚹᛖᛁ-ᚾᚦᚫᛠᚪ-ᛠᛚ-ᚹ-ᛡᚩ-ᚢᚦᛗ-ᛝᛚᚪᚠ/
ᛝ-ᛚᚠᛚᚳᛒᚢᛝᛉ-ᚣᛡᚪᚷ-ᚹᛟᚪᚻᚹᚢ-ᛖᛠᚷ-/
ᛁᚪᛏᛄᛗ-ᛏᛖᛁ-ᚣᛡ-ᚦᚾᚠᚦ-ᚩᛈᚻᚪ-ᚻᛋᛠ-ᛡᛉ/
ᚪᚫ-ᚠᚣᛞᛠᛇᚠᚫ-ᛏᛗ-ᚳᛡᚷ-ᚱᚢᛞ-ᛄ-ᛋᛡᛇᚩ/
-ᛚᛟ-ᚦᚱᚫᛒᛚᚦ-ᛖᚪᚦᛗᛚ-ᚦᛉᚪᚱ-ᛟᛖᛒᛄᚱᛄᛖᛁ/
ᛈ-ᚪᛖᛠᚠᛄᚢ-ᛞᚹᚦᚣ-ᛉᚷᚩᚳᛡ-ᛇᛗᛞᚳᛏ-/
ᚻᛚᚦᛝᛖᛗᚱ-ᛒᚷᛞᛉᛗᛒᛉᚳᛝᚦᚣᛞᚫᛠ-ᛋ/
ᛏᛗᛏᚻᚹ-ᛇᚳᚪᛞ-ᛠᚢᛒᛉ-ᛡᛁᛡᛚ-ᚷᛋᚦᛞ-ᚠ/
ᚢᚩᛠ-ᛚᛋᚣᛏ-ᛋᚪᛞᚫᚹᛄᛞ-ᛋᛈᛋᛄ-ᚪᛖᛁᛇᛒᛟ/
%
-ᛏᛄ-ᚠᚩᛚᛞ-ᚾᚷᚳ-ᛚᚷᛗ-ᛠᚦᚢ-ᛟᚻᚾᛟᚣᛡ./
ᛇᚻᚣᚪᛈ-ᚾᛋ.ᛞᚫᛠᚳᛉᛄ-ᚦᚹᛋᚱᚦᚫᚾ-ᛡᛚᚣ/
ᚫᛋᛖ-ᛟᚣᛝᛡ-ᚦᚣᚷᛇᚱ-ᛋᛠᛏ-ᛡᚳᛉ-ᛠᚷ-/
ᚳᛒᛋ-ᚹᚾᚻᛖᛝᛋ-ᚩᛡᛗᛉᛝ-ᛉᚦ-ᛠᛞᚳᛒᚷ/
ᛉᚹᛝᚢ-ᛉᛞᛈ.ᛉᛡᛈᛟ-ᚾᛡᚠᛡᚢᛋ-ᛉᚪᛖ/
ᚻᚱᚣᛠᛇ-ᛒᛟ-ᚪᛝᛡ-ᚳᚱᚳᛈᚩᛏ-ᚻᚣᚫᛁᛋᚩᚦᛚ/
-ᛟᛚ-ᛋᚪᚢᚪᛈᚻ./
&
%
ᚠᚢᛚᛗ-ᚪᛠᚣᛟᚪ./
3258    3222    3152    3038/
3278    3299    3298    2838/
3288    3294    3296    2472/
4516    1206    708 1820/
&
$
ᛚᚢᛝᚾ-ᚳᚢ-ᛒᚾᛏᚠᛝ.ᛁᚢᛁᚢ-ᛟᚫᛄᚠᚫ-ᚢ/
ᚷᛉᛇᛈᛉ-ᚣᛠᛚᚪᛉ-ᛟᛉᛡᚦᚻᛠ-ᚾ/
ᚪᚳ-ᚢᚷᚾ-ᛈᛖᚾᚦᚩᚢᛁᛡᚱ-ᛏᛁᛒᛇᚳᚠᚷ-ᚩ/
ᚦᚪ-ᛁᛈᚻᛡᛒ-ᚹᛈᚻᚱᛞᛉᛏᚢ-ᚣᛒ-ᚠᛋᛉᚢ-ᛗᛁ-/
ᛡᚱ-ᛝᚢᚠᚦᛝ-ᛈᛟᛒ-ᚻᚷᚻᛡᛚ-ᚩᛞᚪᚳ-ᚦᛈᛞᛋ/
ᛡᚻᛇᛚ-ᚢᛏᛋᛞ-ᚦᚢᛞᛝ-ᛚᛉᛝ-ᛏᚩᛚ-ᚪᛚ-ᚣ-ᛟ/
ᛡᛉᚣ-ᛒᚻᚫᛄᛡᛁ-ᚱᚦᛚᚠ-ᛠᚾᛝ-ᛉᛗᛒᚩᛠᛈ-/
%
ᛖᛞᚪᚫᛏᚩᛠᛖᛠᛉᚳᛠᛏ-ᚩᛞᚳᛠᚾᚳᚦ/
ᛗ-ᛞ-ᚷᛁᚳᚹᛟ-ᚪᚢᛒᚳᚫ-ᚦᚱ-ᛋᚣᚪ-ᛏᚦᛒ-ᛝᚹᛋᚱᛁ/
ᛝ-ᛒᛁᚪᚫᛚ-ᛏᚱᛡᚫᚠᛞ-ᛝᛄᚩ-ᛡᛠᛉ-ᚪᛡᚻ-ᚱᛒ/
ᛁ-ᛞᛡᛄᚪᛈᚱᛋ-ᚢᛡ-ᚻᚷ-ᛚᛟᚠ-ᚻᚷᚫᛋ.ᛈᚹᚷᚷ/
-ᛗᛟᚪᚾᚱ-ᚩᛟᛞ-ᚷᛟᚠᛠ-ᛡᚷᚳ-ᛉᛠᚠᛚ-ᛒᚫ/
ᛈ-ᚩᛄᛈ-ᛄᛗᛠ-ᚾ-ᛉᚪ.ᛡᛖᛋᚷᚫᚦ-ᛄᚷᛉᚩᚦ/
ᛄᚳᚣ-ᚢᛄᚦᛄᚪᚾᛏᛒ-ᚳᛈᛡᛄᛋᚫ-ᛋᛗ-ᚻᛞᛠ/
ᛉᚢᛗ-ᛏᛠᛖᚣᚠ-ᛄᛏᛋᛗᛞᛟᛁᛝᚪᛉᛖᛈ-ᛚ/
ᛇᛞᚦ-ᚪᛋᛉ-ᚳᛒᚢᛟᚳᛒᛚᚾᛟᛝᛉᚩ-ᛖᚳ-ᛝᛟ/
ᚳᛁᛒᛈᚫ-ᚣᛖᛄᛝ-ᛞᚢᚱ-ᛉᛟᚩ-ᚠᚹᚩ-ᚣᛁᚠᚢᛇ-ᛚ/
ᛏᛈᛒᛗ-ᛇᛝ-ᚢᚳᚱᛡ-ᛖᚩᛁᚣᛄᛏᛡ-ᛖᚠᛇᚠᛚ-ᛁ/
.ᚣᚷᚠᛝᛡᛈᚷᛒ-ᛡᚩᚷᛡ-ᛟᚾᚹᛡᛈᛟ-ᚦᛈ-ᛟᚷ/
%
ᛚᚦ-ᛈᛞ-ᚦᛇᛒ-ᛡᚪᛒᚪ-ᚾᛗ-ᚳᚾᛖᛡᚹᛝᛏᚱ-ᛝᚫ/
ᛚᛟᛁᛇᚣ-ᛝᛡᚾᛏ-ᚱᛁ-ᛋᚪᛖ-ᛇᚢ-ᛝᛞᛄ-ᚠᚱᛠᛗ/
ᛠᚪ-ᚫᛈ-ᛏᚠ-ᛖᛏᚷᚾᚠᛁᚠ-ᚱᚻᚱᛇᛒ.ᚻᛈᛏ-ᛇᚱ/
ᛝᛡᛒᚹᛚᛏ-ᛗᛉᚦ-ᚾᛄᚳᚫ-ᚷᛈ-ᛋᛖᚩ-ᚢᛝᚩ-ᛏ/
ᛈᛁᚣᚾᚪ-ᛏᚹ-ᚠᛗᚾᛟᚾᚳᛒ.ᛄᛉᛡ-ᛟᚪᛁᚫᛝ-ᛒ-/
ᛉᛏᛄᛁᛋ.ᛠ-ᚳᛖᚱᚦᚣᚩᚣ-ᛈᚫᚷ-ᛡᛄᛁᚩ-ᚱᚦ/
ᛠ-ᛇᚦᚩᛉ-ᚾᚱᚾᚫᛁᛉ-ᛁ-ᛝᚣᚫᛡᚫᛗ-ᚹᛖ-ᛇᚷᚻ/
ᛖᛗ-ᚷᚢᛞᚹ-ᛄᚻ.ᛉᚱᚢᛄᚢᚾᛈ-ᛋᚣᛄᚫ-ᛈᚳ/
ᚣᚳᛒᛡ-ᚫᛟᚪᚠ-ᛏ-ᚷᚩᛇᛟ-ᛁᚱᛗ-ᛖᛉᛟ-ᛗᛇᚫᛟ/
ᚦ-ᚱ-ᛞᛁᚢᚦᚻᛗᛡᚾ-ᛁᚦᚻᛚ.ᛏᚳ-ᚪᚦ-ᚠᚪᚫᚣᚻ/
ᛠ-ᚦᚠᛋᚠᛝᚷᚱᛈ-ᛏᛄᛉᛟ-ᚷᛚᚻ-ᚩᚪᚦᛏᚳᛁ-ᚠ/
ᚣᚢᛁᚹ-ᛟᚪᚣᛁᛠᛄᚪ-ᛟᛝᚦ-ᛟᚠᚦᚾ-ᛇᚷ-ᛠᛚᛒᚠ/
%
-ᛠᚪᛄᛇᛠᛚ-ᚱᚷᛋ-ᚹᚩᛒᛁ-ᛠᚳ-ᛁᛞᛄ-ᛖᛗᚱ-ᚷ/
ᚪᚻᛠᛚᚷᚩ-ᛉᚻ-ᛡᛝ-ᛞᚱᚹᚩᛈᛡ-ᚣᚳᚦ-ᛁᛇᚢᛁ-/
ᛟᚦᚠᚳᚻ-ᚩᛁ-ᛝᚾᛁᛞ-ᛏ-ᚫᚱᛝᚫᛈ-ᛠᛞᛇᛉᚳ/
ᛠᚩᛟᛖ.ᛗᛈᛒᚦᛝᛋᚢᛡ-ᚻᛡᛏ-ᛉᛇᚷᚠᛡᛡ/
ᛟᚢ-ᛡᚦᚣᛞᚪᚫᛝᛒ-ᚳᚩᚷ-ᛏᛞᚦᛁ-ᚠᛒᛖ-ᚦᛟᚳ-/
ᚠᚻ-ᛞᚠᚣᛋᚾᛟ-ᛠᛇᛄ-ᛖᛉ-ᚩᛈᛠᛚᚪ-ᛟᚩᚾ-/
ᛄᛉᛋ-ᚣᚫᚷᛖᚩᛟᚢᚱᚹᚢ-ᛟᛡᛄᛇᚢᛞᛉ-ᛒᛇ/
ᚳ-ᛝᛚᛗᛠᛗ-ᚪᚱᛡᛗᛒᚩᚹ-ᛋᛖᚾᚻᚣ-ᛈ-ᛞᛚᛞ/
-ᛈᛏ-ᚪᛞᛚᛉ-ᛟᚱᚾᚹ.ᛠᚠᛁ-ᛟᚾᛒ-ᛇᛟᛖᛝᚳᚠ/
ᛏᛞᛏ-ᛇᚫ-ᛝᚢ-ᛠᛡᚫᛖᛟᛞᛝᛠ-ᚠᛗᛒᛚ-ᛏ/
ᚢ-ᛈᚱᚹᛟᛇᛉ-ᚳᛟᛈᛏ-ᚢᚠᚳᛞ-ᛄᛋᛞᛈᛚ-ᚠᛝ/
ᚱᛄᚣ-ᛞᛗᛖᚣ-ᚢᛖᛝᛠᚳᛞᛈᚩᛠ-ᛏᛒᚳ-ᚷ/
%
ᚾᚩᛟᚾᚠ-ᚩᛁᚠᚢᛋᚾ-ᛞᚹᛠᛇᛈ-ᚱᚩᚩᛄ-ᚪᛟ-ᛇᛠ/
ᛄᛁ-ᛟᛄᛞᚢᚳᛝᚩ-ᚱᛝᛋ-ᛄᛁᛈᛉᛖ-ᛞᛁᚾᛗᛗᚳ/
.ᛉᚩᛁᛄᛞᚳ-ᚢᚪᛇ-ᚦᛡᛇᚻᛠᚣ-ᛠᚻ-ᚠᚩ-ᛡ/
ᛠᛋᛟᚪ-ᚹ-ᚫᚻᚩᛄᚢᚱᚩᚣ-ᛏᚫᚪᛡᚷ-ᛄᛚᛄ-ᛝᛏ/
ᛖᛒᛚᛉᚻ-ᚱᚩᚫᛇᛈᛄᛠ-ᚳᛈᛚᚣᛈ-ᚪᛠᚻᚻᛋ/
ᚫ-ᚩᛝᚹ-ᛋᛞᚠᚳᛠ-ᚩᛇᚫᚪᚩᚹᛗᚪ-ᚣᚫᚷᚫᛄᚱᚹ/
ᛞ-ᚱ-ᚦᚷᚳᚹ-ᚾᚷᛡ-ᛚᛒᚳ-ᛄᚷᚹᚹ.ᚱᛁᚠᛏ-ᚠᛚ-ᛋᛄ/
ᛚᚪᛄᚱᛏ-ᛞᚷᚫᛠᚠᛉᛞ-ᚫᚷᚻᛏ-ᛗᚣᛈ-ᛏᛒᛟ/
ᛝ-ᛄᛋᚾ-ᛝᛁᚹ-ᚦ-ᛠᛝᛞᚾᛟᚷᚫ-ᛁᛗ-ᛝᛉᚱᛞᛋ/
ᛗ-ᚠᚫᚹ-ᛟᛋ-ᚦᛞᛞᛈᛝ-ᛞᛡᚷᛒ-ᚪᛟ.ᚦᛡᛒ-ᚪᚹ-/
ᚾᛉᚫ-ᛚᛈᛁ-ᛒ-ᚠᚾᚠ-ᛡᚩᛏᛞᚾᛋᛖᚳᚻ-ᛖᚻ-ᚢᛟ-/
ᚪᛖᛗᛝ-ᛠᚫ-ᛈᚩᚪᛞ-ᚠᚫᚻ-ᚠᛏᚦᛄᛚᛄᛒ-ᛗᛇ/
%
ᛈ-ᛄᚢᛒ-ᚷᛁᛇ-ᛈᛉᚣ-ᛈᛟᚦᛞᚱᛠᚪᛡ-ᛝᛡᛒᛚ/
ᚻᚦᚫᛉ-ᛟᚫ-ᚪᛇ-ᛉᚳ-ᛠᚠᚫ-ᚢᚣᚦᛋ-ᚠᛝᚠᚱᚹ-/
ᛟᛒᛗᚷᛞᚾᛡ-ᛞᚪ-ᚻᚣᛇ-ᚱᛚ-ᛖᚣᛇᚻᛠᚩ-ᚢ/
ᚳᚱᚻ-ᛡᛟᛗᛠᛝᛄᚦ-ᛄᚢᛁᛇ-ᛄᛁ-ᛖᚷᛁ-ᚪᛇᛏ-ᛝ/
ᛡᚳᛚ-ᛇᚠᛗᚪ-ᚷᛚᛒᛋ-ᛉᛞᚫᛟᛋᛚ-ᚹᛏᛠᛗ-ᛚᚦ/
ᛗ-ᛝᚦ-ᚣᛈᚠ-ᚪᛞᛚᚪᛖᛚᚩ-ᚱᚷ-ᛚᚳᛇᛏᚷᚣᛟᛗ./
ᚪᛁ-ᚷᛄᛒᛡᛗ-ᛞᛈᚪᚳᛠᚷᛋ-ᛏᛈ-ᚩᛋᛏᛗᚱᚣ/
ᛋᛉ-ᛁᛄᛚᛝᛚᛁ-ᛉᚢᛠᛗᛇᚢᛋᚻ-ᚳᛉᛄᚩ-ᚠᛄᚠ-/
ᛁᚣᛁᛟ-ᛏᚷᚱᚦ-ᛡᛒᛋᚳ-ᛇᚢᚷ-ᛚᚱ-ᛁᛗᚱ-ᛗᛝᚻᛈ/
ᚫ-ᛝᛋᚫ-ᛖᛈᛁ-ᛒᛇᚹᚫᚢᛄᚳᛒ-ᚦᛋᚹᚦᚫ-ᛡᛟᚷᛚ-/
ᛞᛚᚢᛟᛡ-ᚱᛞᚱᛒᛄᚳᚢᛠ-ᚩᛉᛉ-ᛝᛡᛄ-ᛁᚫᛟ/
-ᛖᛗᚹ-ᛖᛉᚦᛗᚪᛋᛉ-ᛞᚦ-ᛡᚢ-ᛉᛗᚫᛋᚳᛖ-/
%
ᚳᚫᛠ-ᛞᚳᚷ-ᚩᛁᛇ-ᚾᛟᚷᚣᚳᚦᚳᚦ-ᛗᚣ-ᛈᚪᛒ/
ᛈ-ᚻᚢᚻᚾᛏᚫᛒᛇᚩᛁᛈ-ᚫᚩᚣ-ᛡᚣᛗᚷ-ᚠᚱᛡᛚ/
ᛏ-ᛖᛟᚩᛈᛚᚩᚷᛁᛟᛠ-ᛞᛖᚳᛗᛁᚣ-ᛈᛚ-ᛁᚹᛋᛄᚹ-/
ᛟᛡᚪ-ᚦᛖᚩᛄᚷᛋᛝᚣᛗᛟᚻ-ᛗᚠᚦᛉᚦᚫᛋᛈᚣᚩ/
ᚠ-ᛈᛟᛋᛖᚫᛇᛗᛚᛈᚾ-ᛡᚠᚳᚾᚩᛄᛋᛡ-ᚫᛄᚦᚪᛠ/
-ᛈᚻᛋᛟ-ᛗᚹ-ᚱᚣᛁᚢ-ᛉᚹᛋᚱ-ᛞᛈᚦᛈᚩ-ᛞᛄᚩ-/
ᚢᛈᛖᚪᚫᛉᚫ-ᛏᚱᛟᛏᛒ-ᛠ-ᚫᚳᚾ-ᛖᛝᚦᛄᛄᚠ/
ᛚᚾᚩᛒ-ᛉᚷ-ᚪᚩᛚ-ᚪᚢ-ᛞᚻᚳᚹᛚᛡᛞᛇ-ᛟᚩᛡᛚᚳ/
-ᛡᚳᛉ-ᛝᛠᛝᚷᛝᛞᛄᛏ-ᛠᛈ-ᚹᛈᛗ-ᛈᚱ-ᚫ/
ᛏᛖᚢᛝᚫᛡ-ᚾᛁᛠᚻᚦᚣᛠ-ᚫ-ᚩᛉᛋᚩ-ᛄᚠᛏᚷ-/
ᚹᛁᚪᛁᚩᛁ-ᛝᛠ-ᚾ-ᚷᛗᚹᚦᛖ.ᚷᛟᚪᚹᛞᚻᚢ-ᛡᚹ-/
ᚣᚷᛉᛒᚪᚾᛝᛡᛄᛡ-ᚠᚷᛈᚦᚠᚦ-ᛁᛈᚪᛝᛋᛞᛟᚩ/
%
ᛝᛗ-ᛁᚷ-ᛄᚷ-ᚳᚩᚦᛖᚦᛄ-ᚣᚠ-ᚦᚳᛄᛡᛖᚢ-ᛉᛄ/
ᚳᚻᛄᚱᛄ-ᚪᚻᚾᚦ-ᛚᚷ-ᚱᚦ.ᛒᚪᚩᛖᚢᛡᛄᚹᛏᚱᚹ/
ᛟ-ᚦᚳᛗᚦᚠᚫᚻ-ᛡᚠᛠᚣᚪᚦᛚᛏᛒᚢᛝ-ᛖᛋᛗᚱ-/
ᚪᚹᛒ-ᚹᛒᛗᚱᚾᛗᚻᛗᛁᚾᚪᛞ-ᛡᛖᚩ-ᚾᚹᛡ-ᚢᛄ/
ᚦᛠ-ᛚᚳᚷᛚᛇ-ᛟᛠᛠᚪ.ᛇᛉᚣᚪ-ᚷᛏᚩ-ᛖ/
ᚹᛒᛈᚷᛝᛒ.ᛡᚦᚠᛋᚾ-ᛒᚦᚠ-ᛇᛝᛠ-ᚠᚾᛉ./
&
$
%
ᚢᚪ-ᚹᛝᚷᛉᛞᚷ-ᛁᛒᛁ-ᛇᛏᛒᛁᚣ.ᛠᚷᛋᚫ/
ᛈᚹᛗᛠ-ᛇᛄᛇ-ᚹᚻᛁ-ᚷᛠᛒᚢᚣᚻᚣ-/
ᛝᚹᚢᚱᛋ-ᚩᛡᚠᛡᛠ-ᛞᛟᚦᛗᚳᚾᛉ-/
ᛞᚦᛖᚱᛇᚳ-ᚪᛄᛋᛟ-ᚢᚹᚱᛏ-ᛋᛖᛋᛏ-ᚣᚱᛠᚫᚾ/
ᛞ-ᛈᛒᛡᛋᚢᛞᛖᚣᚦ-ᛚᚹᛟᛋ-ᚷᛚᛄ-ᚫᛖᚩᚳᚦᚹ/
ᛗ-ᚢᚩᚷ-ᚠᚪᚩᛡᛝᛒᛠᚦᚳᚪ-ᚱᛡᛏ-ᛟᚹᚠᚣᛝᚢ/
ᚣᛁ-ᛚᛏᚫᚫ-ᚪ-ᚱᛈᚠᛗᚹᚩᛞ-ᛠᛒᛈ-ᛝᛟ-ᚾᚷᛗ-/
ᛡᛖᚩ-ᚾᛚᛉᛝ-ᛁᛡᚫᛗ-ᚻᛖᚹᛗ-ᛝᛈᛇᛗᛡᛄ-ᚫ/
ᚩᛡ-ᚠᚣᛉᛟᚫᚦ-ᚫᛒᚩ-ᚪᚦᛄᚱᛄᚾᚦ-ᛡᚠᚪᛏᚾᚻ-ᚷ/
ᚢ-ᛞ-ᚳᚦᚢᚱᚢᛟ-ᛞᚻᚱ-ᚷᚹᛏᛈᛖᚠ-ᚪᚻᛠᚦ/
%
ᛞᚱᚠ-ᛖᛄᚫ-ᚾᚳᚻᚹ-ᛇᛡᛈᛠᚹ-ᛗᛚ-ᚹᛟᚹᛠ-ᚪ/
ᚾᚪ-ᚳᚪ-ᚷᛚᚦᛒᚩᚹᚢ-ᚷᛚᚠᛋᚻ-ᚾᛉᛝᛗ-ᛖᚦᚢᛝ/
ᛡ-ᛈᚣᚢ-ᛉᚷᚷ-ᚹᛞᛁᛋ-ᚦᛡᛡᛈᚳᚪᚩ-ᚢᛗᚢ/
ᛉᚩᚣᚻᛏ-ᚩᚫᛗᚢ-ᚩᚾᛏᛠᛒᛟᛒᚠᛁᛈ-ᛚᛋᛝᚫᚳ/
-ᚫᛟᛏ-ᚢᚩᛉᚾᛡᛋᚠᛖ-ᛉᚱ-ᛗᚩᚩᚫ-ᚠᚢᚦᛖᛞᚾ/
ᚣ-ᛡᛋ-ᛋᚱᛚᛟ-ᚢᚻ.ᚢᚾᛈ-ᛁᚻ-ᛖᛉ-ᚦᛞᛗ-ᛈᛟ/
ᚠ-ᛈᚠᛝᚫᛝᛋ-ᛟᛄᚹ-ᛠᛒᚣ-ᛟᚹᛞ.ᚠᚣᛄᛁᛏᛉ/
ᛚ-ᚩᚦᛝ-ᚠᚪᛋᛡᛁᚻᛒᚱ-ᚪᚢᚣ-ᚫᚢ-ᛟᛠᚪᚣ-ᛖᛟ/
ᚫ-ᛖᛈᚠᛒ-ᛈᛄᛁ.ᛋᛝᛒ-ᚱᚦᚳᛇ-ᛚᛁᚢᛈᛏᚳᛒᛉ-/
ᛖᚪᚣᚠᛗᚳᚣᚱ-ᚻᚹᛏᚾᛡᛉᚫᚦᛟ-ᚳᚹ-ᛠᚠ-ᛏ/
ᛠ-ᛝᚩᚻ-ᛡᛠᛒᛋᚻᛟ-ᚫᛁ-ᛠᛏᛁᛋ-ᛏᚫᚻᚱ-ᚻᛄ/
ᛋᛡᚹᚾᚾᛡᚹᛚ-ᚢᛖ-ᛏ-ᚱᛝᚳᚣ-ᚪᛉᛇᛝᛋᛖᛇᛁ/
%
ᚻᚾ-ᚷ-ᚹᛉᚳᛉᚣ-ᛋᛈᚳᛟᚱ-ᛒᚣᛄᛝᛖᛁ-ᚾᚷᚪ-/
ᚣᚷ-ᛚᛒ-ᚢᛄᚩ-ᛝᛉᛉᚪᛖ-ᛒᚦᛉᛡᚱ.ᛏᚷᚹᛄᛋ/
ᛁᚠ-ᛠᛁᛡᚦᛝᚾᛖᚾᚠᚩᛗᛖᚣᚪ-ᚳᛖᚳᚹᚪᚫᚹ-ᛇ/
ᚢᚦᚻᛉᚢᚾ-ᛠᛚᚢᚾᚦᛈᛋᚢᛈᚱ-ᛞᚫᛟᚱᛡᚫᚪ/
ᚢ-ᚢᛗᛚᚦᛠ-ᛚᛝᛈᚣ-ᚩᛋᛟᚪᚱᛗᚦᛟᛈ-ᛚᛋ-ᛏᛁ/
ᚠᛋᛖᚹᛝ-ᛗᛞᚩ-ᛠᚫᛡᛒᛏᚩᛋ-ᛖᛏᚪᚠ-ᚫᛒ-ᛚᚾ-/
ᛋᚪᛉᛟ-ᚾᛚᚹᛖ-ᚩᛚᛁᛄᛏ-ᛒᚪᚠᛉᛏ-ᚩᛟᛄ-ᚾᚷᛋ-/
ᚷᛚᚷᛠ-ᛒᚷᛖᚩᚪᚩᛖᛞ-ᚷᛇᛗ-ᚳᚱᚷ-ᛈᛞᚩᚠᚹ/
ᛇ-ᛠᛞᚣᛝ-ᚾᛁᚠᛈᛚ.ᛖᛟ-ᚢᚳᛗ-ᛚᚫᛏᛉᛄᚱ/
ᛉ-ᛁᛠᚷᛚ-ᚷᚳᛋᚩᛝ-ᚫᚦ-ᛗᚻᛟᚠ-ᚱᛋᚳᚦ-ᚣᚩ-ᛒᛁ/
ᚫᚻᛖᚢᛏᛚᛚ-ᛇᚷᛟᚣ-ᛒᚾᚦᚻ-ᛠᛖᛄᛒᚾᛁᛚᛠ/
ᚱ-ᛄᚠᚳᛋᛝᚳᛈ-ᚷᚻᛋᛗ-ᛇᛞᛇ-ᚣ-ᛡᛖᛏᛠᚢ/
%
ᛡ-ᚩᚾᛠᚩ-ᛄᚣᛇᛉᛠᚪᛡ-ᚾᛞᛝᚻ-ᛈᛠᚻᛡ/
ᚢ-ᛝᚻᚦᛈ-ᛉᚢ-ᛠᚣᛈᛟᚦᛋᚣᛈ-ᚠᛏ-ᛒᛁᛟᚪᚷ/
ᛚ-ᛠᚻ-ᛝᛁᛡᛚᛝᚾᛞᚪᛈᚷ-ᚾᛏᚦᛋᛒ-ᛋᛋᛠ-ᚷᚳ/
-ᛠᛗᚢ-ᛖᛉᛒᚷᚫᚠᚩᛁᛉ.ᚠᚪ-ᛠᚱᛇ-ᚩᛁᛞᛋᛚ/
ᚦᛖᛒᛇ-ᛟᚷᚣᚷᚾᚷ-ᚦᚠᚳᛗ-ᚩᛖᛖ-ᚩᚠᛒᚻᛝ-ᚳᛁ/
ᛄᚪᚾᚩᚪ-ᛈᚻᚱᛗ-ᚱᛗᛟ-ᚦᚷᛄ-ᛒᚱᚦᚪᛠ-ᛉᛖᛡ/
ᛞᚦ-ᚱᛝᛄᛒ-ᚾᛏᚣ-ᛏᛋᛒᚾᚫ-ᚢᛖᛁᚩᛡ-ᛄᛇᚢᚦᛚ/
ᚳᛖ-ᛚᛁ-ᛒᚢᚠᚪᚱᛠ-ᛗᛒ-ᛞᛉᛗ-ᚢᛠᛏᚣ-ᚪᛄ/
ᛈᚢᛈᛠᚣᚷ-ᛗᛡᛗᚢᚪᛗᛝ-ᚣᛡ.ᚪᛖᛏ-ᛖ/
ᛋᚪᛟ-ᚳᚻᛁᛋᚠᛁᚾ-ᛈᛟᛝ-ᛇᚦᚣᛏᚫᛉ-ᛖᛟᛏ-ᛞᛡ/
ᛚᛖᛈᛏᚪ-ᛏᚠᚱᚾ-ᚪᛠᚱ-ᛠᚳ-ᚾᚻᚹᛒᛇᛋ-ᛁᚻᚣ/
ᛋᚹᚩᛉᚹ-ᚩᛝᚢ-ᚻᛝᛟ-ᛏᛚᚠ-ᛄᚷᛏᛝᛄᛝ./
&
$
%
ᛗᛈᚣ-ᛚᛋᚩᚪᚫᚻᛚᛖᛇᛁᛗᛚ-ᛚᛋᚳᛈ.ᚾ/
ᚻᚷᚢᛡᚻᚢ-ᛒᚠ-ᛞᛄᚢ-ᛒᛖᛁ-ᚫᚠ-ᛈ-/
ᚫᛈᚦ-ᚱᛗᛚᚳ-ᛒᚷᚣᛗᛠᛒᚫ-ᚾᚦ-ᛗᚠ/
ᛡᛠᚳᛒᚷᚫᚠ-ᛖᛄᚱᚩ-ᛈᛒ-ᚠᛒᚩ-ᛇᚱᛠᚱ-ᛠᚷ/
ᛖᛚ-ᛇᚱᚾᛋᚩᚩᚳᚪᛖᚣᛖᛖ-ᛏᚱ-ᚢᚣ-ᛟᛄᛉ-/
ᛠᚷᛝ-ᚣᛏᛝᚾ-ᚪᛏᛋ-ᛝᚪᛄ-ᚠᛚᛋᚢ-ᚹᛠᛈᛁᛏ-/
ᛁᚾ-ᚱᚱᛝᛗ-ᚣᛗᚠᛁᚫᛁᚪ-ᚢᛟᛒᚹ-ᛗᛁᚻᚣᚹᛞᛚ.ᛟ/
ᛏᛞ-ᛟᚳᛒ-ᛡᛒ-ᚪᛏ-ᚹᛏᛈ-ᚹᛠᚩᚱᚩᛖ-ᚣᛚᛋ./
ᚢᛡᚱᚠᛄᛇᚱᛡᚦᛖᚢᛏ-ᛝᚫ-ᚾᚪᛠᚩᚪᚾᚪᚦᚷᚩ-/
ᚫᛉᛒᛏᛖᛠᛗᚷᚱᛗ-ᚣᛝᚠᛒ-ᛞᛟᛞᚪ-ᛠᚱᚳᛁ/
ᛈᛞᚠᛗᛝᚻ-ᛋᚩ-ᛞᛈᛉᚾ-ᛟᚱᛡᚾᚳᚳᛏ-ᚾᛈᚠ/
%
ᛈᚳ-ᛄᚦᛒᛁᚹ-ᛞᚹᛝᛠᛡᚹᛚ-ᚹᛄᚾᚪᛟ-ᛏᛞᛉᚣ/
ᛖᚱᛞ-ᚱᛏᛇᛁᚳᛈ-ᛝ-ᚦᛟᚷᛄᚦ-ᚣᛋ-ᛠᚻ-ᚠᛒᛚ-ᛁ/
ᚫᛚᛞᛉᚪ-ᛁᚹᚷ-ᛒᚩᚹᚾᛠ-ᛋᛖᛗᛒᛋ-ᚳᚹᚦᛟᚠᚻᚫ/
-ᛞᚢᛁᛒᛞ-ᛇᛝᛈᚠᛁ-ᛟᚢᚣᛏ-ᚻᚱᛖᚾᚳᛈᛡᛈᛞ/
ᛄ-ᛁᛏᛗᛋᚫᛉᚩᚣ-ᚪᛄᛗᛡᛖ-ᛇᛄᚠᛗᚱ.ᛞᛟᚪᛒ/
ᛞᚻ-ᚾᛈᚪ-ᛇᚱᚻᚾᛝᛠᚠᚾᚠ-ᚩᛗᛋᚾ-ᛠᚪᛁᚢᛚ-/
ᚪᚫ-ᛄᛉᛡᚠ-ᛁᛖᛈᛠᚻ-ᚠᛇᚩᚹ-ᛠᛄᛇᛁᛠᚫ-ᛄ/
ᛒ-ᛋ-ᚠᛖᚷ-ᛋᛁ-ᛟᛗᛒᛁᛝᛏᚪᚢᛁᚦ-ᚩᛝᛗᚠ-ᚹᛟᛒᛟ/
ᛡ-ᚠᚣᛝᚩᛠ-ᚳᛚᛈᚱ-ᛞᛄᚩᛝᛄ-ᚪᛖᛗᛈᚾ-ᚠ/
ᛠᚷᛞᛒ-ᚩᛉᚷᚾᚣᚷ-ᛠᛈᛄᛞᚾᛟᚩᚢᚾᚹᛗ./
ᛄ-ᚢᚷᛠ-ᛗ-ᛇᚪ.ᚻᚦᛡ-ᛝᛈᛞᛒ-ᚳᛉᚳ-ᛠ/
ᛉ-ᛟᚣ-ᛒᚦᛁᛄᛚᛡᛝᛡ-ᚹᛄᚫ-ᛋᛗᚪᛡᛠᛇᛝᛏ-/
%
ᚦᛞᚷ-ᚢᛏᛚᛏᚣ-ᚢᛝ-ᚷᛟᚪᛏ-ᛄᚦᚣ-ᚫᚻᚪ-ᛒᛝ-/
ᚦᚢᚱᚪᚾᛞ-ᛁᛝᚫ-ᛚᚫᚷ-ᚹᛁᛒᚣ-ᚾᚫᚠ-ᛚᛋᛒ-ᛈᛟᚪᛟ/
ᛞᚷᛟᚣᛉᚷᛚ-ᛋᛠᛁ.ᚳᛟᛁᚦᛈᚹᛉ-ᛖᚢ-ᛟᛄᛝ/
ᛋᚢᛝ-ᚳᛡᛠ.ᛚᛇ-ᛚᚷᚢᛁᛏᛒᛋ-ᛞᛁ-ᚠᚠᚷᚠ-ᚦᛄ/
ᚳ-ᚫᛟ-ᛁᛗᛡᛁᛇᚦ-ᚩ-ᚢᛈᛒ-ᚻᛋ-ᛄᚣᛄᛖ.ᛒᛇᛇᚱ-/
ᚹᛄᛏᛡ-ᚳᚪᚫ.ᚩᛈᚱ-ᛡᚾᛗᛁᛝ-ᚻᚹᚦ-ᛡᚦᚻᚦ-ᛉ/
ᚫᚫᛋᚳᛡᚾᛇ-ᛟᛉᚢ-ᚱᛄᛖ-ᛚᚾᛞ-ᛗ-ᛏᚱᛟᚦ-ᛁᛝ/
ᛡᛒ-ᚳᚩᚹᛟ-ᛏᛗᛋᚱᚷ-ᚱᛚᛞᛚ-ᚩᚣ-ᛞᚳᚪᛖᛞᚠ/
ᚳ-ᛇᛖᛉᛚᚫ-ᛖᚩᛁᛋ-ᛡᛁᛟᛋᚪᛒᛗ-ᛗᚣᚹᛄ-ᛖᚫᛝ/
ᛚ-ᛄᚱᛇ-ᛈᛚᚩᚻ-ᚪᛞ-ᛡᛄ-ᛞᚠᚹᛞᛄᚳ-ᚾᚦᛉ-ᛄ/
ᚻ-ᚷᛚ-ᚠᛖᚦ-ᛇᚻ-ᛝᛖᛒᛚᛞᛁᛗᚠ-ᚹᛒᛗᛟᛁᛖᛁᛠ-/
ᛈᚻᛝᛖᛞᛟᚩᚻᛄ-ᚹᚩᚾᛄᛈᛗ-ᛖᚳ-ᛖᛇ-ᚷᚻᛗ/
%
ᛞᚪᛈᛖ-ᛗ-ᛉᚫᛒᛇᚱ-ᛖᚣᛟᚣ-ᚱᛠᛈᚢᛠ-ᚣ/
ᛖᚪᚻ-ᚩᛉᛠᚢᚻᛡᛟ-ᚷᚫᚩᛒᛉ-ᚫᚱᛞᛋᚩᚱ-ᚷ/
ᛠ-ᛉᚻᛁ-ᚷᚳᛞᛠᛡᚳ-ᛄᛠᛉᛇᚻᛋᚹ-ᛝᛡᚷ/
ᛖᛡᚣ-ᛠᚩᚷ-ᚱᚦᚠᛟᚩᚦ-ᚦᛁᛏᚱ-ᛇᛉᛇ-ᚢᚷᛠ-/
ᛟᛏ-ᚩᚠᛚ-ᛟᛝᛈ-ᚱᛡᚪᚩᛏ-ᚩᛠᚷᚫᛗ-ᛈᛋᚱ-ᛖ/
ᚦᚠ-ᛞᚹᚾᛚ-ᛝᚩᛇᛄ-ᚳᛚᚢᚹᛏ-ᚩᛖᛏᚠᚪᛚ-ᛟᛇᛟ-/
ᛠᚱᛇ-ᚢᚪᚦᛈᛟᛡᛉ.ᛡᛒᚱᛒᚠᚢᛚᚢᛟ-ᛒᛇᛒ-/
ᛉᚦᚹ-ᛝᚣᛖ-ᚳᚫᚣᛟ-ᚹᛁᛝᚫᛏ-ᚫᛇᛈᛡᛟᚠ-ᛚ-ᛝ/
ᚠᛡ.ᛞᚪᛚᛈ-ᛋᛁ-ᚢᚣᚪᛚᛠᛝᚹ-ᚪᛏᛈᚳᚣ-ᛝᚫ/
ᚻᛗᛞᚷᛚ.ᛠᛉᛒ-ᛇᛡᛋᛖ-ᚣᛁᛚ-ᚣᛠᚣ-ᚻ./
ᚣᛉᚾᛏᚫᛉᛋᚦᚪᚹᛗ-ᚪᚱ-ᚪᚩᚻ.ᛗᛖᚫᛞᛠᛁᛗ/
-ᛒᛟᚾᚳᚩᚱᛉ-ᛋᚹᚫ-ᚻᛖ-ᛋᚠᚾ-ᚢᚦᛟᚷᛖᚪᛟᛇᛇ-/
%
ᚦᚳᛒᛝᛏᛉᛡᛞ-ᛋᛡ-ᚩᚠ.ᛈᛖᛞᛋᛁ-ᛚᛁᚻᚾᛝᚱ-/
ᚻᛈ-ᛇᚢᚫᛞ-ᛚᚻᛉᚳᛈ-ᛁᛗᛉᚳ.ᛄᚫᚾᛞᛋ-ᛏᛚ/
ᛡᚩᛋᛗ-ᛚᛞᚾ-ᛈᚫᛏᚷᛈ-ᚫᚦᛄᛗ-ᛒᚻᚩᚻᛁᚷᚻᚳ-/
ᛚᚹᛋᚱᛇᛗᛏ-ᛄᚳᛁ-ᛠᚦᛞ-ᛏᛚ-ᚱᛖᛠᛒᚪ-ᛒᚠᛒ-ᛁ/
ᛒᛡᛇᛏᚣ-ᛏᛖᚣᚳᚱᛋᚠ-ᛁᚦᚪᛉ-ᚪᚣᚫᛠ-ᛄ-ᛈ/
ᛗ-ᚠᛋ-ᚪᛒᚱ.ᛉᚣᚻ-ᚦᚩ-ᛇᛞᚢ.ᚠᛁ-ᚻᚩᚫᚠᚣᚷ/
ᚱᚪᛄ-ᛏᛉᛇ-ᛖᛠᛞ-ᛏᚠᚢᛝ-ᚫᛄᛖᛈᚳᛒᚦᚢ/
ᛝ-ᛡᛒᚹᚱ-ᛖᚾᛈᛇᚣᛇ-ᛉᚱᚹ-ᛒᛡᛞ-ᛖᚱᚩᚻᚣ/
ᛠᛈᚦ-ᛗᛁᚷᛚ-ᚹᛉᚫ.ᚠᛞᚾ-ᛄᛟ-ᚻᛚᛡ-ᛗᛖᚷ-/
ᛟᛁᛡ-ᚻᛟᚱᛇᚹᚣᚠ-ᛈ-ᛄᚷᚦ-ᚪᛒᛝ-ᛈᛒᚪᛖ-ᚢᚹᚻ/
ᚩᛒᛋᛉ-ᚹᛞ.ᚦᛇᚱᛖ-ᛄᚾᛞᛝᚹᚪ-ᚻᛖᚹ-ᛟᛡᛄ/
ᛡᛟᛝᛄᛉᛚᛄ-ᛞᛉᛟᛈ-ᚱᚪᛁᛏᚷᛉᛝᛇ-ᛠᛗᚩ/
%
ᛚ-ᚦᚫᚹ-ᚫᚢᛈᛡᚳ-ᚹᛝᚻᚹᛒᛗᛋᛟᛖᛁᛡ-ᛟᚹᚦᚻᛒ/
-ᛡᚱᛏᚦᚠ-ᚠᚩᚦ.ᚻᚩᛗᛖᛉᚹᛞᛋᛚᚠᛞ-ᛝᛒᛇᛡ/
ᛚᚪ-ᚹᛞᚾᚫᛉᛏᚣᛗᚷ-ᚦᚹᛉᛡᚦ-ᚹᛒᛋᚱᛉᛡᛉ/
ᚪ-ᚢᛒᚻᛠ-ᚹᛝᚢᚻᛇᛝᛡᛠᛄ-ᛋᛈᚦᛏ-ᛟᛝᚩ/
ᛗᛒᚢᛞᛋ-ᛒᛄ-ᛠᚱᛟ-ᛖᚾ-ᚾᚹᚷᚢᛚᚪᚩᚣ-ᚢᛏ/
ᚠᛄᛏ-ᚪᚷᛒᛇ./
&
$
%
ᛞᛇ-ᛉᚳᚠᛁᚪᚹᚻᚷ.ᛇᛟ-ᚠᛏᛖᛟᛠᚪ/
ᛡᛋᚷ-ᚣᛠᚾᚦᚫᚱ-ᚩᛡᛗ-ᚹᛉᛗ-ᚣ/
ᛞᛒᛏᚱ-ᚢᛄᚻ-ᚫᛟ-ᛡᛝᚹᚻᛋᚠᛡ-ᛚᚦ/
ᛏ-ᛁᚹᛏ-ᚩᚢᚾᚹᛗᛚ-ᛋᚦᛠᚹᛄ-ᚪᛄᚫᚷᚣᛗᚹᛞ-/
ᛈᛡ-ᛖᛄᚹ-ᛖᚢ-ᚻᚹ-ᛝᛁ-ᛋᚫᚷ-ᛄᛚ./
&
ᛝᚦᛇ-ᛁᚠᚳᛟᛇ.ᛞᛒᚣᛡᚣᚢ-ᚣᚾᚦᚱᛖ/
ᛗᛁ-ᛇᛞᚱᚹ-ᛉᛒᚻ-ᚳᛄᛡᚪ-ᚾᚹ-ᚾᛗ-ᚠ/
ᛇᛁ-ᛇᚪ-ᚩᛋᛒᛟ-ᛏᛄ-ᛈ-ᛖᛈᛄᚩᚹᚢᛠ/
ᛝᚹ-ᛗᚳᚩᛏᛏᚠᚢᛄ-ᛞᛠᛉᚩ-ᛉᚦᚷᛞ-ᛒᚩᛏᛚ/
ᛇᛁᛒᛡᚪ-ᛖᚠᛠᚢᛖ-ᛈᛋᚹᛞᛞ-ᛋᛡ-ᚹᚦᛞᛋ-ᛝ/
ᛄ-ᛚᚷᚢᛡ-ᚾᛉᚠ-ᚱᚪᚣᛗᚠᚦᚻ-ᚱᚪᚱ-ᚫᚪᚷᛟᛞ-ᛒ/
%
ᛗᛒ-ᚾᚻ-ᛇᛞ-ᚻᛗᛚᛁ.ᛠᚾᛁ-ᚫᛖᚢ.ᛏᚦᛇᛋᛈᚻ/
-ᚻᛇᚳᛠᚫ-ᛞᛚᛋᛝ-ᛁᚹ-ᚪᚳᚩᛏᛇᛝᚷ-ᚳᚦᛋᛠᚠ/
ᚢᛝᛚᚻ-ᚹᚩᛇᚪᛈᚷ-ᛇᛗᛚᛄᛋᛏ-ᛚᚳᛈ-ᚾᛋᛝ-ᚳᚪ/
ᚳ-ᚾᛉ-ᚾᚢᛉᚫᛗᛏᛞᛏᚫ-ᛟᛗᛋᛉ-ᛏᚣᛉ-ᛇ/
ᛠᚷ-ᚻᛒᚾᚷᛇᚢᛟ-ᛄᚦᛉᚩ-ᚾᚪ-ᛞ-ᚩᛈ-ᛠᛚᛋ/
ᛏ-ᛒᚷᛁᚢᛟᛖᛁ-ᛄᚦᛖᚻᚹ-ᛄᚫᛄᚾᚻᛉᚹ-ᛒᚪᛋ-ᚠᚱ/
ᚱᛁᛉᚢᚦᚻ-ᚢᛗᚪ-ᛞᛝᛠᚪ-ᚫᛉᛖᚾᚹ-ᛟ.ᛝᛞ/
ᚾ-ᛈᚫᚳᛡ-ᛈᚠᛉᚩ-ᛒᚷᛗᚫ-ᛚᚻᛞᚣᛖᛉᛒ-ᛄᚹ/
ᛇ-ᛈᚩᛁᚦᚠ-ᚷᚾᛈᛞᛝᛏᛖᚪ-ᛄᛋᛠ-ᛈᛝᚢ-ᛒᚷ/
ᚳᛉ-ᚪᚢᛈᛚ-ᛄᚱᚷᚣᚪ.ᚪᚠ-ᛗᛝᚣᚳᛟ-ᚹᚣᚷ/
ᛈ-ᛗᛖᚩᚹᚢ-ᛟᛞᛋᚱ-ᚣᛞᛋᚳᛡᛉ-ᚻᚦᚹᛚᛞ/
ᛠᚩᛞᛠᚢᛟᛖ.ᛠᚹ-ᛉᚻᛡᚹᛞ-ᚪᛗ-ᚠᚦᛈ-/
%
ᛝᛏᚳᚪ-ᛠᚣᚷ-ᚳᚦᛖᚾᚢᛁᚫᛁᚢᛡ-ᚹᛚᚳ-ᚻᛈ-ᛞ/
ᛄᚳ-ᛗᛒ-ᛗᚪᛄ-ᚩᚪᛞᛁ-ᚩᚱᛟᚠᛖᚣᛟᛁ.ᛇᛟ-ᛁᛈᚣ/
ᛚᚪᛡ-ᚳᛏᛠᛋᛖᛒᛝ-ᚫᛟᚫᛞᛖᛞᚣᛡ-ᛠᚪᛖ/
ᚦᛚᚫ-ᚳᛋᚪᚩᚷᚹᛚ.ᛈᛖᛏ-ᛄᛉᛝᛚ-ᛏᛉᚩᚣᛝ/
ᚠᚩᚣ-ᛁᚻ-ᛟᚫᚷᛄᛝᛡᚾᛗᚣᛟᛡ-ᛝᚷᛖᛉ-ᛟᛉ/
ᛈᛚᛋᛉᛠ-ᛚᛡ-ᚱᚪᛞ-ᛠᚷ-ᚱ-ᚳᛇᚻ-ᛗᚪᛟᚷ-/
ᛞᚪᛋᛡᚻ-ᛈᚷᛖᚳᛟᚱᛟᚢ-ᛁᚫᛟᚦ-ᛄᚱᛡ-ᚱᛖᚦ/
ᚣᛏᛝᛡᚩᛒ-ᛏᚦᚳ-ᛉᚳ-ᛋᚪᚫ-ᛗᚠᛄᚱᛖ-ᛡᛇᛁᛇ/
ᛟᛉᚳᚹᚪᛖ-ᛋᚢᛉ-ᛋᛟᛚ-ᛄᚾ-ᛈᛇᛒ-ᚦᚦ-ᛁᚫᛚᛋᛝ/
ᛄᛄᛡ-ᛟᚻᛇᚢᛚ-ᛁᚱ-ᛡᚻᛚᛏᚹᛉᛇ-ᚱᛏᛠ-ᛁᚫᛚ/
ᛗ-ᛁᚱᚷᛏᛠ-ᛇᛟᚻᛟᚳᛋᛏᚾᚩ-ᛁᚱᚷ-ᚹ-ᛞᚢᚣᛚᛁ/
ᛗᛒᚢ-ᛚᚱ-ᛏᛁᚢ-ᚷᚳᚠᛇ-ᛚᛇᚣᛏ-ᛏᚫᚢ-ᚫᛠᛇ/
%
ᚣᚾ-ᚢᚹᛝᚻ-ᚷᚣᚱ-ᚩᛁ-ᛚᚾᛉ-ᚾᚩᛈ-ᚠᛠᚫᚫᚩ-ᛉ/
ᚾᛋᛟᚫᛚ-ᚾᚫ-ᚦᚢᛠᚣᚫ-ᛈᛁᛇᚢᚱᛄ-ᛈᛟᛄᚪᛝᛈ/
ᚦᛈᚪᛝ-ᚣᛗᛟ-ᛉᛒᚢᛏᛇᛗᛈᚫᚣ-ᛉᚫᚣᚱᚫᚣ/
ᚠᚠᛗᛡ-ᛉᛖ-ᚱᚢᛏᚷᚢᚣᚱ-ᛡᚢᚩᛇᛁ-ᛄᚠᛈᛄ/
ᛞ-ᛁᚦᚩᚻᛡᚷᚻ./
1-ᛚᚦᛇᛟ-ᚪᚫᛠ-ᛗᛉᚻᚳᛉᚪᛏᚦ-ᚫᛉ-ᚩᛋᚳᛞ/
ᛏ-ᚣᚹᚾ-ᛟᛏᛉ-ᚹᛁᛟᛄᚠᛁᚩ-ᛁᚱᛋ-ᛉᚾᛗᚪᛡ-ᚱᛈᛋ/
ᛞ-ᛁᛟ-ᚻᛖᛏᚢᚹ-ᛠᛟᛞᛟᛄᛁᛝᛡ-ᛄᚱᛞᛗᛒ-ᚩ/
ᚳᚩ-ᚦᛟᚱᚢᛚ-ᚢᚦᛋᚢᛞᛚ-ᚷᛁᚣᛝᚩᛟ-ᛁᛖᚣ-ᛖᚠ-/
ᛇᛝᛒᛚᛁᚢᚣᚠᛟᚾᛟ-ᛒᛟᚷᛄᚪᚾᛗᚫ-ᚣᚦᚠ-ᛁᛒᛝᛈ/
ᚾᛁᚱᚷ-ᛄᛇᚫ-ᚻᚪ-ᚱᛉᛉ-ᚩᛚᚾᚫ-ᛞᚣᛒᚾᚪ./
%
2-ᚾᚣᛖᛉ-ᚾᚢᛉᛁ-ᛝᛏᛈᚹᛋᚣ-ᛏᛠᛈᛉ-ᚪᛁ/
ᛄᛋᚱᚪᛏᛋᛝᛏ-ᚳᚷᚳᚻ-ᛖᛟᚱᚪᛡᚻᚳ-ᛝᛒᛖᚱ/
ᛠᚪ-ᛚᛟᛖᛚᚪ-ᚦᛋ-ᚳᚹᚱᚹ-ᚩᚻᚣ-ᚢᛝᚩ-ᛈᛚᛁᛏᚪ/
-ᚠᛋᛝᛞ-ᚳᚪᚱᛒ-ᚹᛈ-ᚾᚩᚦᚳᚦᚾᛗᚩᛖ-ᚣᛇᚾ-ᚠᛒ./
3-ᛞᚢᛈ-ᚹᚾᛖᚪ-ᚱᛚᛁᚹ-ᚫᛉ-ᛝᚠᛞᚪᚠ-ᛒᛄᛉ-ᛞ/
ᛄᛝᚣᛇᚪ-ᚫᛄ-ᛝᛈᚪ-ᚢᛠ-ᛇᛏᚱ-ᛖ-ᚫᛗ-ᚫᛠ/
ᚻ-ᛁᚫᛟ-ᛠᚹᚳᛄᚦᚻ-ᛡᚩᚢ-ᚩᚦᚷᛡ-ᚻᛋᚷᚪᛁᛟᛞ/
ᚪᛄ-ᛁᚹᛡᛒ-ᛗᛝᛡᛞᚠᛒᛋᛏ-ᛒᚷᚠ-ᚷᛟᚢᚳᚫᛏᛁ/
ᛖ-ᚱᚷᛗᚣ-ᚪᚷᚹ./
4-ᛝᛄᛋᛄᛗᚱᛗ-ᚾᛒᛋᛗᛉᛞᚻᛉᛁ-ᚣᛡᚻᚣ/
ᛠᛉᚻ-ᛞᛖ-ᚹᛖᚦ-ᚢᚳ-ᛉᛗᚪᚣᛠ-ᚹᚫᚪᚳ-/
%
ᚢᚫᚳᛇᚳᚣ-ᛡᚫᛏᛖᚳᚠ-ᛋᚻ-ᛋᚱᚢᚦ-ᛁᛋᛝᛗᛞ/
ᚫᚢᛠᚢᚪ.ᚾᛝᚳ-ᛖᛈᚹᛉ-ᚢᛉᚫ-ᚾᛈᚳᚻᚱᚣ/
ᚹᛚᛉᚱᛒ-ᛗᚫᛟᚣᚩ-ᚳᛇᛗ./
5-ᚻᚫᛉᚦᛒᛟ-ᛏᛟᚹᛄ-ᚫᛠᛗᚠᚫᚳᚷ-ᛇ-ᚻᚹᛗ/
ᚻᛝᚣ-ᛁᚩᛁ-ᛏᛁᛖᛡᛄ-ᛗᚣᛚ-ᚻᚱᚩᛞᛒᛡᛈᛠᛗ-/
ᚳᛠ-ᛖᛒᚢ-ᚷᛁᚦ-ᛟᚫ-ᛡᚻᛝᛖᚾ-ᚱᛠᛡᛋ-ᚻᛏ/
ᛝᚻᚪᚷᚩᛝᚫ-ᚹᛚᛏᚱ-ᚷᛁᚾ-ᛖᛠᛄᛡᛞᛋᚻ-ᛝᚾ/
ᚳᛋᚾᛞᛇᚾᛋᛁᚳᛡ-ᚱᛝᛚᚫᚣᛇᛚᚩ-ᚳᛞᚾ-ᛝᚷᛡ./
ᛝᛄ-ᚻᛄᛚᛠᛟ-ᛄᛏᚷ-ᛚᛒᛝᚢᛏ-ᚻᚳ./
&
ᚫᛞᛟᚫᛟᛗ-ᛟᚫᚪᚻᚱᛗᚢ-ᚣᚢᚣ-ᛈᛗ-ᚪᛄᚫᛟ/
ᛠᛚᚠᛖᛡᚢ-ᛉᚻ-ᚪᚩᛡᛒᛠᚢᚷ-ᚻᛏᛠᚪᛞ-/
%
ᛋᚹ-ᚦ-ᚾᛋᛁᚻᛒ-ᛉᛠᛝ-ᛒᚢᛚᛟᚢᚾ-ᚢᚦᚩᛗᚪ-ᚾ/
ᛞᚫᛇ-ᚫᚣᚪᛋ-ᚣᛝᛡᛗᚷᛇᚾᛈ-ᛠᚳᚻᛝᛚ-ᚠᚷ/
ᛡ-ᛁᛡᚪᚠᛒᛈ-ᚳᛋᚦᛠᚦᚫᚱ-ᚷᛞᛚᛟ-ᚷᚱᛁᛇ-ᚣᚩ/
ᛟᚢᛝᚱᚷ-ᛗᛏᚷᛒᛈᚷ-ᛗᛏ-ᛗᚣᚹᛒᛏᛒ-ᚷᚣᛈ/
ᚷ.ᚾᚦᛇᛒᚳ-ᚷᛖᛇᛟᛚᛈ-ᚹᚾ-ᚻᚷᚱᛇᛏ-ᛈᚷᛒ-ᚹ/
ᛗᛋᚹᛟᚻ./
&
ᛡᚳᛋ.ᛈᛞᛋᛡ-ᚪᚹᛏᚳᚹᛟ-ᛗᚹᛁᛒᛞ-ᚷ/
ᛇᚢᛚ-ᛉᛋᚫ-ᛟᚻᛚᚦᛒ-ᚣᚪᛚᛞᚦᚠ-ᚻ-/
ᛞᛝᚩᚢᛋᚪᚫ-ᛖᚦᛁ-ᛏᛄᛏ-ᛝᚦᚾᚳᛉ/
ᛏᛝ-ᚳᛈᛁ-ᚾᛏ-ᛒᚾᛡᚱᛒ-ᚢᛈᛋᚦᛁᚳᛈᛋᛁᚹ-ᚹᛚᚣᚾ/
ᚢ-ᛒᛁᚪᛠ-ᚹᛟᚳ-ᛠᚢᚪ-ᛚᚦᚹ-ᚠᚾᛏᚳᛡᛁ-ᛚᚩ-ᚾ/
ᛗᛄᛠ-ᚦᛟᛄ-ᚪᚦᚹ-ᛡᚾᛖᛠᛈ-ᛒᛋᛄ./
&
$
%
ᚠᚾᛗ-ᚣᚷᛞᚫᚻ.ᚪᛈᛉᚣᚻ-ᛇᛠᚩᛖ-ᛏᛝ/
ᛠ-ᛚᛁᛏᚦᚠ-ᛗᚪᚳᛖ.ᛞᚳ-ᛏᚱᛟᚷᛠᚾ/
ᚫᛒᚢᛖᛒᚢ-ᚦᚠᛟ-ᚷᛋᛟ-ᛁᛈ-ᛟᛉᛋᛒ-ᚹᛄᛒ/
ᚣᛗᚢᛠ-ᚱᛁᚢᛟᛄᛁ-ᛗᛖᚫ-ᚱᛋᛉᛝ.ᛠᛈᛚ-/
ᛞᚩᛚᛁᛉᛠᛝᛖᚱ-ᚾᛈᛖᚹᛡ-ᚾᛄᛏᚣ.ᛋᚩᛋ/
ᛏᛝ-ᚢᚾᛇᚪ-ᛖᛏᚪᛄᚳᚣ-ᛟᛒ-ᛚᛋ-ᛒᛞᛄ-ᛁᛝᚣᛖ/
ᚳ-ᛄᚻᛚᚣ-ᚷᚫᛚᛞ-ᛚᚫᛚᚦᛉ-ᛚ-ᛖᛉᚩᛉᛁᚳᚢᛗ/
ᚾᚢ-ᚩᚾᛇ-ᚻᛡᛚᛇᚩᚫᚪ-ᚩᛟᚩ-ᚣᚱ-ᛖᚠᚢ.ᛁᚻ-ᛟᛚ/
ᚾᛏ-ᚠᛞᚱᛠᚷ-ᛈᚩᛇᚩᛗᛠᛒ-ᛄᛡ-ᛋᛗᚠ-ᛏ/
ᚠᚫᚩ-ᛟᚳᛚᛞᛡᛚ-ᚩᚳᛝᚢ-ᛈᚹᛏ-ᚷᚳᛋ-ᚢᛟᚷᚦ-/
ᚠᛉᚠᛏ-ᚳᛋᛉᛟ-ᚷᚠᛉᚾᛞ-ᛒᛏᛠᛡ.ᛈᛡ/
%
ᛠᛁᚪ-ᛋᚣᛗᛞᚣᛋ-ᛒᛞᛄᛞ.ᚩᚾᛏᛚ-ᚳᚪᛝ-ᚱᚷ/
ᚻᚷ-ᛄᚹᚠ-ᚪᚢᛇ-ᛞᛏᛗᛄᛁ-ᛝᚫ-ᛉᛈᚳᛈᛠ-ᛟᚪ/
ᛒᛁᛁᛋ-ᛇᚷᚻᛋ-ᛇᛡᛒ-ᚠᚹᛝ-ᚫᚪᚠᚩᚣᛡᚪᚾᚻ-ᛒᚦᛟ/
ᛇᚣᛟᛁᛒ-ᛟ-ᚩᛋᚹ-ᛞᚳᚠᚪᛁ.ᛉᛏᛟᚢᚩᛟᚦᛈᛋᚩ-/
ᚻᛇᚦᛝ-ᛏᛠᚠᛝᛠ-ᚩᛗ-ᛏᚠᚣᛚᚣ-ᚹᛚᛞ-ᚪᛉ/
ᛠ-ᚪᛄ-ᚩᛋᛒᛚ-ᚳᛖᚾᚪᚩᚱᛏᚦ-ᚱᛒᚳᚣ-ᛠᛗᚹᛚ-/
ᚻᛈ-ᛇᛈᛖ-ᛚᛄᚩᛡᚪ-ᛖᛋᚫᚩ-ᛠᛉᛝᚣ-ᛖᚫᛒ/
ᛗ-ᛖᚻᚱ-ᛈᚾᛗ-ᚹᛏᛟᚣᚢ-ᚠᛉᛈᛗᚩᚷᚾ-ᛡᛇᚳ/
ᚠᛒᛈᛗ-ᛋᛇᛁ-ᛖᛈᚢᚱᛏᚳᚣ-ᛄᛚᚠ.ᚱᛚᚱᚫᛖᚻᛟ/
-ᛇᚣᛡ-ᚩᛉ-ᚪᛋᚣᛁᛝ-ᛉᛚᛄᚳ-ᛖᚣᚢᛝᚦᛇᚱ-/
ᛠᛁᚫ-ᚦᚠᛟᚷᛠᛁ-ᛈᛋᛒ-ᛗᛒᛄᚠᚾᚳᛖ-ᚻᚫᚩᛄ-/
ᛉᛄᛚᛈᚪᛁ-ᛟᚹᚱᛁᚱᚦᛖᛉ-ᚪᚾ-ᛞᛄᚷ-ᛟᛟᚳᛏᛄ/
%
ᛞ-ᛉᚾᛗᚦ-ᛁᛄᚱ-ᛈᛉᚢᚫᚦᛒᚠᛄᚦ-ᚠᚪᛝᛖ-ᚹᚹᚣ/
ᛚᛇ-ᚢᚣ-ᚾᚱᚪ-ᛈᚾᚹ-ᛚᚾᛏᛚᚢᛒᚱᛝᚪᛋ-ᚫᛈ-ᛄᛚ/
ᚢᚳᚷ-ᛚᛏᛄᚹᛈ-ᚫᛗᛚ-ᛉᛚᛗᛏᛞᚠᛈᛁ.ᚠᚳᚦ/
ᛗᛄᚹᚱᚪᛚ-ᚩᛝᚱᚢᛈᚱᛟᛡ-ᚳᛉᚱ-ᛇᛏᚦᚾ-ᚱᛇᚫ/
ᛞᛟᚻ-ᛒᚾᚣ-ᚠᛡᚪᛡᛖᚫᛞᛄᚢᛖ-ᚦᚱ-ᚩᛇᚱᛡ-/
ᚣᛁᛉᛇᚻᚩᛠ-ᚫᚻᛡᛝᛠᚦ-ᚾᚣ-ᚾᚠᛁᛝ.ᛏ/
ᚻᚹᚫ-ᛒᛇ-ᛡᚻᛉᛒ-ᛞᛝᚱᛄᚦᚻ-ᚪᚷᚣᛁᚠᚷ-ᛁᛏᛞ/
ᛠᛒᚠᚩᛈ-ᛇᛡᛟᚹᚱᚾᚩᛏ-ᛋᚹᚢ.ᛖᛡᛖᛡᚦ-ᛉ/
ᚪᚷᛈᚾ-ᛋᚱᚠᛞᛝᚻᛖᛄᛞ-ᛄᛡ-ᚱᚹ-ᚷᛝᚪᛒ-ᛄᛈ/
ᛄ-ᛏᚠᛉ-ᚪᛄ-ᛁᚠᛉᚢᚩᚣᚻᚦ-ᚻᚾᛁᛒ-ᛡᛟᛡᛋᛈᚣ/
ᛉ-ᛠᚢᛠᛚ-ᚠᛝᛗᚻ-ᚦᛒᚩ-ᛗᛚ-ᚩᛠᛋᚦᛠ-ᛇ/
ᛋᛉ-ᚠᛗᛒ-ᚫᛋᛇᚾᛡᚾ-ᚢᚫᚹ-ᛞᛠᚢᚾᛝᚠᚾᛖᚫ/
%
ᚻᛄ-ᛁᛖᛏᛡ-ᚷᛁᚩᚾ-ᚳᚢᚫᛗᛈᛋᚪᛡ-ᚷᛚᚣᚹᛟ-/
ᚠᚢ-ᛉᚠᚫᛞᚠᛡᛄᚾ.ᚻᛋᚦᚠ-ᛏᚠᛄᚱᚹᚠᛋᚾᚹᛄ/
ᛖᛒᚢᚦ-ᚩᛇᚫᛈ-ᛡᛟ.ᚢᛁᚩᛄᚩᛇᛟᛄᛞᚩ-ᛈᚹᛞ/
ᚷᚱ-ᚠᛟ-ᛇᚷ-ᛄᛟᛇᚫᛋᚫᚣ-ᛒᛏᛞᛟ-ᛠᚻᛡᚱᛠ/
ᛠᛉᛋ-ᚠᚾᚣᚱᚠ.ᚪᚾᛡᚪᛖᚫ-ᚳᛇᛁᛝ-ᛒᛡᛞᛠ/
ᚫᛒᛠᚳᛉᚠ-ᚫᛏᛁᚱᚪᛗᚩ-ᛚᛉᛋᚪ-ᛒᚩᛈᚫᚩᛝᚻᛇ/
ᛖᛇᚫ-ᚻᛖᛇᛠ-ᚱᛗᛞ-ᚫᛇᛗ.ᚾᚾᚣᛡ-ᚱᚾᛗ/
ᛠ-ᛄᛉᛋᛄ-ᛟᛖᛒ-ᛏᚻᚾ-ᚠᚪᚠ-ᛒᚾ-ᚩᚾ-ᛖᛋᛏᛒᚹ/
ᛡ.ᚻᛏ-ᚩᛟᚩ-ᛒᚾᛖᚳᛁᚹᚣᛟ-ᛟᚩᛒ-ᛋᛖᚩ-ᚫᚻᛟ/
ᚠᚫᚷᚩᛄ-ᛟᛒᚻ-ᚳᛖᛁᛚᚫᚣᛚ-ᚢᛚᛁ-ᚾᛟᛏ-ᚫᛈᛟᛈ/
ᛝᛗ-ᚳᚢᛁ-ᚣᛋᚳᚢᛡᛇᚩ-ᚠᛖ-ᚷᛟ-ᚻᚫ-ᛝᚠ-ᛗᚠ/
ᛝᛉᛞᛁ-ᛗᛝᚣᚪᛝᚠᛉᛁᛟᚷᛚ-ᛇᚩ-ᚫᛡᛏ-ᛄᛏ/
%
ᛠᚢ-ᚷᚦᚣ-ᚦᚾᛟᚣᚩᛖᚻ-ᛁᛋᛖᚣᚦᚪᛡᛝᛟᛇᛚ-/
ᛡᛏᛝ-ᛁᛚ-ᚠᛉᛡᛠᛏ-ᚠᚾᛄᚠᚻᚳ-ᚻᛞᛠᚣᛟ/
ᛝ-ᛉᛇᚻᚩᛋᚻ.ᛇᛏᚠ-ᛚᚱᛇᚦᚪᛁᛁ-ᛒᚠᛁᛚ-ᛄᛡᛒᚣ/
ᛗᚫᚫ-ᛞᚻᛟ-ᚪᚹᛉᛚᛏᛁᚪ-ᛟᛞᛖᚾᛈᚻᚣ-ᚦᛚᛖᛋ/
ᛖᛟᚫᛖ-ᛏᚱᚪ-ᛁᚫᚹᚫ-ᛋᛈᚱ-ᛄᛡᚪᛏ-ᚫᚦ-ᚠᛠᚢ/
ᛈᚣᚫᛝ-ᚣᚾᚻᛡ-ᚳᛗᚠᚾ-ᛞᛄ-ᛖᚩ-ᛒᚷᚻᚪ-ᛖᛞ/
ᛟᚠᛇᛞᛟ-ᛈᚳᛁᚪᛒᚷᛒᛈᛟ-ᛟᛄᚠᚪᛖ-ᛄᚣᚩᛄ-ᚣ/
-ᚫᛋ-ᚦᛁᚫᛄᚫᛏ-ᛖᛇᚻᛟ-ᚣᚠᚹᛞᚷ.ᛡᚱᛒᚢ-ᛒᛚ/
ᚢ-ᚷᛈᛄᚪ-ᛏᛡ-ᚳᛄᚠᛡᛝᛚᚣᛒ-ᛗᚻ-ᚱᛚᛟᛠᛋ/
ᚦᛝ-ᛏᚳᛟᛉᛁ-ᛄᚱᚳᛖᛏᛄᚷ-ᛡᛈᛏᛉᚩᛁᛄᛟ-ᚷ/
ᚩᚪᚢ-ᚣᛖᚪᛋᛟᛇᚢᚪᛡ-ᛗᚱᛚᚳᚠ-ᛒᛗᛝ-ᚻᛉ-/
ᛠᛄᚫ-ᛉᚪᚷᚻᚣᛏᛖᛝ-ᛉᛉᛗᚾᚫᛋ-ᚱᛗᛞᛋ/
%
ᚳ-ᚦᛚᛟ-ᛝᛇᚢ-ᚻᚩ-ᛏ.ᚢᛁᚦᛄᚾᚠᚱᚦ-ᛋᛟᚷᛠ/
ᛗᚪ-ᛝᛚᚪᛁᛒᛠᚢᛋ-ᚩ-ᛖᛋᛝ-ᚠᛡᚢᛟᛞᛇᚪ-ᛞ/
ᛡᛒᚹᚩ-ᛄᛋ-ᛟᛝᛏᚳ-ᚻᚾᛇᛋ-ᛗᛚᚻᛞᛖᛈ-ᚫᛄᚱ/
ᚪᚢᚻᚱᚦᚱ-ᛟᛄ-ᛟᛗᚩᛟᛏ-ᚫᛇ-ᛉᛒᚳ-ᛄᛁ-ᚪᚩᛉ-/
ᚹᚪᚾᛈᛏᚢᚣ-ᛁᛒᚢ.ᚦᚩᛡ-ᛗᚳᚠᛉᚱᛁ-ᚪᛗᛏᛒ-/
ᛗᛚᛁᚦᛏᛠᛋᚾᚷᛚ-ᛏ-ᛇᛈ-ᚩᛚᛞ-ᛚᚹᚳᛄᚹᛉ-ᚪ/
ᛡᚹᛇ-ᛖᛖᚹ-ᛏᚪ-ᚣᚠᛉᚳ-ᛗᚩᚷᛞᚷ-ᛚᚳ-ᛒᚣᛋ/
ᚣᚠᛞᚣᛝ-ᛠᛇᛏᚩᚢᚫ-ᛟᛁᛒ-ᛏᚾᚫᚠ.ᛄᛟᛗᚾ/
ᛈ-ᛠᛡᚩᛏᛡᚪᚱᛞ-ᚪᛝᛈᚹᛗᛄᛟᛠᚩ-ᛚᚹᛉ-/
ᚱᛗ-ᚩᛏᚹᛄᚹᚾ-ᚷᚳᛠ-ᛄᚳᚢᚱ-ᛟᛇᛟᚾᚻᚫᛉ-/
ᚣᛚᚩ-ᚩᛡᚳᚻᛄ-ᛋᚣᚹᛁ-ᚣᚠᛋᚾᚪ-ᚷᛖᚾᛄᚪᚹᛠ-/
ᛞᚠᛟ-ᚢᛁ-ᛖᛇᚦ-ᚫᛞ-ᚳᛄ-ᚷᚢᚻᚣᚻᛁᛒᛉᚾ-ᚹᛝ/
%
ᚻᛏᛉᚫᛁᛄᚢ-ᛞᚠᛡᚫ-ᛋᛁᚹᛝᛈ-ᛗᛉᛄᛈ-ᛞᛗ/
ᛝ-ᛇᛚᛞᚣ-ᚠᚩᛞ-ᛝᚷᚾᛇ-ᚷᛖ-ᛚᛉᚣ-ᚫᛚᛖᛉ./
ᛡᛝᛋ-ᚳᛁᚦ-ᚷᛏᚣ-ᚹᚩ-ᛝᛖ-ᛒᚪᛗᛏᚪᚷᛒ.ᛈᛡ/
ᛟ-ᚪᛉᛝᛒᛞᛉᛄᚦᚢ-ᛏᛇᛖ-ᚣᚪᚳ-ᛠᚦᚹ-ᛏᛉ/
ᚩᚳᛞᛒ-ᛟᚩᛠᚾᚠᚪ.ᛚᛗᛖᛁᚦᚫᚪᛡᛄᛁᚪᚱ-ᚦᚱᛖ/
ᛖᚣᛋᚾ-ᛖᛏᚢᚻᛈᚳᚦᛋ-ᚳᛇᛉᛖᛇᚠ-ᛞᛠᛏ/
ᛈ-ᚣᛇᛠᚢᛏ-ᛉᚦᚷᚻ-ᚫᚾᛠᚱ-ᛡᛒᛏᛁᛉ-ᚩᚢ/
ᛝ-ᛚᛒᛇᚩ-ᛟᛉ-ᚦᛞᚷᚠ-ᚩᚱᛈᚪᛏ-ᚫᛋᚪᚦ-ᛖᛟᚪᛝ/
ᚫ-ᚣᛒᛚ-ᛡᚦᚾᚠᛈᛟᛡᚾ-ᛖᚹ-ᛖᛗᚩ-ᛉᚹᚦᛠ-ᛁᚦ/
ᛒᛖᚱ-ᛟᚳᛉ-ᛈᛖ-ᛁᚢᚦ-ᛈᚠᛞᛈᛄ-ᛁᛟᚻ-ᛒᚦᛏᚩ/
ᚳᚢᛚ-ᛞᛄᛝ-ᚦᛄᛁᚪ-ᚹᚣ-ᚢᛝᚾ-ᛋᚾᛈᚠᚫᛒᛄᚫ-ᛡ/
ᛗᚹ-ᛇᚪᚩᚾᛄᚳᛚᛒᛉ-ᚣᛠᚦᚹ-ᛝᛚᛗᚳᛡᛇᚠᚫ/
%
ᛠᛁᚦ-ᛒᛠᛚᚦᚳᛞᛁᛇ-ᚠᚢᛉᛋᛉᛁᚦᚫᛋᛗ-ᚦᚹ./
ᛈ-ᛒᛋᛏᚫᚾᚱᛁ-ᚦᛇᛡᚱᛚᛡᚹ-ᚢᚩᛋᚱ-ᚹᚫ-ᛒᚹᛡᛖ/
ᛟᛄ-ᛡᚣᛖᚩᛖᛡᚷᚫᚠᚾᚹ-ᛟᛏᚫᚠᛄᚹᛠ.ᚦᛞ-ᛁ/
ᚫᚩᚾ-ᛋᚷᛈᚪᛖᚩ-ᚣᚦᚹ-ᚾᚷ.ᛠᛋᚩᛇᛏ-ᛝᛚᚷᛞ/
-ᛒᛈᛈ-ᛗᛁᚪᛖ-ᛚᛏᛁ-ᚫᛄᛖ-ᛒᚾᚠᚪᛋᚷᛒᚠ-ᚫᚹᚣᚷ/
ᚢᛡᚠᛠ-ᛖᛋᛞ-ᛚᚳᛒᛞᛏᛈ-ᛖᚾᛈᚣ-ᚱᚠᚻ-ᚫ/
ᛝ-ᛟᚪᛗ-ᛒ-ᛡᛚ-ᛝᛋᚱᚢᚹᚱᚣᚻᚹ-ᚹᛡᛈ-ᛁᚻᚾᚻᚱ/
-ᚳᛖᛏᚫᚩᛋ-ᚣᛋ.ᛝᚫᛡᛝᚫ-ᚻᚦ-ᛇᚪᛞᛋ-ᛒᛁᚳᛈ/
-ᛇᛒᛟᚫ-ᛠᛝᛖ-ᛝᛠᚣ-ᛒᚣᛉᚻᚢᚠᚦᛞᚹ-ᛗ/
ᚢᛁᛡᛄᚩ-ᛋᛇᚫᛇᛝᚱ-ᛚᛇᛠ-ᛏᚩᛄ-ᚩᛝᛈ-ᚱᚻ/
ᛠᚢᛉᚦ-ᚣᚢᛋ-ᛡᛚᛖᚷᛗᛝᚹᚻᚱᛋ-ᚢᛟᚣᛠ/
ᚷᚩᚷ-ᛇᛁᛖ-ᛠᛄᛇᛁᚾᛄᚩᛗᚱᛡᛉ-ᚠᚻᚳ-ᚪᚩᚪᚫ/
%
ᚻᚳᛁᚦ-ᛄᚷ.ᛝᛖᚢ-ᛡᛏᛁ-ᛚᚩᚱᛈ.ᚠᚪ-ᛈᛞᚱᛒ-/
ᛝᛁᛋ-ᚷ-ᚠᚾᛈᚠᛒ-ᛟᚦᛁᛠᚪ-ᛡᛏᚾᚳ.ᚦᛟᚻᛈᛖᛚ/
ᚫ-ᛟᚠᛗ-ᛡᛝ.ᛒᛝᚦᛝᛠᚠ-ᛇᛗᛟ-ᚩᛠᛈ-ᛁᛡᚱ/
-ᚹᚹᛟᚩᛒᚩ-ᚾᚩᛄᛟᚾ-ᚦᛡᚠ-ᚩᛄᛞᚦᛏᛁ-ᛈᚾᚪᚱᛄ-/
ᛉᚱᚣ-ᛝᛡ-ᛏᛗ-ᛈᛞᚣᚻ-ᛗᛝᚫᚳᛇ.ᛡᚣᛄᛟ/
-ᛝᚩᚢᛇᛁᚱ-ᛏᚪ-ᚩᚻᚪᛚᚫᛚᚪ-ᛋᛈ-ᛏᚪᛄᚳᚦᚢᛏᚹ/
ᚦ-ᛗᚷᛖᛗᚣᛡᛁᛞ-ᚢᛋᚠᛒ-ᛟᛚᛟ-ᚪᛒ-ᚦᛚᚣ-ᚳ/
ᛠᚣ-ᛞᛇᛁ.ᚹᛉ-ᛟᛝᛒᚢᛋᛞᚻᛞ-ᚢ-ᛠᚱ-ᚫᚩ/
ᚻᛝᛒᚪᚹ-ᛈᛡᚾᛚᛇ-ᛖᛟᛝ-ᛡᚠᛇᛡ-ᚳᚦᚹ.ᛚᚦᚪᛁ/
ᛈ-ᛞᛟᛄ-ᚢᛉᚢᚾᛠᚠ-ᚩᚾᚪ-ᚱᛠᚷ-ᛗᚢ-ᛗᛁᛄ/
ᛒᛗᚱᚾᛗ-ᚩᚾᚠᚣ-ᛗᚠᛇᚠᛄ-ᛒᛡᛈᛄᛖᛡᛏ-ᛈᛟ/
ᚫᛏᛟ-ᚻᛖᚾ-ᚳᛇᚩ-ᛋᚻᚫᛇ-ᛝᛁᛟ-ᛇᚠᚢᛞᚣᚪᛚᚠ/
%
ᛡ-ᛖᛄ-ᚠᛚᛟ-ᛁᚳ-ᛁᛝᚷᚦ-ᛗᛋᚫᚷᚪᛠ-ᛗᛁ-ᛒᛡᛏ/
ᚾ-ᛝᛗᚦ-ᛏᚣᚫᛄ-ᛖᚻᚠᚪᛡᚷ-ᚪᛗᛁ-ᛞᛉᛏ-ᚢᛖ/
ᚦᚾ-ᛖᚪᛈᚹᛠᛚ-ᛒᚢᚱᛡᛟ-ᚪᚣ-ᛟᛇᚹᛄᛈᛞ./
&
3N  3p  2l  36  1b  3v  26  33/
1W  49  2a  3g  47  04  33  3W/
21  3M  0F  0X  1g  2H  0x  1R/
1n  3I  2r  0P  2U  16  2L  2D/
1t  1s  3H  0d  0s  1K  2D  05/
1K  1O  0S  1D  3o  1L  3J  1G/
4D  0G  0L  0x  1Q  2p  2a  1K/
4E  1w  2Q  19  1k  3G  24  0p/
22  4F  0P  3C  3J  1D  2n  1m/
2i  1J  3P  2v  1s  2O  0k  1M/
%
2M  0w  3L  3D  2r  0S  1p  15/
3V  3e  3I  0n  3u  1O  0u  0Z/
3g  2U  1C  0Y  1N  3n  0W  3Q/
22  13  0V  3c  0E  34  0W  1t/
1D  2N  3H  47  0s  2p  0Z  34/
0g  3v  1Q  0s  0D  0K  2h  3D/
3L  2x  1Q  20  2n  2L  1C  2p/
0A  29  3r  0D  45  0k  2e  2W/
25  3U  1W  2r  46  2s  2X  39/
3p  0X  0E  1q  0q  4B  49  48/
3r  3b  3C  1M  1j  0l  4A  48/
40  3m  4E  0s  2s  1v  3T  0I/
3t  2B  2k  2t  2O  0e  2l  1L/
%
28  2a  0J  1L  0c  3C  2o  0X/
00  2Z  2d  1T  2u  1t  1j  0l/
1o  1E  3T  18  3E  1G  27  0L/
0v  2t  06  11  1A  2U  4B  1O/
2M  3d  2S  0x  0w  0q  0p  2V/
18  0q  1D  49  2O  00  1v  2t/
1k  3s  3G  21  3w  0W  29  2r/
2O  2L  0g  3Y  0M  0u  3i  3C/
1r  2c  2q  3o  30  0a  39  1K/
&
ᚹᚹᛈ-ᚠᛡᛚᛉᛒᚾ-ᚳᛗᚾᚱᛗ-ᚻᚦᚫᛞᛄ-ᛒᛡᚫ-ᛇᚹ/
ᛗᚢ-ᚪᛈᛡ-ᛈᛁᛄ-ᚪᚢᚾᛠᛖᛞᛗᚪ-ᛏᛟᛗ-ᛋᛞ/
ᛝᚷᛚᛋᛞᛝ-ᛟ-ᛋᛄᛞ-ᛚᛟᚠᛄᚫᚠᚪ-ᛝᛟᚣᛈ-ᚣᚩ/
ᛒᚷᚳᛖᛏᚹ-ᚪᛋᛒ-ᛗᛠᚣᛇᛗᚫᛚᚱ-ᚹᛇᛄᛒ-ᛈᛚᚠ/
%
ᛈ-ᚠᛗ-ᛝᚪᛇᚾᛟᚹᛇᛉ-ᚣᚫᛉᛞᛟᚱᛒ-ᛡᚱᛟ-ᚹᛏ/
ᚷᚱᛄᛖ-ᛠ-ᛈᛚᛞ-ᚻᚦᚱ-ᚦᚣᛚᛉ-ᛠᛈᚫᚠᚪ-ᚫᚪ/
ᛒ-ᛈᛋ-ᛗ-ᛏᚫᚳᛈᛝᚹᚦ-ᚻᛠ-ᛞᚩᛄᚷ-ᛋᚩᛠᚳ/
ᛖᛋ-ᚣᛖᚫ-ᛈᚦ-ᛁᛇᛈᚳᛝ.ᛈᚳᛇᚢᛏᚳᛡᛇᛝᚾ/
ᚢᚻᚦ-ᚣᚠᛗᚾ-ᛝᚠᛄᛉᛟᚱᛗ-ᛝᛠᛄᛏᚳ-ᚢᚷ/
ᚦ-ᚠᚦᛋ-ᚪᛈᚩᚪᚫᛞᛋᛝ-ᛒᛗᚩᚷ-ᚹᚠᛗᛖ-ᛠᛇᚻᚠ/
ᚻᚳᚱᚫ-ᛝᛗᛉᚳ-ᛋᚪᚹᛋᛠ-ᚩᚣᛚᛉᛝ-ᛠᛟᛉ/
ᛟᛠᛡᛝᛒ-ᛝᚳᚫᛁᚱ.ᛒᚠ-ᛏᚣᚣ-ᛠᛒ-ᚣᛚᚩ-ᛇ/
ᛉ-ᚩᚷᛗᚩ-ᚠᛚᛟᛝᚦᛠ-ᚦᚣᛖᚣ-ᚾᚷᚾ.ᛡᛏ-ᛄ/
ᛟᚾᛁ-ᛋᛟ-ᛠᚦᚣ-ᛋᛒ-ᚫᛚᚪᛄᛡᛖᚷᛉᛡᚾᛉᛏ-/
ᛡᛒᚻᛚᚷ-ᚢᚦᛠ-ᚢᚾᛁᚩᛗᛠᛁᚷ-ᛟᚦᚱᚣ-ᛒᛖ/
ᛠᚩᛈ-ᛗᛏᚱᚫᚢᚻᛁᛝ-ᛇᚳᚠ-ᛄᚾᚱᚷ-ᛟᚷᚻᚣᚻ/
%
ᛇᚫᛠᚫᚣ-ᚢᛗᛈ-ᛉᛁᚢᚾᚩᛟᚾ-ᚷᛞᚦ-ᛡᚫᚹ-ᛞ/
ᛟᛖᚱ-ᛗᚾᛖᚻᚷᛒᚢᛄ-ᚢᚦᛗᛖᛞᛝ-ᛒᚷᚣᚱ-ᛖ/
ᛁᚢᛄ-ᚣᛡᛚᚢ-ᛄᛟ.ᛠᛉᚣᛇᚱ-ᚩᛈᛋᚳᚫᛗ/
ᛇ-ᚾᛄ-ᛖᚠᛋ-ᛖᚠᚪᛝ-ᚢᛝᛄᛇᚷᚠᛝᚱᛁᚦ-ᛄᚢᚫ-/
ᚣᛋᚠᛖᚢᛋᚫᚣᛠ-ᛁᛏᛟᚱᛏᛟᚩ-ᚷᚾᚻ-ᛞᛗᚩᚳ/
ᛞᛖᛏ-ᚹᛉᛞᛚ-ᚩᚫᛄ-ᛇᚢᛒ-ᛗᛏ-ᛞᛗᛖ.ᛏ/
ᛈᚹᛇᛋ-ᚹᛒᛇᚦ-ᚾᚻᚷᛄ-ᚱᛡᛞᛡᚦᚪᛁᛇᚫᛉᛚ-ᛇ/
ᛠ-ᛡᚪᛄ-ᚻᚱ-ᚦᛈᛞᛄᛝᚩ-ᚷᚠᛇᛗᚳ-ᚻᛞᚩᛏᚳ/
-ᚢᚱ-ᛈᚾ./
&
%
ᚪ-ᛗᛝᛞᛡᚦᛉᛁᛗ.ᛡᛞᛈᛝᚢᚹᚪᛗ-ᛏᚪ/
ᛝ-ᛝᚦᛡᚹᛋᚻ-ᛁᚳ-ᚫᛈᚫᚷᚩ-ᛗᛁᚪ-ᛖᚩ-ᛏᚹ/
ᚩ-ᚠᚣᚢᛏᛄ-ᚦᛄᛠᛖᚳᚾᛠ-ᚳᛠᛖ-ᚱ/
ᚩᚢᛉ-ᛞᚹᚻᛒᛝᚠᚪᚳᛄᚢ-ᚩᛄᛡᛠᛁᛚᚷᚻ-ᛒᚢ/
ᛄ-ᛉᚪᚳᚹᛡ-ᛗᚩᛈᚣᛞᛡᛚᛈ-ᛇᛁᚦᚱ-ᚣᚷᛗ-ᛉ/
ᛟᚷᛋ-ᛗᛈᛄᛟᛞ-ᛟᛏᛡᛟ-ᛏᛝᛁ-ᛗᛝᚣᚪᚫ-ᛝ-ᚱ/
ᚣᛄ-ᚾᛚᚢᛉᛒ-ᚻᛈᛄᚩᛠ-ᚷᚫᚹ-ᛉᛋᛞᚳ-ᚢᛏ-/
ᛟᚻᛇᚾᛈᛏ-ᛠᚣᛒᚢᚷ-ᚷᚪᛇ-ᚾᚷᚩᛖᛚᛗᛒᚦ-ᚣ/
ᛡᛟᛇᚣ-ᛗᚳᛟᚦ-ᛖᛚᚱᛇᛈᚱᛞᚣ-ᛉᛞ-ᛝᚣᛈ-/
ᛋᛖᛉᚹ-ᚳᚷᚠᛞᚱᛖ-ᛞᛖᚹᚩᛇᛟ-ᚻᚩᛟ-ᛒᛋ-ᚻ/
ᛠᚪᚳᛁᛗᛉᛄᛗᛖ-ᛗᛚ-ᚷᚩᛏᚦᛉᛖᛠᚱᚷᚣ/
%
ᛝ-ᚫᛗᛁᚹ-ᛋᛒ-ᛉᛗ-ᛋᛇᚷᛞᚦᚫ-ᚠᛡᚪᛒᚳᚢ-ᚹᚱ-ᛒ/
ᛠᚠᛉᛁᛗᚢᚳᛈᚻᛝᛚᛇ-ᛗᛋᛞᛡᛈᚠ-ᛒᚻᛇᚳ-/
ᛇᛖ-ᛠᛖᛁᚷᛉᚷᛋ-ᛖᛋᛇᚦᚦᛖᛋ-ᚦᛟ-ᚳᛠᛁᛗ/
ᚳᛉ-ᛞᛄᚢ-ᛒᛖᛁ
'''

import os

page_index = -1
for c in cipher.split('%'):
    page_index += 1
    print(f'PAGE {page_index}\n\n')
    print(Cicada.runes_to_latin(c, totient_substruction=True))
    Cicada.press_enter() 



'''
key = ''
while len(key) < len(expected):
    min_rune = None
    min_len = 1337
    for rune in Cicada.RUNES:
        v = Cicada.vigenere_decrypt(given, key + rune)
        if not v[len(key)] == expected[len(key)]:
            continue
        if min_len > len(v):
            min_len = len(v)
            min_rune = rune
    if min_rune is None:
        raise Exception('fuck')
    key += min_rune
    print(f'{key} --> minLen = {min_len}')


xxx = cipher.strip().split('/')[0].split('-')
import pdb; pdb.set_trace()
print(len('ᚣᚾ-ᚢᚹᛝ'))
'''
