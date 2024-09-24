#!/usr/bin/env python3
from core import *
from squares import *
from secrets import *
from transformers import *
from liber_primus import LiberPrimus

import subprocess
import platform
import os
import itertools
import sys
from tqdm import tqdm
import string
import screen
import requests
import tempfile
import gzip
import shutil
import sympy

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

            # Build cache
            if cls._ENGLISH_WORDS is None:
                cls._ENGLISH_WORDS = set() 
                with open('english_wordlist.txt', 'r') as fp:
                    for word in fp.read().split('\n'):
                        runic = RuneUtils.english_to_runes(word)
                        if len(runic) > 0:
                            cls._ENGLISH_WORDS.add(runic)
            
            # Use cache
            result = set.union(result, cls._ENGLISH_WORDS)

        # Return wordlist sorted by word length descending
        return sorted(result, key=len)[::-1]

    @staticmethod
    def print_section_data(section, processed_text=None):
        """
            Unified way of printing a section data.
        """

        # Present section contents
        print(f'Section: {section.name} ("{section.title}")')
        if processed_text is not None:
            print(f'Runic IoC (post): {processed_text.get_rune_ioc()}\nLatin IoC: {processed_text.get_latin_ioc()}\nRune count: {len(processed_text.get_runes())}\n\n')
            screen.print_solved_text(f'{processed_text.to_latin()}\n\n{section.get_all_text()}\n\n\n')

        # Show page numbers if available
        page_numbers_string = ', '.join([ str(number) for number in section.get_page_numbers() ])
        if len(page_numbers_string) > 0:
            print(f'\n\nPages: {page_numbers_string}')

    @staticmethod
    def open_path(path):
        """
            Opens the path.
        """

        # Act differently based on platform
        if platform.system() == 'Darwin':
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':
            os.startfile(path)
        else:
            subprocess.call(('xdg-open', path))

