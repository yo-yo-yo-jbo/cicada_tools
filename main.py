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
import logging

class Experiments(object):
    """
        Experiments made.
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
                screen.print_yellow('GP-sums of words:', end='')
                print(f'  {processed_text.get_gp_sum_of_words()}')
                screen.print_yellow('GP-sums of sentences:', end='')
                print(f' {processed_text.get_gp_sum_of_sentences()}\n')
            
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

    @measurement(AllWordsMeasurement())
    @staticmethod
    def sentence_cribbing(skip_limit=31, start_val_limit=3301, consider_interrupters=False):
        """
            Attempts cribbing the first sentence automatically, assuming a prime-related ascending key.
            Assumes interrupters might occur. Also attempts to use emirps (Decimal-reversal of primes).
        """

        # Get words
        wordlist = ResearchUtils.get_rune_wordlist(True)

        # Work on unsolved sections
        unsolved_sections = ResearchUtils.get_unsolved_sections()
        max_runes = max([ ProcessedText(section=section).get_num_of_runes() for section in unsolved_sections ])

        # Build a primes cache
        with tqdm(desc='Building primes cache') as pbar:
            max_prime = MathUtils.find_next_prime(start_val_limit)
            primes = [ 2 ]
            while max_prime not in primes:
                primes.append(MathUtils.find_next_prime(primes[-1]))
                pbar.update(1)
            for i in range((skip_limit + 1) * max_runes):
                primes.append(MathUtils.find_next_prime(primes[-1]))
                pbar.update(1)

        # Either reverse or not
        for rev_option in (False, True):

            # Iterate all unsolved sections
            for section in unsolved_sections:

                # Get the section number of runes
                section_runes_len = ProcessedText(section=section).get_num_of_runes()

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
                for skip in tqdm(range(1, skip_limit), desc=f'Section "{section.name}" (rev={rev_option})'):
                    for start_index in range(0, len(primes) - skip*section_runes_len):
                       
                        # Take interrupters into account
                        gen = ResearchUtils.iterate_potential_interrupter_indices(header_pt) if consider_interrupters else [[]]
                        for interrupt_indices in gen:

                            # Build primes key
                            key = [ primes[i] for i in range(start_index, start_index + skip * section_runes_len, skip) ]

                            # Check for primes
                            pt = ProcessedText(rune_text=' '.join(header_words), section=section)
                            KeystreamTransformer(keystream=iter(key), interrupt_indices=interrupt_indices).transform(pt)
                            pt.check_measurements(key=key, mode='Primes', skip=skip, start=key[0])
                            
                            # Check for abs(3301 - primes)
                            pt.revert()
                            key_abs = [ abs(3301 - i) for i in key ]
                            KeystreamTransformer(keystream=iter(key_abs), interrupt_indices=interrupt_indices).transform(pt)
                            pt.check_measurements(key=key, mode='Func15', skip=skip, start=key[0])

                            # Check Totient of primes
                            pt.revert()
                            key = [ i - 1 for i in key ]
                            KeystreamTransformer(keystream=iter(key), interrupt_indices=interrupt_indices).transform(pt)
                            pt.check_measurements(key=key, mode='Totient', skip=skip, start=key[0])

                            # Check for abs(3301 - tot(primes))
                            pt.revert()
                            key_abs = [ abs(3301 - i) for i in key ]
                            KeystreamTransformer(keystream=iter(key_abs), interrupt_indices=interrupt_indices).transform(pt)
                            pt.check_measurements(key=key, mode='Func15-Totient', skip=skip, start=key[0])

                            # Build mirpe key
                            pt.revert()
                            key = [ int(str(i + 1)[::-1]) for i in key ]
                            KeystreamTransformer(keystream=iter(key), interrupt_indices=interrupt_indices).transform(pt)
                            pt.check_measurements(key=key, mode='Emirps', skip=skip, start=key[0])

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4))
    @staticmethod
    def double_tot_index_with_reversing():
        """
            Adds or substructs either tot(primes) or tot(tot(primes)), on both normal text as well as reversed text.
            If the number of prefixed words are above the given threshold or the IOC is above the given threshold, print result.
        """

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all number of totient operations
            for tot_call_count in tqdm(range(1, 3), desc=f'Section "{section.name}"'):
               
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

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4))
    @staticmethod
    def totient_keystream():
        """
            Uses the Totient function of natural numbers as a keystream.
        """

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

                # Try adding or substructing
                for add_option in tqdm((False, True), desc=f'Section "{section.name}"'):

                    # Start at zero or not
                    for start_at_0 in (False, True):

                        # Apply keystream
                        pt = ProcessedText(section=section)
                        TotientKeystreamTransformer(add=add_option, start_at_0=start_at_0).transform(pt)
                        pt.check_measurements(add=add_option, start_at_0=start_at_0)

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4)) 
    @staticmethod
    def use_2013_missing_primes():
        """
            Attempts to use the Cicada 3301 message missing primes from 2013 as a keystream.
            Also attempts to use emirps (Decimal-reversed primes).
        """

        # Build the Emirp keystream
        emirp_ks = [ int(str(p)[::-1]) for p in MISSING_PRIMES_2013 ]

        # Iterate all sections 
        for section in ResearchUtils.get_unsolved_sections():

            # Whether to add or substruct
            for add in tqdm((False, True), desc=f'Section "{section.name}"'):

                # Try decryption
                pt = ProcessedText(section=section)
                KeystreamTransformer(add=add, keystream=iter(MISSING_PRIMES_2013)).transform(pt)
                pt.check_measurements()

                # Try with Emirps
                pt = ProcessedText(section=section)
                KeystreamTransformer(add=add, keystream=iter(emirp_ks)).transform(pt)
                pt.check_measurements()

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4))
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

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4)) 
    @staticmethod
    def page15_function_keystream():
        """
            Uses abs(3301-p) on all primes p as a keystream, as well as Fibonacci-indexed primes and other variants.
            This function was concluded from the Page 15 square matrix.
        """

        # Iterate all sections 
        for section in ResearchUtils.get_unsolved_sections():

            # Try adding or substructing
            for add_option in tqdm((False, True), desc=f'Section "{section.name}"'):

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

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4))
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
            for square in tqdm(SQUARES, desc=f'Section "{section.name}"'):
                
                # Try adding or substructing
                square_index += 1
                for add_option in (False, True):

                    # Use as a keystream
                    pt = ProcessedText(section=section)
                    SpiralSquareKeystreamTransformer(matrix=square, add=add_option).transform(pt)
                    pt.check_measurements(square=square_index, add=add_option)
 
    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4))
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
            for square in tqdm(squares, desc=f'Section "{section.name}"'):
                
                # Either inverse or not
                for inverse_option in (False, True):

                    # Use Hill cipher
                    square_index += 1
                    pt = ProcessedText(section=section)
                    HillCipherTransformer(matrix=square, inverse=inverse_option).transform(pt)
                    pt.check_measurements(square=square_index, inverse=inverse_option)

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4))
    @staticmethod
    def gp_value_autokey():
        """
            Attempts to use the GP-value of previous runes as an Autokey, in both modes (plaintext, ciphertext).
        """

        # Iterate all unsolved sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all options
            for primer_value in tqdm(range(RuneUtils.size()), desc=f'Section "{section.name}"'):
                for add_option in (False, True):
                    for use_plaintext in (False, True):

                        # Use an Autokey
                        pt = ProcessedText(section=section)
                        AutokeyGpTransformer(add=add_option, primer_value=primer_value, use_plaintext=use_plaintext).transform(pt)
                        pt.check_measurements(primer_value=primer_value, add=add_option, use_plaintext=use_plaintext)

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.6)) 
    @staticmethod
    def gp_sum_keystream():
        """
            Attempts to use the GP-sum of each solved section words as a keystream, in various forms (as-is, as indices to primes and so on).
        """

        # Container for streams
        streams = []
        total_enc_stream_words = []
        total_dec_stream_words = []
        total_enc_stream_sentences = []
        total_dec_stream_sentences = []
        total_enc_stream_words_no_titles = []
        total_dec_stream_words_no_titles = []
        total_enc_stream_sentences_no_titles = []
        total_dec_stream_sentences_no_titles = []
        product_sums_enc = []
        product_sums_enc_no_titles = []
        product_sums_dec = []
        product_sums_dec_no_titles = []

        # Iterate all solved sections
        for section in tqdm(LiberPrimus.get_all_sections(), desc='Building streams from sections'):

            # Process text and skip unsolved sections
            pt = ProcessedText(section=section)
            for transformer in section.transformers:
                transformer.transform(pt)
            if pt.is_unsolved():
                continue

            # Work on either encrypted or decrypted section
            for use_enc in (False, True):

                # Handle encrypted by reverting (processed text was transformed by the section's transformers previously)
                if use_enc:

                    # Skip direct translations as decrypted and encrypted runes are equal
                    if len(section.transformers) == 0:
                        continue
                    pt.revert()

                # Add a stream for the processed text words and sentences
                streams.append(pt.get_gp_sum_of_runes())
                streams.append(pt.get_gp_sum_of_words())
                streams.append(pt.get_gp_sum_of_sentences())
                if use_enc:
                    total_enc_stream_words += pt.get_gp_sum_of_words()
                    total_enc_stream_sentences += pt.get_gp_sum_of_sentences()
                else:
                    total_dec_stream_words += pt.get_gp_sum_of_words()
                    total_dec_stream_sentences += pt.get_gp_sum_of_sentences()

                # Take the product of the GP-sums of sentences and split to groups of 3 as dictated by 2013 Parable message
                prod_string_rev = str(sympy.prod(pt.get_gp_sum_of_sentences()))[::-1]
                if use_enc:
                    product_sums_enc += [ int(prod_string_rev[i:i+3][::-1]) for i in range(0, len(prod_string_rev), 3) ]
                else:
                    product_sums_dec += [ int(prod_string_rev[i:i+3][::-1]) for i in range(0, len(prod_string_rev), 3) ]

                # Handle the section without titles
                pt_no_titles = ProcessedText(rune_text=section.get_all_text(exclude_titles=True), section=section)
                if pt_no_titles.get_runes() == pt.get_runes():
                    continue
                streams.append(pt_no_titles.get_gp_sum_of_runes())
                streams.append(pt_no_titles.get_gp_sum_of_words())
                streams.append(pt_no_titles.get_gp_sum_of_sentences())
                if use_enc:
                    total_enc_stream_words_no_titles += pt_no_titles.get_gp_sum_of_words()
                    total_enc_stream_sentences_no_titles += pt_no_titles.get_gp_sum_of_sentences()
                else:
                    total_dec_stream_words_no_titles += pt_no_titles.get_gp_sum_of_words()
                    total_dec_stream_sentences_no_titles += pt_no_titles.get_gp_sum_of_sentences()

                # Take the product of the GP-sums of sentences and split to groups of 3 as dictated by 2013 Parable message
                prod_string_rev = str(sympy.prod(pt_no_titles.get_gp_sum_of_sentences()))[::-1]
                if use_enc:
                    product_sums_enc_no_titles += [ int(prod_string_rev[i:i+3][::-1]) for i in range(0, len(prod_string_rev), 3) ]
                else:
                    product_sums_dec_no_titles += [ int(prod_string_rev[i:i+3][::-1]) for i in range(0, len(prod_string_rev), 3) ]

        # Adjust streams
        streams.append(total_enc_stream_words)
        streams.append(total_dec_stream_words)
        streams.append(total_enc_stream_sentences)
        streams.append(total_dec_stream_sentences)
        streams.append(total_enc_stream_words_no_titles)
        streams.append(total_dec_stream_words_no_titles)
        streams.append(total_enc_stream_sentences_no_titles)
        streams.append(total_dec_stream_sentences_no_titles)
        streams.append([ val for val in product_sums_enc if val > 0 ])
        streams.append([ val for val in product_sums_dec if val > 0 ])
        streams.append([ val for val in product_sums_enc_no_titles if val > 0 ])
        streams.append([ val for val in product_sums_dec_no_titles if val > 0 ])
        streams = [ stream for stream in streams if len(stream) > 0 ]

        # Build primes and the Fibonacci sequence
        max_value = max([ max(stream) for stream in streams ])
        primes = [ 2 ]
        fibonacci = [ 1, 2 ]
        with tqdm(total=max_value - 1, desc=f'Building primes and Fibonacci numbers for stream values') as pbar:
            while len(primes) < max_value:
                primes.append(MathUtils.find_next_prime(primes[-1]))
                fibonacci.append(fibonacci[-2] + fibonacci[-1])
                pbar.update(1)
        
        # Iterate all unsolved sections and attempt to use each stream on each section
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all streams 
            stream_index = -1
            for stream in tqdm(streams, desc=f'Section "{section.name}"'):
                
                # Use a keystream
                stream_index += 1
                for add_option in (False, True):

                    # Either reverse or not
                    for rev_option in (False, True):

                        # Build base stream
                        base_stream = stream[::-1] if rev_option else stream

                        # Use as-is
                        pt = ProcessedText(section=section)
                        KeystreamTransformer(keystream=iter(base_stream), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='AsIs', reverse=rev_option)

                        # Try the function from page 15
                        pt.revert()
                        func15_ks = [ abs(3301 - val) for val in base_stream ]
                        KeystreamTransformer(keystream=iter(func15_ks), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='Func15', reverse=rev_option)

                        # Take the totients of the keystream
                        pt.revert()
                        totients = [ MathUtils.totient(val) for val in base_stream ]
                        KeystreamTransformer(keystream=iter(totients), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='Totients', reverse=rev_option)

                        # Use values as prime indices
                        pt.revert()
                        prime_indices = [ primes[val - 1] for val in base_stream ]
                        KeystreamTransformer(keystream=iter(prime_indices), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='PrimeIndices', reverse=rev_option)

                        # Use Emirp indices
                        pt.revert()
                        emirp_indices = [ int(str(val)[::-1]) for val in prime_indices ]
                        KeystreamTransformer(keystream=iter(emirp_indices), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='EmirpIndices', reverse=rev_option)

                        # Use Totient value of the prime indices
                        pt.revert()
                        totient_prime_indices = [ MathUtils.totient(val) for val in prime_indices ]
                        KeystreamTransformer(keystream=iter(totient_prime_indices), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='TotientOfPrimeIndices', rev=rev_option)

                        # Use Totient value of the Emirp indices
                        pt.revert()
                        totient_emirp_indices = [ MathUtils.totient(val) for val in emirp_indices ]
                        KeystreamTransformer(keystream=iter(totient_emirp_indices), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='TotientOfEmirpIndices', rev=rev_option)

                        # Use as Fibonacci sequence indices
                        pt.revert()
                        fibonacci_indices = [ fibonacci[val - 1] for val in base_stream ]
                        KeystreamTransformer(keystream=iter(fibonacci_indices), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='FibonacciIndices', rev=rev_option)

                        # Only take primes from the keystream
                        primes_ks = [ val for val in base_stream if sympy.isprime(val) ]
                        if len(primes_ks) == 0:
                            continue
                        pt.revert()
                        KeystreamTransformer(keystream=iter(primes_ks), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='Primes', rev=rev_option)

                        # Take the Totient value of the primes
                        tot_primes_ks = [ MathUtils.totient(val) for val in primes_ks ]
                        pt.revert()
                        KeystreamTransformer(keystream=iter(tot_primes_ks), add=add_option).transform(pt)
                        pt.check_measurements(stream=stream_index, add=add_option, mode='TotientOfPrimes', rev=rev_option)

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

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4))
    @staticmethod
    def primes_indices_apart(max_skip=167, max_start_value=3301):
        """
            Performs a keystream manipulation on runes based on prime numbers that are indices apart.
        """

        # Generate primes
        assert max_skip > 0, Exception('Skip value must be strictly positive')
        assert sympy.isprime(max_start_value), Exception('Maximal start value must be prime')
        unsolved_sections = ResearchUtils.get_unsolved_sections()
        max_runes = max([ ProcessedText(section=section).get_num_of_runes() for section in unsolved_sections ])
        primes = [ 2 ]
        start_values = [ 2 ]
        with tqdm(desc='Generating initial primes') as pbar:
            while max_start_value not in primes:
                primes.append(MathUtils.find_next_prime(primes[-1]))
                start_values.append(primes[-1])
                pbar.update(1)
        for i in tqdm(range((max_skip + 1) * max_runes), desc='Extending primes'):
            primes.append(MathUtils.find_next_prime(primes[-1]))

        # Iterate all sections
        for section in unsolved_sections:

            # Iterate all start values and skip values
            with tqdm(desc=f'Section "{section.name}"', total=max_skip * len(start_values)) as pbar:
                for start_value in start_values:
                    for skip_value in range(1, max_skip + 1):

                        # Either adding or substructing
                        for add_option in (False, True):

                            # Use the prime sequence
                            pt = ProcessedText(section=section)
                            prime_index = primes.index(start_value)
                            ks = [ primes[i] for i in range(prime_index, prime_index + skip_value * max_runes, skip_value) ]
                            KeystreamTransformer(add=add_option, keystream=iter(ks)).transform(pt)
                            pt.check_measurements(start_value=start_value, add=add_option, skip=skip_value, mode='AsIs')

                            # Try Atbash
                            AtbashTransformer().transform(pt)
                            pt.check_measurements(start_value=start_value, add=add_option, skip=skip_value, mode='Atbash')

                            # Revert Atbash
                            AtbashTransformer().transform(pt)

                            # Try shifting
                            for shift_value in range(1, RuneUtils.size()):
                                ShiftTransformer(shift=1).transform(pt)
                                pt.check_measurements(start_value=start_value, add=add_option, skip=skip_value, shift=shift_value, mode='Shift')
                        
                        # Update progrsss bar
                        pbar.update(1)

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4)) 
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
        keys += [ '3301', '1033', '761', '167', '1595277641' ]

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
    def primes_indexed_by_totient_keystream(consider_interrupters=False):
        """
            Performs a keystream manipulation on runes based on the primes that are indexed by the Totient of the natural numbers.
        """

        # Saves the keystream
        keystream = [ 2 ]
        primes = [ 2 ]

        # Iterate all sections
        for section in tqdm(ResearchUtils.get_unsolved_sections()):

            # Extend the keystream as required
            pt = ProcessedText(section=section)
            while len(keystream) < pt.get_num_of_runes():
                next_tot = MathUtils.totient(len(keystream) + 1)
                while len(primes) <= next_tot:
                    primes.append(MathUtils.find_next_prime(primes[-1]))
                keystream.append(primes[next_tot - 1])

            # Either add or substruct
            for add_option in (False, True):

                # Consider interrupters
                pt = ProcessedText(section=section)
                gen = ResearchUtils.iterate_potential_interrupter_indices(pt) if consider_interrupters else [[]]
                for interrupt_indices in gen:

                    # Revert processed text
                    pt.revert()

                    # Apply keystream
                    KeystreamTransformer(add=add_option, keystream=iter(keystream), interrupt_indices=interrupt_indices).transform(pt)
                    pt.check_measurements(add=add_option)

    @measurement(PrefixWordsMeasurement(threshold=4))
    @measurement(IocMeasurement(threshold=1.8)) 
    @staticmethod
    def fibonacci_sequence_keystream_bruteforce(consider_interrupters=False):
        """
            Performs a keystream manipulation on runes based on Fibonacci sequence starting at every two numbers between 0 and 28.
        """

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all start values
            with tqdm(total=RuneUtils.size() * RuneUtils.size(), desc=f'Section "{section.name}"') as pbar:
                for start_a in range(RuneUtils.size()):
                    for start_b in range(RuneUtils.size()):

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

    @measurement(PrefixWordsMeasurement(threshold=4))
    @measurement(IocMeasurement(threshold=1.6)) 
    @staticmethod
    def alberti_cipher_bruteforce(max_period=26):
        """
            Attempts to brute-force Alberti cipher configurations.
        """

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all start values
            with tqdm(total=RuneUtils.size() * (RuneUtils.size() - 1) * max_period, desc=f'Section "{section.name}"') as pbar:
                for period in range(1, max_period + 1):
                    for periodic_increment in range(1, RuneUtils.size()):
                        for initial_shift in range(RuneUtils.size()):

                            # Run cipher
                            pt = ProcessedText(section=section)
                            AlbertiTransformer(period=period, periodic_increment=periodic_increment, initial_shift=initial_shift).transform(pt)
                            pt.check_measurements(period=period, periodic_increment=periodic_increment, initial_shift=initial_shift)

                            # Update progress bar
                            pbar.update(1)

    @measurement(PrefixWordsMeasurement(threshold=4))
    @measurement(IocMeasurement(threshold=1.6)) 
    @staticmethod
    def mathematical_constants_digits_keystream(max_period=26):
        """
            Uses mathematical constants digits as keystreams.
        """

        # Work on unsolved sections
        unsolved_sections = ResearchUtils.get_unsolved_sections()
        max_runes = max([ ProcessedText(section=section).get_num_of_runes() for section in unsolved_sections ])

        # Define constants
        consts = {
            'Pi'    : sympy.pi,
            'TwoPi' : 2 * sympy.pi,
            'e'     : sympy.exp(1),
            'Phi'   : sympy.S.GoldenRatio,
            'Sqrt2' : sympy.sqrt(2)
        }

        # Add the constants as keystreams
        keystreams = {}
        for k, v in consts.items():
            digits = [ int(d) for d in str(sympy.N(v, max_runes + 1)).replace('.', '') ]
            keystreams[k] = [ digits, digits[1:] ]

        # Iterate all sections
        for section in unsolved_sections:

            # Iterate all constants
            pt = ProcessedText(section=section)
            for const_name in tqdm(keystreams, desc=f'Section "{section.name}"'):
                for keystream in keystreams[const_name]:

                    # Either add or substruct
                    for add_option in (False, True):

                        # Run cipher
                        pt.revert()
                        KeystreamTransformer(keystream=iter(keystream), add=add_option).transform(pt)
                        pt.check_measurements(const=const_name, add=add_option)

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4)) 
    @staticmethod
    def primes_descend_ascend(max_start_value=3301):
        """
            Uses primes (and Totient of primes) as they descend and then ascend.
        """

        # Validations
        assert sympy.isprime(max_start_value), Exception('Maximum start value must be prime')

        # Build primes
        primes = [ 2 ]
        while max_start_value not in primes:
            primes.append(MathUtils.find_next_prime(primes[-1]))
        rev_primes = primes[::-1]

        # Iterate all sections
        for section in ResearchUtils.get_unsolved_sections():

            # Iterate all start values
            pt = ProcessedText(section=section)
            for start_index in tqdm(range(len(rev_primes)), desc=f'Section "{section.name}"'):

                # Build stream
                ks = rev_primes[start_index:] + primes
                
                # Either add or substruct
                for add_option in (False, True):

                    # Run stream
                    pt.revert()
                    KeystreamTransformer(keystream=iter(ks), add=add_option).transform(pt)
                    pt.check_measurements(start_value=ks[0], add=add_option, mode='AsIs')

                    # Try Totients
                    pt.revert()
                    KeystreamTransformer(keystream=map(sympy.totient, ks), add=add_option).transform(pt)
                    pt.check_measurements(start_value=ks[0], add=add_option, mode='Totients')

    @measurement(PrefixWordsMeasurement(threshold=3))
    @measurement(IocMeasurement(threshold=1.4)) 
    @staticmethod
    def ascii_values_keystream_cribbing_bruteforce(prefix_words_threshold=2):
        """
            Attempts to crib section words by ascii values of dictionary words.
        """

        # Get English words (uppercase)
        english_uppercase = [ word.upper() for word in ResearchUtils.get_english_dictionary_words(as_runes=False) ]

        # Build all word permutations (uppercase)
        uppercase_perms = list(tqdm(itertools.combinations(english_uppercase, prefix_words_threshold), desc=f'Building permutations of {prefix_words_threshold} words with a dictionary size of {len(english_uppercase)}'))

        # Work on unsolved sections
        for section in ResearchUtils.get_unsolved_sections():

            # Process section
            pt = ProcessedText(section=section)

            # Apply keystream
            for option in tqdm(uppercase_perms, desc=f'Section "{section.name}" (lowercase={use_lower})'):

                # Either use uppercase or lowercase
                for use_lower in (False, True):

                    # Either add or substruct
                    for add_option in (False, True):

                        # Map option to a keystream based on ASCII
                        pt.revert()
                        keystream = map(ord, ''.join(option).lower()) if use_lower else map(ord, ''.join(option))
                        KeystreamTransformer(keystream=keystream, add=add_option).transform(pt)
                        pt.check_measurements(key=option, add=add_option, lower=use_lower)

def main():
    """
        Main routine.
    """

    # Logging capability
    logging.basicConfig(filename='CicadaUtils.log', level=logging.INFO)
    logger = logging.getLogger(__name__)

    # List all static methods in Experiments 
    exprs = [ (k, v) for (k, v) in Experiments.__dict__.items() if isinstance(v, staticmethod) ]
    menu_items = [ (k.replace('_', ' ').title(), v.__func__.__doc__.strip().split('\n')[0]) for (k, v) in exprs ]

    # Run forever
    while True:

        # Run menu
        try:
            choice = screen.run_menu('== METHODS AVAILABLE ==', menu_items)

            # Handle quitting
            if choice is None:
                return

            # Handle a valid choice
            logger.info(f'Starting: {menu_items[choice][0]}')
            screen.clear()
            screen.print_yellow(f'== {menu_items[choice][0]} ==\n')
            exprs[choice][1].__func__()
            logger.info(f'Finished: {menu_items[choice][0]}')
            screen.print_green('\n\nEXECUTION COMPLETE\n')
            screen.press_enter()

        except (KeyboardInterrupt, EOFError):
            logger.info(f'Stopped: {menu_items[choice][0]}')
            screen.print_red('\n\nSTOPPED BY USER\n')
            screen.press_enter()
            continue

if __name__ == '__main__':
    main()
    
