#!/usr/bin/env python3
from research_utils import ResearchUtils
from core import *
from secrets import *
from transformers import *
from liber_primus import LiberPrimus
from measurements import *
import screen

import os
import itertools
from tqdm import tqdm
import string
import requests
import tempfile
import gzip
import shutil
import sympy
import subprocess

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
            processed_text = ProcessedText(section=section)

            # Calculate the doublets rate
            runes = processed_text.get_runes()
            doublets_count = len([ True for i in range(len(runes) - 1) if runes[i] == runes[i + 1] ])
            doublets_rate = doublets_count / len(runes) if len(runes) > 0 else 0.0

            # Decrypt
            for transformer in section.transformers:
                transformer.transform(processed_text)

            # Optionally skip unsolved
            if only_solved and processed_text.is_unsolved():
                continue

            # Present section contents
            ResearchUtils.print_section_data(section, processed_text)

            # Show the doublets rate
            print(f'\n\nDoublets rate: {doublets_rate} ({doublets_count} / {len(runes)})')

            # Show GP sums of solved sections
            if not processed_text.is_unsolved():
                gp_sum_string = ', '.join([ str(RuneUtils.runes_to_gp_sum(word)) for word in processed_text.get_rune_words() ])
                print(f'GP-sums of runes: {gp_sum_string}\n')
                gp_sum_string = ', '.join([ str(RuneUtils.runes_to_gp_sum(line)) for line in processed_text.split_lines(include_empty_lines=False) ])
                print(f'GP-sums of lines: {gp_sum_string}\n')
            
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
                        ResearchUtils.launch_path(image_path)
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
    def sentence_cribbing(skip_limit=3301, start_val_limit=3301):
        """
            Attempts cribbing the first sentence automatically, assuming a prime-related ascending key.
            Assumes interrupters might occur. Also attempts to use emirps (Decimal-reversal of primes).
        """

        # Get words
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Either reverse or not
        for rev_option in (False, True):

            # Iterate all unsolved sections
            for section in ResearchUtils.get_unsolved_sections():

                # Optionally reverse
                text = section.get_all_text()
                if rev_option:
                    text = text[::-1]

                # Get header words
                header_pt = ProcessedText(rune_text=text.split('.')[0], section=section)
                header_words = header_pt.get_rune_words()
                if len(header_words) == 0:
                    continue

                # Iterate all potential prime keys
                for skip in tqdm(range(1, skip_limit), desc=f'Section {section.name} (rev={rev_option}'):
                    for start_val in range(start_val_limit):
                       
                        # Take interrupters into account
                        for interrupt_indices in ResearchUtils.iterate_potential_interrupter_indices(header_pt):

                            # Build primes key
                            key = []
                            curr = start_val
                            while len(key) < header_pt.get_num_of_runes():
                                key.append(curr)
                                curr = sympy.nextprime(curr)

                            # Check for primes
                            processed_text = ProcessedText(rune_text=' '.join(header_words), section=section)
                            KeystreamTransformer(keystream=iter(key), interrupt_indices=interrupt_indices).transform(processed_text)
                            pt_header_words = processed_text.get_rune_words()
                            if len([ word for word in pt_header_words if word in wordlist ]) == len(pt_header_words):
                                plaintext_latin = RuneUtils.runes_to_latin(' '.join(pt_header_words))
                                print(f'Primes key: {key} with skip {skip} and start value of {start_val} yields {plaintext_latin} (interrupt_indices={interrupt_indices})')

                            # Check for abs(3301 - primes)
                            key_abs = [ abs(3301 - i) for i in key ]
                            processed_text = ProcessedText(rune_text=' '.join(header_words), section=section)
                            KeystreamTransformer(keystream=iter(key_abs), interrupt_indices=interrupt_indices).transform(processed_text)
                            pt_header_words = processed_text.get_rune_words()
                            if len([ word for word in pt_header_words if word in wordlist ]) == len(pt_header_words):
                                plaintext_latin = RuneUtils.runes_to_latin(' '.join(pt_header_words))
                                print(f'Primes abs(3301-x) key: {key} with skip {skip} and start value of {start_val} yields {plaintext_latin} (interrupt_indices={interrupt_indices})')

                            # Check Totient of primes
                            key = [ i - 1 for i in key ]
                            processed_text = ProcessedText(rune_text=' '.join(header_words), section=section)
                            KeystreamTransformer(keystream=iter(key), interrupt_indices=interrupt_indices).transform(processed_text)
                            pt_header_words = processed_text.get_rune_words()
                            if len([ word for word in pt_header_words if word in wordlist ]) == len(pt_header_words):
                                plaintext_latin = RuneUtils.runes_to_latin(' '.join(pt_header_words))
                                print(f'Totient primes key: {key} with skip {skip} and start value of {start_val} yields {plaintext_latin} (interrupt_indices={interrupt_indices})')

                            # Check for abs(3301 - tot(primes))
                            key_abs = [ abs(3301 - i) for i in key ]
                            processed_text = ProcessedText(rune_text=' '.join(header_words), section=section)
                            KeystreamTransformer(keystream=iter(key_abs), interrupt_indices=interrupt_indices).transform(processed_text)
                            pt_header_words = processed_text.get_rune_words()
                            if len([ word for word in pt_header_words if word in wordlist ]) == len(pt_header_words):
                                plaintext_latin = RuneUtils.runes_to_latin(' '.join(pt_header_words))
                                print(f'Totient primes abs(3301-x) key: {key} with skip {skip} and start value of {start_val} yields {plaintext_latin} (interrupt_indices={interrupt_indices})')

                            # Build mirpe key
                            key = [ int(str(i + 1)[::-1]) for i in key ]
                            processed_text = ProcessedText(rune_text=' '.join(header_words), section=section)
                            KeystreamTransformer(keystream=iter(key), interrupt_indices=interrupt_indices).transform(processed_text)
                            pt_header_words = processed_text.get_rune_words()
                            if len([ word for word in pt_header_words if word in wordlist ]) == len(pt_header_words):
                                plaintext_latin = RuneUtils.runes_to_latin(' '.join(pt_header_words))
                                print(f'Emirps (Decimal-reverse primes) key: {key} with skip {skip} and start value of {start_val} yields {plaintext_latin} (interrupt_indices={interrupt_indices})')

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8))
    @staticmethod
    def double_tot_index_with_reversing():
        """
            Adds or substructs either tot(primes) or tot(tot(primes)), on both normal text as well as reversed text.
            If the number of prefixed words are above the given threshold or the IOC is above the given threshold, print result.
        """

        # Iterate all sections
        for section in tqdm(ResearchUtils.get_unsolved_sections(), desc='Sections being analyzed'):

            # Iterate all number of totient operations
            for tot_call_count in range(1, 3):
               
                # Try adding or substructing
                for add_option in (False, True):

                    # Also attempt emirps
                    for emirp_val in (False, True):

                        # Try reversing and then run totient index manipulation
                        pt = ProcessedText(section=section)
                        ReverseTransformer().transform(pt)
                        TotientPrimeTransformer(tot_calls=tot_call_count, add=add_option, emirp=emirp_val).transform(pt)
                        pt.check_measurements()

                        # Try without reversing
                        pt.revert()
                        TotientPrimeTransformer(tot_calls=tot_call_count, add=add_option, emirp=emirp_val).transform(pt)
                        pt.check_measurements()

                        # Reverse after totient index manipulation
                        ReverseTransformer().transform(pt)
                        pt.check_measurements()

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8))
    @staticmethod
    def totient_keystream():
        """
            Uses the Totient function of natural numbers as a keystream.
        """

        # Iterate all sections
        for section in tqdm(ResearchUtils.get_unsolved_sections(), desc='Sections being analyzed'):

                # Try adding or substructing
                for add_option in (False, True):

                    # Start at zero or not
                    for start_at_0 in (False, True):

                        # Apply keystream
                        pt = ProcessedText(section=section)
                        TotientKeystreamTransformer(add=add_option, start_at_0=start_at_0).transform(pt)
                        pt.check_measurements(add=add_option, start_at_0=start_at_0)

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8)) 
    @staticmethod
    def use_2013_missing_primes():
        """
            Attempts to use the Cicada 3301 message missing primes from 2013 as a keystream.
            Also attempts to use emirps (Decimal-reversed primes).
        """

        # Build the Emirp keystream
        emirp_ks = [ int(str(p)[::-1]) for p in MISSING_PRIMES_2013 ]

        # Iterate all sections 
        for section in tqdm(ResearchUtils.get_unsolved_sections()):

            # Whether to add or substruct
            for add in (False, True):

                # Try decryption
                pt = ProcessedText(section=section)
                KeystreamTransformer(add=add, keystream=iter(MISSING_PRIMES_2013)).transform(pt)
                pt.check_measurements()

                # Try with Emirps
                pt = ProcessedText(section=section)
                KeystreamTransformer(add=add, keystream=iter(emirp_ks)).transform(pt)
                pt.check_measurements()

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8)) 
    @staticmethod
    def autokey_and_vigenere_bruteforce_with_reversing(min_key_len=6):
        """
            Attempts Autokey or Vigenere bruteforcing with or without reversing the text of each section.
            Uses keys derived from all decrypted sections, with and without replacing all occurrences of first character with "F".
            Also tries reversing all keys.
            Uses all supported modes of Autokey: plaintext, cipehrtext or alternating (starting from either plaintext or ciphertext, or using the Mobius function).
        """

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
                pt = ProcessedText(section=section)
                VigenereTransformer(key=key).transform(pt)
                pt.check_measurements(mode='Vigenere', key=key)

                # Iterate all modes
                for mode in (AutokeyMode.PLAINTEXT, AutokeyMode.CIPHERTEXT, AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT, AutokeyMode.ALT_MOBIUS_START_PLAINTEXT, AutokeyMode.ALT_MOBIUS_START_CIPHERTEXT):

                    # Either try or do not try GP-mode
                    for use_gp in (False, True):

                        # Revert previous runs
                        pt.revert()

                        # Apply Autokey
                        AutokeyTransformer(key=key, mode=mode, use_gp=use_gp).transform(pt)
                        pt.check_measurements(mode=f'Autokey {mode}', key=key)

                        # Reverse
                        ReverseTransformer().transform(pt)
                        pt.check_measurements(mode=f'Autokey {mode} then reversing', key=key)

                        # Start from reversing and then apply Autokey
                        pt.revert()
                        ReverseTransformer().transform(pt)
                        AutokeyTransformer(key=key, mode=mode, use_gp=use_gp).transform(pt)
                        pt.check_measurements(mode=f'Reversing then Autokey {mode}', key=key)

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8))
    @staticmethod
    def oeis_keystream():
        """
            Tries all OEIS sequences on each section, using them as keystreams.
        """

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
                    pt = ProcessedText(section=section)
                    KeystreamTransformer(keystream=iter(sequences[seq]), add=add_option).transform(pt)
                    pt.check_measurements(sequence=seq)

                    # Try a special function on the sequence which comes from the Cicada page 15 spiral
                    pt.revert()
                    func_seq = [ abs(3301 - elem) for elem in sequences[seq] ]
                    KeystreamTransformer(keystream=iter(func_seq), add=add_option).transform(pt)
                    pt.check_measurements(mode='Func15', sequence=seq)

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8)) 
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
                pt = ProcessedText(section=section)
                Page15FuncPrimesTransformer(add=add_option).transform(pt)
                pt.check_measurements(mode='Primes', add=add_option)

                # Try on Fibonacci-indexed primes
                pt.revert()
                Page15FiboPrimesTransformer(add=add_option).transform(pt)
                pt.check_measurements(mode='Func15-fibonacci-primes', add=add_option)

                # Try on Fibonacci-indexed emirps
                pt.revert()
                Page15FiboPrimesTransformer(add=add_option, emirp=True).transform(pt)
                pt.check_measurements(mode='Func15-fibonacci-emirps', add=add_option)

                # Try the Totient of the Fibonacci-indexed primes
                pt.revert()
                KeystreamTransformer(add=add_option, keystream=map(lambda x:sympy.totient(x), MathUtils.get_fibo_primes())).transform(pt)
                pt.check_measurements(mode='Totient-fibonacci-primes', add=add_option)
                
                # Try the Totient of the function from page 15 on Fibonacci indexed primes
                pt.revert()
                KeystreamTransformer(add=add_option, keystream=map(lambda x:abs(3301 - sympy.totient(x)), MathUtils.get_fibo_primes())).transform(pt)
                pt.check_measurements(mode='Func15-totient-fibonacci-primes', add=add_option)
              
                # Try on Fibonacci-indexed primes without the page 15 function
                pt.revert()
                FiboPrimesTransformer(add=add_option).transform(pt)
                pt.check_measurements(mode='Fibonacci-primes', add=add_option) 
 
                # Try on Fibonacci-indexed emirps without the page 15 function
                pt.revert()
                FiboPrimesTransformer(add=add_option, emirp=True).transform(pt)
                pt.check_measurements(mode='Fibonacci-emirps', add=add_option)

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8))
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
                    pt = ProcessedText(section=section)
                    SpiralSquareKeystreamTransformer(matrix=square, add=add_option).transform(pt)
                    pt.check_measurements(square=square_index, add=add_option)
 
    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8))
    @staticmethod
    def hill_cipher():
        """
            Tries to perform Hill Cipher with all squares.
        """

        # Build a new square from the sum of first two squares
        squares = SQUARES[:]
        squares.append(squares[0] + squares[1])
        squares.append(squares[0] * squares[1])

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all squares
            square_index = -1
            for square in squares:
                
                # Either inverse or not
                for inverse_option in (False, True):

                    # Use Hill cipher
                    square_index += 1
                    pt = ProcessedText(section=section)
                    HillCipherTransformer(matrix=square, inverse=inverse_option).transform(pt)
                    pt.check_measurements(square=square_index, inverse=inverse_option)

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8))
    @staticmethod
    def gp_value_autokey():
        """
            Attempts to use the GP-value of previous runes as an Autokey, in both modes (plaintext, ciphertext).
        """

        # Iterate all unsolved sections
        for section in tqdm(ResearchUtils.get_unsolved_sections()):

            # Iterate all options
            for primer_value in range(RuneUtils.size()):
                for add_option in (False, True):
                    for use_plaintext in (False, True):

                        # Use an Autokey
                        pt = ProcessedText(section=section)
                        AutokeyGpTransformer(add=add_option, primer_value=primer_value, use_plaintext=use_plaintext).transform(pt)
                        pt.check_measurements(primer_value=primer_value, add=add_option, use_plaintext=use_plaintext)

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8)) 
    @staticmethod
    def gp_sum_keystream():
        """
            Attempts to use the GP-sum of each solved section words as a keystream.
            Also attempts to use the GP-sums of entire solved LP1 as a keystream.
            Also attempts to use line GP-sums of solved sections from LP1.
        """

        # Build dictionary mapping solved sections to GP-sum based streams
        lp1_keystream_words = []
        lp1_keystream_lines = []
        had_unsolved = False
        streams = []
        result = set()
        for section in LiberPrimus.get_all_sections():

            # Process all text
            processed_text = ProcessedText(section=section)
            for transformer in section.transformers:
                transformer.transform(processed_text)
            
            # Skip unsolved sections
            if processed_text.is_unsolved():
                had_unsolved = True
                continue

            # Get the word stream
            stream_words = [ RuneUtils.runes_to_gp_sum(word) for word in processed_text.get_rune_words() ]
            if len(stream_words) > 0:
                streams.append(stream_words)

            # Get the line stream
            stream_lines = [ RuneUtils.runes_to_gp_sum(line) for line in processed_text.split_lines(include_empty_lines=False) ]
            if len(stream_lines) > 0:
                streams.append(stream_lines)

            # Append current section stream to the LP1 keystreams
            if not had_unsolved:
                lp1_keystream_words += stream_words
                lp1_keystream_lines += stream_lines

        # Add LP1 keystreams to the front of the streams
        streams.insert(0, lp1_keystream_words)
        streams.insert(0, lp1_keystream_lines)

        # Iterate all unsolved sections and attempt to use each stream on each section
        for section in tqdm(ResearchUtils.get_unsolved_sections()):

            # Iterate all streams 
            stream_index = -1
            for stream in streams:
                
                # Use a keystream
                stream_index += 1
                for add_option in (False, True):
                    pt = ProcessedText(section=section)
                    KeystreamTransformer(keystream=iter(stream), add=add_option).transform(pt)
                    pt.check_measurements(stream=stream_index, add=add_option)

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8))
    @staticmethod
    def square_sections_spiral():
        """
            Performs a spiral transformation on sections with numbers of runes that are a square.
        """

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Conclude if the number of runes is a square
            pt = ProcessedText(section=section)
            runes = pt.get_runes()
            if not MathUtils.is_square(len(runes)):
                continue

            # Treat as a square matrix
            side = MathUtils.sqrt(len(runes))
            matrix = sympy.Matrix([ [ RuneUtils.get_rune_index(rune) for rune in runes[i:i+side] ] for i in range(0, len(runes), side) ])

            # Walk the matrix in a spiral
            pt.set_runes([ RuneUtils.rune_at(index) for index in MathUtils.matrix_to_spiral_stream(matrix) ])
            pt.check_measurements(size=f'{side}x{side}')

    @measurement(PrefixWordsMeasurement(threshold=6))
    @measurement(IocMeasurement(threshold=1.8))
    @staticmethod
    def modular_inverse():
        """
            Performs a modular inverse of each rune in each unsolved section (except the zero-th rune).
        """
            
        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Perform modular inverse
            pt = ProcessedText(section=section)
            ModInvTransformer(use_shift_counter=True).transform(pt)
            pt.check_measurements()

    @measurement(PrefixWordsMeasurement(threshold=4))
    @measurement(IocMeasurement(threshold=1.8))
    @staticmethod
    def primes_indices_apart():
        """
            Performs a keystream manipulation on runes based on prime numbers that are 11 or 13 indices apart.
            This logic was concluded based on Liber Primus 1 (first solved pages) that have the numbers 107, 167, 229.
            The number 13 was derived based on IoC analysis on several pages, specifically 54-55.
        """

        # Iterate all sections
        for section in tqdm(ResearchUtils.get_unsolved_sections()):

            # Start values could be either 107 (naturally from LP1), 13 (lowest prime to start from assuming 107 is in sequence) and 2 (first prime)
            for start_value in (107, 13, 2, 0):
                
                # Either adding or substructing
                for add_option in (False, True):

                    # Either work with 13 or 11
                    for indices_apart in (13, 11):

                        # Use the prime sequence
                        pt = ProcessedText(section=section)
                        PrimesIndicesApartTransformer(add=add_option, start_value=start_value, indices_apart=indices_apart).transform(pt)
                        pt.check_measurements(start_value=start_value, add=add_option, skip=indices_apart)

                        # Try Atbash
                        AtbashTransformer().transform(pt)
                        pt.check_measurements(start_value=start_value, add=add_option, skip=indices_apart, mode='Atbash')

                        # Revert Atbash
                        AtbashTransformer().transform(pt)

                        # Try shifting
                        for shift_value in range(1, RuneUtils.size()):
                            ShiftTransformer(shift=1).transform(pt)
                            pt.check_measurements(start_value=start_value, add=add_option, skip=indices_apart, shift=shift_value)

    @measurement(PrefixWordsMeasurement(threshold=4))
    @measurement(IocMeasurement(threshold=1.8)) 
    @staticmethod
    def use_cuneiform_keystream():
        """
            Uses the Cuneiform stream as a keystream in either base 59 or base 60.
        """

        # Get an extended wordlist for a measurement
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Translate Cuneiform to base60 or base59 and try all combinations
        for base in (60, 59):

            # Build all the digit chunks since we do not know the ordering
            lowercases = string.ascii_lowercase[:-2]
            if base == 59:
                lowercases = ''.join([ c for c in lowercases if c != 'f' ])
            digit_chunks = [ string.digits, string.ascii_uppercase, lowercases ]

            # Iterate all ordering options
            for digit_ordering in tqdm(itertools.permutations(digit_chunks), desc=f'Base{base} with all ordering permutations'):

                # Build the keystream (both ordered and reversed) 
                digits = ''.join(digit_ordering)
                order_marker = '<'.join([ chunk[0] for chunk in digit_ordering ])
                cuneiform_stream = [ digits.index(i[0]) * base + digits.index(i[1]) for i in CUNEIFORM_STREAM ]
                keystreams = [ cuneiform_stream, cuneiform_stream[::-1] ]

                # Try both normal and reversed keystreams
                for keystream in keystreams:

                    # Iterate all sections
                    for section in ResearchUtils.get_unsolved_sections():

                        # Either add or substruct
                        for add_option in (False, True):

                            # Try decryption
                            pt = ProcessedText(section=section)
                            KeystreamTransformer(add=add_option, keystream=iter(keystream)).transform(pt)
                            pt.check_measurements(base=base, order=order_marker, add=add_option)

    @staticmethod
    def outguess_dictionary_attack(text_len_threthold=50):
        """
            Performs an Outguess dictionary attack (both English and runes, as well as few selected prime numbers used by Cicada).
        """

        # Get the outguess path
        outguess_path = ResearchUtils.get_command_path('outguess')
        assert outguess_path is not None, Exception('The outguess binary was not found - please install outguess and make sure it\'s in PATH')

        # Get potential rune keys
        keys = list(ResearchUtils.get_english_dictionary_words(as_runes=True))

        # Add "F" replacements for keys
        keys += [ k.replace(k[0], RuneUtils.rune_at(0)) for k in keys ]
        
        # Add English words (both uppercase and lowecase)
        english_words = [ w.upper() for w in list(ResearchUtils.get_english_dictionary_words(as_runes=False)) ]
        english_words += [ w.lower() for w in english_words ]
        keys += english_words

        # Add specific primes used by Cicada
        keys += [ '3301', '1033', '761', '167' ]

        # Add an empty key and the option to not use a key
        keys.append('')
        keys.append(None)

        # Create a temporary file for outguess
        temp_file_path = tempfile.mktemp()

        # Iterate all pages that have file paths
        for section in LiberPrimus.get_all_sections():
            page_index = 0
            for page in section.pages:
                if page.filepath is None:
                    continue

                # Try all keys
                page_index += 1
                for key in tqdm(keys, desc=f'Section "{section.name}" (page {page_index}/{len(section.pages)})'):

                    # Run outguess and retrieve file
                    if key is None:
                        args = [ outguess_path, '-r', page.filepath, temp_file_path ]
                    else:
                        args = [ outguess_path, '-k', key, '-r', page.filepath, temp_file_path ]
                    subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    try:
                        with open(temp_file_path, 'r') as fp:
                            contents = fp.read()
                    except Exception:
                        continue

                    # Try either to decode as PGP or just retireve printable data
                    if len(contents) < text_len_threthold:
                        continue
                    if 'BEGIN PGP SIGNED MESSAGE' in contents or contents.isprintable():
                        ResearchUtils.print_section_data(section, None)
                        key_str = '<NO KEY>' if key is None else key
                        screen.print_yellow(f'Key: {key_str}')
                        print(contents)

    @measurement(PrefixWordsMeasurement(threshold=4))
    @measurement(IocMeasurement(threshold=1.8)) 
    @staticmethod
    def fibonacci_sequence_keystream_bruteforce(consider_interrupters=False):
        """
            Performs a keystream manipulation on runes based on Fibonacci sequence starting at every two numbers between 0 and 28.
        """

        # Get an extended wordlist for a measurement
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all start values
            with tqdm(total=29*29, desc=f'Section "{section.name}"') as pbar:
                for start_a in range(29):
                    for start_b in range(29):

                        # Either add or substruct
                        for add_option in (False, True):

                            # Consider interrupters
                            pt = ProcessedText(section=section)
                            gen = ResearchUtils.iterate_potential_interrupter_indices(pt) if consider_interrupters else [[]]
                            for interrupt_indices in gen:

                                # Revert processed text
                                pt.revert()

                                # Apply keystream
                                FibonacciKeystreamTransformer(add=add_option, start_a=start_a, start_b=start_b, interrupt_indices=interrupt_indices).transform(pt)
                                pt.check_measurements(start_a=start_a, start_b=start_b, add=add_option)

                        # Update progress bar
                        pbar.update(1)

def main():
    """
        Main routine.
    """

    # List all static methods in Attempts
    attempts = [ (k, v) for (k, v) in Attempts.__dict__.items() if isinstance(v, staticmethod) ]
    menu_items = [ (k.replace('_', ' ').title(), v.__func__.__doc__.strip().split('\n')[0]) for (k, v) in attempts ]

    # Run forever
    while True:

        # Run menu
        try:
            choice = screen.run_menu('== METHODS AVAILABLE ==', menu_items)

            # Handle quitting
            if choice is None:
                return

            # Handle a valid choice
            screen.clear()
            screen.print_yellow(f'== {menu_items[choice][0]} ==\n')
            attempts[choice][1].__func__()
            screen.print_green('\n\nEXECUTION COMPLETE\n')
            screen.press_enter()

        except KeyboardInterrupt:
            screen.print_red('\n\nSTOPPED BY USER\n')
            screen.press_enter()
            continue

if __name__ == '__main__':
    main()
    