class Attempts(object):
    """
        Attempts made.
    """

    @staticmethod
    def show_all_sections(only_solved=False):
        """
            Presents all sections.
        """

        # Decrypt all sections
        for section in LiberPrimus.get_all_sections():

            # Build the processed text
            processed_text = ProcessedText(section.get_all_text())

            # Get the rune IoC
            rune_ioc = processed_text.get_rune_ioc()

            # Decrypt
            for transformer in section.transformers:
                transformer.transform(processed_text)

            # Optionally skip unsolved
            if only_solved and processed_text.is_unsolved():
                continue

            # Present section contents
            ResearchUtils.print_section_data(section, processed_text)

            # Show GP sums of solved sections
            if not processed_text.is_unsolved():
                gp_sum_string = ', '.join([ str(RuneUtils.runes_to_gp_sum(word)) for word in processed_text.get_rune_words() ])
                print(f'\n\nGP-sums: {gp_sum_string}\n')

            # Wait for further input if filename is available
            image_paths = [ page.filepath for page in section.pages if page.filepath is not None ]
            if len(image_paths) > 0:

                # Ask for input and present if thus selected
                print('Show images? [', end='')
                screen.print_yellow('Y', end='')
                print('/', end='')
                screen.print_yellow('N', end='')
                print(']? (default=', end='')
                screen.print_yellow('N', end='')
                choice = input(')? ')
                if choice.strip().upper() == 'Y':
                    for image_path in image_paths:
                        ResearchUtils.open_path(image_path)
                    screen.press_enter()
                else:
                    screen.clear()
            else:
                screen.press_enter()

    @staticmethod
    def show_all_solved_words():
        """
            Presents all solved words.
        """

        # Get words and show them
        words = ResearchUtils.get_rune_wordlist()
        word_index = 0
        for word in words:
            word_index += 1
            screen.print_solved_text(f'[{word_index} / {len(words)}]: {len(word)}\t\t{word}\t\t{RuneUtils.runes_to_latin(word)}')
            screen.press_enter()

    @staticmethod
    def show_unsolved_sections_potential_cribs_lengths():
        """
            Shows each unsolved sections with potential crib lengths at the beginning of the section.
        """

        # Iterate all unsolved sections
        for section in ResearchUtils.get_unsolved_sections():

            # Get all words until a period
            header_words = ProcessedText(section.get_all_text().split('.')[0]).get_rune_words()
            if len(header_words) == 0:
                continue
            header_words_lengths = [ len(w) for w in header_words ]

            # Show section information
            ResearchUtils.print_section_data(section, None)

            # Present the header words lengths
            print('Potential crib lengths: ', end='')
            screen.print_solved_text(f'{header_words_lengths}\n\n{section.get_all_text()}')
            screen.press_enter()

    @staticmethod
    def double_tot_index_with_reversing(word_threshold=6, ioc_threshold=1.8):
        """
            Adds or substructs either tot(primes) or tot(tot(primes)), on both normal text as well as reversed text.
            If the number of prefixed words are above the given threshold or the IOC is above the given threshold, print result.
        """

        # Get an extended wordlist for a measurement
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Iterate all sections
        for section in tqdm(ResearchUtils.get_unsolved_sections(), desc='Sections being analyzed'):

            # Iterate all number of totient operations
            for tot_call_count in range(1, 3):
               
                # Try adding or substructing
                for add_option in (False, True):

                    # Try reversing and then run totient index manipulation
                    pt = ProcessedText(section.get_all_text())
                    ReverseTransformer().transform(pt)
                    TotientPrimeTransformer(tot_calls=tot_call_count, add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        ResearchUtils.print_section_data(section, processed_text)

                    # Try without reversing
                    pt = ProcessedText(section.get_all_text())
                    TotientPrimeTransformer(tot_calls=tot_call_count, add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        ResearchUtils.print_section_data(section, processed_text)

                    # Reverse after totient index manipulation
                    ReverseTransformer().transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        ResearchUtils.print_section_data(section, processed_text)

    @staticmethod
    def use_2013_missing_primes(word_threshold=6, ioc_threshold=1.8):
        """
            Attempts to use the Cicada 3301 message missing primes from 2013 as a keystream.
        """

        # Get an extended wordlist for a measurement
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Iterate all sections 
        for section in tqdm(ResearchUtils.get_unsolved_sections()):

            # Whether to add or substruct
            for add in (False, True):

                # Try decryption
                pt = ProcessedText(section.get_all_text())
                KeystreamTransformer(add=add, keystream=iter(MISSING_PRIMES_2013)).transform(pt)
                if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                    ResearchUtils.print_section_data(section, pt)

    @staticmethod
    def autokey_and_vigenere_bruteforce_with_reversing(word_threshold=6, ioc_threshold=1.8, min_key_len=6):
        """
            Attempts Autokey or Vigenere bruteforcing with or without reversing the text of each section.
            Uses keys derived from all decrypted sections, with and without replacing all occurrences of first character with "F".
            Also tries reversing all keys.
            Uses all supported modes of Autokey: plaintext, cipehrtext or alternating (starting from either plaintext or ciphertext, or using the Mobius function).
        """

        # Get an extended wordlist for a measurement
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Build potential keys
        keys = ResearchUtils.get_rune_wordlist()
        rev_keys = [ k[::-1] for k in keys ]
        keys += [ k.replace(k[0], RuneUtils.rune_at(0)) for k in keys ]
        keys += rev_keys
        keys = [ k for k in keys if len(k) > min_key_len ]
        keys = set(keys)

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all keys
            for key in tqdm(keys, desc=f'Section {section.name}'):
              
                # Attempt Vigenere
                pt = ProcessedText(section.get_all_text())
                VigenereTransformer(key=key).transform(pt)
                if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                    print(f'Vigenere Key="{key}"')
                    ResearchUtils.print_section_data(section, pt)

                # Iterate all modes
                for mode in (AutokeyMode.PLAINTEXT, AutokeyMode.CIPHERTEXT, AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT, AutokeyMode.ALT_MOBIUS_START_PLAINTEXT, AutokeyMode.ALT_MOBIUS_START_CIPHERTEXT):

                    # Either try or do not try GP-mode
                    for use_gp in (False, True):

                        # Apply Autokey
                        pt = ProcessedText(section.get_all_text())
                        AutokeyTransformer(key=key, mode=mode, use_gp=use_gp).transform(pt)
                        if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                            print(f'Autokey key="{key}" mode={mode}')
                            ResearchUtils.print_section_data(section, pt)

                        # Reverse
                        ReverseTransformer().transform(pt)
                        if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                            print(f'Autokey key="{key}" mode={mode} and then reversing')
                            ResearchUtils.print_section_data(section, pt)

                        # Start from reversing and then apply Autokey
                        pt = ProcessedText(section.get_all_text())
                        ReverseTransformer().transform(pt)
                        AutokeyTransformer(key=key, mode=mode, use_gp=use_gp).transform(pt)
                        if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                            print(f'Autokey key="{key}" mode={mode} on reversed text')
                            ResearchUtils.print_section_data(section, pt)

    @staticmethod
    def oeis_keystream(word_threshold=6, ioc_threshold=1.8):
        """
            Tries all OEIS sequences on each section, using them as keystreams.
        """

        # Get an extended wordlist for a measurement
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Check if download is necessary
        oeis_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oeis.txt')
        if not os.path.isfile(oeis_filepath):

            # Download stripped temporary file
            temp_dir = tempfile.mkdtemp()
            gz_filepath = os.path.join(temp_dir, 'oeis.gz')
            response = requests.get('https://oeis.org/stripped.gz', stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading OEIS') as progress_bar:
                with open(gz_filepath, 'wb') as fp:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        fp.write(data)

            # Extract contents
            oeis_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'oeis.txt')
            with gzip.open(gz_filepath, 'rb') as f_in:
                with open(oeis_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Best-effort deletion
            try:
                os.unlink(gz_filepath)
            except Exception:
                pass

        # Parse OEIS
        sequences = {}
        with open(oeis_filepath, 'r') as fp:
            for line in fp.readlines():
                stripped_line = line.strip()
                if len(stripped_line) == 0 or stripped_line[0] == '#':
                    continue
                chunks = [ elem for elem in stripped_line.split(',') if len(elem) > 0 ]
                if len(chunks) < 2:
                    continue
                sequences[chunks[0].strip()] = [ int(elem.strip()) for elem in chunks[1:] ]
        
        # Try all sequences
        for seq in tqdm(sequences):
            
            # Iterate all sections 
            for section in ResearchUtils.get_unsolved_sections():

                # Try adding or substructing
                for add_option in (False, True):

                    # Try sequence as-is
                    pt = ProcessedText(section.get_all_text())
                    KeystreamTransformer(keystream=iter(sequences[seq]), add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'OEIS sequence {seq}')
                        ResearchUtils.print_section_data(section, pt)

                    # Try a special function on the sequence which comes from the Cicada page 15 spiral
                    pt = ProcessedText(section.get_all_text())
                    func_seq = [ abs(3301 - elem) for elem in sequences[seq] ]
                    KeystreamTransformer(keystream=iter(func_seq), add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'OEIS sequence {seq} after abs(3301-x) on it')
                        ResearchUtils.print_section_data(section, pt)

    @staticmethod
    def page15_function_keystream():
        """
            Uses abs(3301-p) on all primes p as a keystream, as well as Fibonacci-indexed primes and other variants.
            This function was concluded from the Page 15 square matrix.
        """

        # Iterate all sections 
        for section in ResearchUtils.get_unsolved_sections():

            # Try adding or substructing
            for add_option in (False, True):

                # Try on primes 
                pt = ProcessedText(section.get_all_text())
                Page15FuncPrimesTransformer(add=add_option).transform(pt)
                print(f'Func15(primes) transformation (add={add_option}):')
                ResearchUtils.print_section_data(section, pt)
                screen.press_enter()

                # Try on Fibonacci-indexed primes
                pt = ProcessedText(section.get_all_text())
                Page15FiboPrimesTransformer(add=add_option).transform(pt)
                print(f'Func15(fibo-primes) transformation (add={add_option}):')
                ResearchUtils.print_section_data(section, pt)
                screen.press_enter()

                # Try the Totient of the Fibonacci-indexed primes
                pt = ProcessedText(section.get_all_text())
                KeystreamTransformer(add=add_option, keystream=map(lambda x:sympy.totient(x), MathUtils.get_fibo_primes())).transform(pt)
                print(f'Totient(fibo-primes) transformation (add={add_option}):')
                ResearchUtils.print_section_data(section, pt)
                screen.press_enter()

                # Try the Totient of the function from page 15 on Fibonacci indexed primes
                pt = ProcessedText(section.get_all_text())
                KeystreamTransformer(add=add_option, keystream=map(lambda x:abs(3301 - sympy.totient(x)), MathUtils.get_fibo_primes())).transform(pt)
                print(f'Func15(Totient(fibo-primes)) transformation (add={add_option}):')
                ResearchUtils.print_section_data(section, pt)
                screen.press_enter()
              
                # Try on Fibonacci-indexed primes without the page 15 function
                pt = ProcessedText(section.get_all_text())
                FiboPrimesTransformer(add=add_option).transform(pt)
                print(f'Fibo-primes transformation (add={add_option}):')
                ResearchUtils.print_section_data(section, pt)
                screen.press_enter()
 
    @staticmethod
    def spiral_square_keystream():
        """
            Try to use all squares as keystreams while walking in a spiral.
            Spiral pattern was concluded from page 15, walking right and going clockwise.
        """

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all squares
            square_index = -1
            for square in SQUARES:
                
                # Try adding or substructing
                square_index += 1
                for add_option in (False, True):

                    # Use as a keystream
                    pt = ProcessedText(section.get_all_text())
                    SpiralSquareKeystreamTransformer(matrix=square, add=add_option).transform(pt)
                    print(f'Square {square_index} (add={add_option}):')
                    ResearchUtils.print_section_data(section, pt)
                    screen.press_enter()
    
    @staticmethod
    def hill_cipher():
        """
            Tries to perform Hill Cipher with all squares.
        """

        # Build a new square from the sum of first two squares
        squares = SQUARES[:]
        squares.append(squares[0] + squares[1])

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all squares
            square_index = -1
            for square in squares:
                
                # Either inverse or not
                for inverse_option in (False, True):

                    # Use Hill cipher
                    square_index += 1
                    pt = ProcessedText(section.get_all_text())
                    HillCipherTransformer(matrix=square, inverse=inverse_option).transform(pt)
                    print(f'Square {square_index} (inverse={inverse_option}):')
                    ResearchUtils.print_section_data(section, pt)
                    screen.press_enter()

    @staticmethod
    def gp_sum_keystream(word_threshold=6, ioc_threshold=1.8):
        """
            Attempts to use the GP-sum of each solved section words as a keystream.
            Also attempts to use the GP-sums of entire solved LP1 as a keystream.
        """

        # Get an extended wordlist for a measurement
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Build dictionary mapping solved sections to GP-sum based streams
        lp1_keystream = []
        had_unsolved = False
        streams = []
        result = set()
        for section in LiberPrimus.get_all_sections():

            # Process all text
            processed_text = ProcessedText(section.get_all_text())
            for transformer in section.transformers:
                transformer.transform(processed_text)
            
            # Skip unsolved sections
            if processed_text.is_unsolved():
                had_unsolved = True
                continue

            # Get the stream
            stream = [ RuneUtils.runes_to_gp_sum(word) for word in processed_text.get_rune_words() ]
            if len(stream) > 0:
                streams.append(stream)

            # Append stream to the LP1 keystream
            if not had_unsolved:
                lp1_keystream += stream

        # Add LP1 keystream to the front of the streams
        streams.insert(0, lp1_keystream)

        # Iterate all unsolved sections and attempt to use each stream on each section
        for section in tqdm(ResearchUtils.get_unsolved_sections()):

            # Iterate all streams 
            stream_index = -1
            for stream in streams:
                
                # Use a keystream
                stream_index += 1
                for add_option in (False, True):
                    pt = ProcessedText(section.get_all_text())
                    KeystreamTransformer(keystream=iter(stream), add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'Stream {stream_index} (add={add_option}):')
                        ResearchUtils.print_section_data(section, pt)
                        screen.press_enter()

    @staticmethod
    def square_sections_spiral():
        """
            Performs a spiral transformation on sections with numbers of runes that are a square.
        """

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Conclude if the number of runes is a square
            pt = ProcessedText(section.get_all_text())
            runes = pt.get_runes()
            if not MathUtils.is_square(len(runes)):
                continue

            # Treat as a square matrix
            side = MathUtils.sqrt(len(runes))
            matrix = sympy.Matrix([ [ RuneUtils.get_rune_index(rune) for rune in runes[i:i+side] ] for i in range(0, len(runes), side) ])

            # Walk the matrix in a spiral
            pt.set_runes([ RuneUtils.rune_at(index) for index in MathUtils.matrix_to_spiral_stream(matrix) ])
            print(f'Spiral rearrangement on section (size={side}x{side})')
            ResearchUtils.print_section_data(section, pt)
            screen.press_enter()

    @staticmethod
    def primes_11_indices_apart(word_threshold=4, ioc_threshold=1.8):
        """
            Performs a keystream manipulation on runes based on prime numbers that are 11 indices apart.
            This logic was concluded based on Liber Primus 1 (first solved pages) that have the numbers 107, 167, 229.
        """

        # Get an extended wordlist for a measurement
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Iterate all sections
        for section in tqdm(ResearchUtils.get_unsolved_sections()):

            # Start values could be either 107 (naturally from LP1), 13 (lowest prime to start from assuming 107 is in sequence) and 2 (first prime)
            for start_value in (107, 13, 2):
                
                # Either adding or substructing
                for add_option in (False, True):

                    # Use the prime sequence
                    pt = ProcessedText(section.get_all_text())
                    Primes11IndicesApartTransformer(add=add_option, start_value=start_value).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'Primes 11 apart (start_value={start_value}, add={add_option}):')
                        ResearchUtils.print_section_data(section, pt)
                        screen.press_enter()

                    # Try Atbash
                    AtbashTransformer().transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'Primes 11 apart with Atbash (start_value={start_value}, add={add_option}):')
                        ResearchUtils.print_section_data(section, pt)
                        screen.press_enter()

                    # Revert Atbash
                    AtbashTransformer().transform(pt)

                    # Try shifting
                    for shift_value in range(1, RuneUtils.size()):
                        ShiftTransformer(shift=1).transform(pt)
                        if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                            print(f'Primes 11 apart (start_value={start_value}, add={add_option}, shift={shift_value}):')
                            ResearchUtils.print_section_data(section, pt)
                            screen.press_enter()

def research_menu():
    """
        Research menu.
    """

    # Run menu forever
    last_error = None
    finished_run = False
    stopped_by_user = False
    started_run = False
    while True:

        # Clear screen
        screen.clear()
        if last_error is not None:
            screen.print_red(f'{last_error}\n')
            last_error = None
        if finished_run:
            screen.print_green('FINISHED METHOD\n')
            finished_run = False
        if stopped_by_user:
            screen.print_yellow('STOPPED BY USER\n')
            stopped_by_user = False
        started_run = False

        # List all static methods in Attempts
        screen.print_yellow('== METHODS AVAILABLE ==')
        attempts = [ (k, v) for (k, v) in Attempts.__dict__.items() if isinstance(v, staticmethod) ]
        index = 0
        for k, v in attempts:
            index += 1
            nice_title = k.replace('_', ' ').title()
            nice_desc = v.__func__.__doc__.strip().split('\n')[0]
            if len(nice_desc) > 170:
                nice_desc = nice_desc[:170] + '...'
            screen.print_blue(f'{index}.', end=' ')
            print(f'{nice_title}\n\t{nice_desc}')

        # Always give the option of quitting
        print('\nChoose ', end='')
        screen.print_yellow('Q', end='')
        print(' to quit, or ', end='')
        screen.print_yellow('CTRL+C', end='')
        print(' to stop a method mid-execution.\n')

        # Get choice and run it
        try:
            choice = input('Choose the method: ').strip()
            if choice in ('q', 'Q'):
                break
            if choice == '':
                continue
            assert choice.isdigit(), Exception('Invalid choice')
            method_index = int(choice)
            assert method_index > 0 and method_index <= len(attempts), Exception('Invalid choice')
            screen.clear()
            started_run = True
            attempts[method_index - 1][1].__func__()
            started_run = False
            finished_run = True
            print('\n')
            screen.press_enter()
        except KeyboardInterrupt:
            stopped_by_user = started_run
            print('\n')
            try:
                screen.press_enter()
            except KeyboardInterrupt:
                pass
            continue
        except Exception as ex:
            last_error = f'ERROR: {ex}'

if __name__ == '__main__':
    research_menu()
