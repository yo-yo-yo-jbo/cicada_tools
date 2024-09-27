#!/usr/bin/env python3
from core import *
from squares import *
from transformers import *
from liber_primus import LiberPrimus
import screen

import subprocess
import platform
import os

class ResearchUtils(object):
    """
        Research utlities.
    """

    # Cache for English words as runes
    _ENGLISH_WORDS = None

    # Cache for unsolved sections
    _UNSOLVED_SECTIONS = None

    @classmethod
    def get_unsolved_sections(cls):
        """
            Gets all unsolved sections.
        """

        # Work on cache
        if cls._UNSOLVED_SECTIONS is None:

            # Try to decrypt all sections
            cls._UNSOVLED_SECTIONS = []
            for section in LiberPrimus.get_all_sections():

                # Process all text
                processed_text = ProcessedText(section.get_all_text())
                for transformer in section.transformers:
                    transformer.transform(processed_text)

                # Add to result if section is unsolved
                if processed_text.is_unsolved():
                    cls._UNSOVLED_SECTIONS.append(section)

        # Return all unsolved sections
        return cls._UNSOVLED_SECTIONS

    @classmethod
    def get_rune_english_dictionary(cls):
        """
            Gets runes from an English dictionary.
        """

        # Build cache
        if cls._ENGLISH_WORDS is None:
            cls._ENGLISH_WORDS = set() 
            with open('english_wordlist.txt', 'r') as fp:
                for word in fp.read().split('\n'):
                    runic = RuneUtils.english_to_runes(word)
                    if len(runic) > 0:
                        cls._ENGLISH_WORDS.add(runic)
        
        # Use cache
        return cls._ENGLISH_WORDS

    @classmethod
    def get_rune_wordlist(cls, use_dictionary=False):
        """
            Get a Runic wordlist from all solved sections dynamically.
            Can also extend to an English wordlist.
        """

        # Try to decrypt all sections
        result = set()
        for section in LiberPrimus.get_all_sections():

            # Process all text
            processed_text = ProcessedText(section.get_all_text())
            for transformer in section.transformers:
                transformer.transform(processed_text)

            # Skip unsolved sections 
            if processed_text.is_unsolved():
                continue

            # Get all words
            for word in processed_text.get_rune_words():
                if len(word) == 0:
                    continue
                result.add(word)

        # Optionally extend to use a wordlist
        if use_dictionary:

           # Use cache
            result = set.union(result, cls.get_rune_english_dictionary())

        # Return wordlist sorted by word length descending
        return sorted(result, key=len)[::-1]

    @staticmethod
    def print_section_data(section, processed_text=None):
        """
            Unified way of printing a section data.
        """

        # Present section contents
        print(f'Section: {section.name}', end='')
        if len(section.title) > 0:
            print(f' ("{section.title}")')
        else:
            print('')
        if processed_text is not None:
            print(f'Runic IoC (post): {processed_text.get_rune_ioc()}\nLatin IoC: {processed_text.get_latin_ioc()}\nRune count: {len(processed_text.get_runes())}\n\n')
            screen.print_solved_text(f'{processed_text.to_latin()}\n\n{section.get_all_text()}\n\n\n')

        # Show page numbers if available
        page_numbers_string = ', '.join([ str(number) for number in section.get_page_numbers() ])
        if len(page_numbers_string) > 0:
            print(f'\nnPages: {page_numbers_string}')

    @staticmethod
    def launch_path(path):
        """
            Launches the given path.
        """

        # Act differently based on platform
        if platform.system() == 'Darwin':
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':
            os.startfile(path)
        else:
            subprocess.call(('xdg-open', path))

    @staticmethod
    def iterate_potential_interrupter_indices(processed_text, interrupter_rune='ᚠ'):
        """
            Iterates all the potential interrupter indices.
        """

        # Finds all potential indices
        runes = processed_text.get_runes()
        potential_interrupters = [ i for i in range(len(runes)) if runes[i] == interrupter_rune ]

        # Iterate
        for mask in range(2**len(potential_interrupters)):
            yield [ potential_interrupters[i] for i in range(len(potential_interrupters)) if (mask & (1<<i)) > 0 ]

