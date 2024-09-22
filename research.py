#!/usr/bin/env python3
from pages import PAGES
from core import RUNES
from core import LATIN
from core import ProcessedText
from core import latin_to_runes
import secrets
from transformers import *
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

def get_unsolved_pages():
    """
        Gets all unsolved pages.
    """

    # Try to decrypt all pages
    result = []
    for page in PAGES:

        # Process all text
        processed_text = ProcessedText(page[0])
        page[1].transform(processed_text)

        # Add to result if page is unsolved
        if processed_text.is_unsolved():
            result.append(page[0])

    # Return all unsolved pages
    return result

def get_rune_wordlist(use_dictionary=False):
    """
        Get a Runic wordlist from all solved pages dynamically.
        Can also extend to an English wordlist.
    """

    # Try to decrypt all pages
    result = set()
    for page in PAGES:

        # Process all text
        processed_text = ProcessedText(page[0])
        page[1].transform(processed_text)

        # Skip unsolved pages
        if processed_text.is_unsolved():
            continue

        # Get all words
        for word in processed_text.get_rune_words():
            if len(word) == 0:
                continue
            result.add(word)

    # Optionally extend to use a wordlist
    if use_dictionary:
        with open('english_wordlist.txt', 'r') as fp:
            for word in fp.read().split('\n'):
                runic = latin_to_runes(word)
                if len(runic) > 0:
                    result.add(runic)

    # Return wordlist sorted by word length descending
    return sorted(result, key=len)[::-1]

def runes_to_latin(runes):
    """
        Turns runes to latin, assuming input is only runes.
    """

    # Work based on indices
    return ProcessedText(runes).to_latin()

def indices_to_latin(indices):
    """
        Turns indices to latin.
    """

    # Translate to runes and then to latin
    return runes_to_latin(''.join([ RUNES[i] for i in indices ]))

def auto_crib_get_keys():
    """
        Tries to solve each unsolved page that has enough words at the beginning of a sentence using a crib.
    """

    # Get the word list
    wordlist = get_rune_wordlist()

    # Iterate all unsolved pages
    for page in get_unsolved_pages():

        # Get all words until a period
        header_words = ProcessedText(page.split('.')[0]).get_rune_words()
        if len(header_words) == 0:
            continue
        header_words_lengths = [ len(w) for w in header_words ]
        # JBO
        if header_words_lengths != [2, 6, 3, 5]:
            continue
        # JBO
        ciphertext_runes = ''.join(header_words)

        # Iterate all word combinations for each word length
        all_plaintext_options = [ [ w for w in wordlist if len(w) == w_len ] for w_len in header_words_lengths ]
        total_options = 1
        for opt_list in all_plaintext_options:
            total_options *= len(opt_list)
        option_index = 0
        for plaintext_option in itertools.product(*all_plaintext_options):

            # Increase option index
            option_index += 1

            # JBO
            #if runes_to_latin(plaintext_option[0]) != 'AN':
            #    continue
            #if runes_to_latin(plaintext_option[1]) in ('PRESERVATIAN', 'VNREASONABLE'):
            #    continue
            # JBO

            # Should skip?
            if 'Y' != input(' '.join(map(runes_to_latin, plaintext_option)) + f'\t{option_index}/{total_options}\tLooks good? [Y/N]: '):
                continue
            #print(' '.join(map(runes_to_latin, plaintext_option)) + f'\t{option_index}/{total_options}')

            # Saves key options
            key_options = []

            # Get the plaintext runes and get base key indices
            plaintext_runes = ''.join(plaintext_option)
            base_key_indices = [ (RUNES.index(ciphertext_runes[i]) - RUNES.index(plaintext_runes[i])) % len(RUNES) for i in range(len(plaintext_runes)) ]
            
            # Print for now
            print('KEY: ' + indices_to_latin(base_key_indices))

def bruteforce_autokey(word_match_threashold):
    """
        Tries Autokey in all modes given a key, with and without Atbash and\or Caesar and\or totient-prime substruction.
    """

    # Get potential keys
    print('Building wordlist')
    with open('wordlist/words.txt', 'r') as fp:
        potential_keys = [ k.upper() for k in fp.read().split('\n') ]
    potential_keys = [ ''.join([ i for i in k if i.isupper() ]) for k in potential_keys ]
    potential_keys = [ k for k in potential_keys if len(k) > 0 ] 

    # Turn all potential keys to runes
    potential_keys = [ latin_to_runes(k) for k in potential_keys ]

    # Get the wordlist and extend it to also include potential keys
    wordlist = get_rune_wordlist()
    wordlist += potential_keys

    # Extend key list to include rune "F" too for each word
    potential_keys += [ k.replace(k[0], RUNES[0]) for k in potential_keys ]
    keys = list(set(potential_keys))

    # Get unresolved pages
    unsolved_pages = get_unsolved_pages()
    page_index = 0
    unsolved_pages = unsolved_pages[-3:]        # JBO
    for page in unsolved_pages:

        # Increase page index
        page_index += 1

        # Iterate keys
        key_index = 0
        for key in keys:

            # Increase key index
            key_index += 1
            print(f'Trying page {page_index} / {len(unsolved_pages)} and key {key_index} / {len(keys)}')

            # Iterate all modes
            for mode in [ AutokeyMode.PLAINTEXT, AutokeyMode.CIPHERTEXT, AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT ]:

                # Process text
                autokey_pt = ProcessedText(page)

                # Run autokey and iterate each Caesar shift
                AutokeyTransformer(key=key, mode=mode).transform(autokey_pt)
                for shift in range(len(RUNES)):

                    # Shift
                    shift_pt = ProcessedText.from_processed_text(autokey_pt)
                    ShiftTransformer(shift=shift).transform(shift_pt)
                    if shift_pt.get_first_non_wordlist_word_index(wordlist) > word_match_threashold:
                        print(f'Page {page} with shift {shift} has {shift_pt.get_first_non_wordlist_word_index(wordlist)} matches\n\n{shift_pt.to_latin()}')
                        screen.press_enter()

                    # Try Atbash
                    AtbashTransformer().transform(shift_pt)
                    if shift_pt.get_first_non_wordlist_word_index(wordlist) > word_match_threashold:
                        print(f'Page {page_index} with shift {shift} and Atbash has {shift_pt.get_first_non_wordlist_word_index(wordlist)} matches\n\n{shift_pt.to_latin()}')
                        screen.press_enter()

def bruteforce_autokey_mobius():

    # Get potential keys
    with open('wordlist/words.txt', 'r') as fp:
        potential_keys = [ k.upper() for k in fp.read().split('\n') ]
    potential_keys = [ ''.join([ i for i in k if i.isupper() ]) ]
    potential_keys = [ k for k in potential_keys if len(k) > 0 ] 

    # Turn all potential keys to runes
    potential_keys = [ latin_to_runes(k) for k in potential_keys ]

    # Get the wordlist and extend it to also include potential keys
    wordlist = get_rune_wordlist()
    wordlist += potential_keys

    # Extend key list to include rune "F" too for each word
    potential_keys += [ k.replace(k[0], RUNES[0]) for k in potential_keys ]

    # Get unresolved pages
    unsolved_pages = get_unsolved_pages()

    # Threshold
    word_match_threshold = 3

    # Iterate pages
    page_index = 0
    for page in unsolved_pages:

        # Store results
        results = []

        # Iterate keys
        page_index += 1
        key_index = 0
        for keys in itertools.permutations(potential_keys, 3):

            # Print stats
            key_index += 1
            print(f'Page {page_index} / {len(unsolved_pages)} ; Key {key_index} / {len(potential_keys) * (len(potential_keys) - 1) * (len(potential_keys) - 2)}')

            # Build transformer options
            for mode in [ AutokeyMode.PLAINTEXT, AutokeyMode.CIPHERTEXT, AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT ]:
  
                # Build transformers
                transformers = []
                transformers.append( [ AutokeyMobiusTransformer(keys=keys, mode=mode) ])
                transformers.append(TotientPrimeTransformer(add=True))
                tranaformers.append(TotientPrimeTransformer(add=False))
                transformers.append(AtbashTransformer())
                
                # Just autokey
                pt = ProcessedText(page)
                autokey_transformer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
                atbash_transformer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
 
                # Autokey with tot-prime add
                pt = ProcessedText(page)
                autokey_transformer.transform(pt)
                tot_prime_add_transofmer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
                atbash_transformer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
 
                # Autokey with tot-prime sub
                pt = ProcessedText(page)
                autokey_transformer.transform(pt)
                tot_prime_sub_transofmer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
                atbash_transformer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
 
                # Tot-prime add with Autokey
                pt = ProcessedText(page)
                tot_prime_add_transofmer.transform(pt)
                autokey_transformer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
                atbash_transformer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
 
                # Tot-prime sub with Autokey
                pt = ProcessedText(page)
                tot_prime_sub_transofmer.transform(pt)
                autokey_transformer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
                atbash_transformer.transform(pt)
                word_matches = pt.get_first_non_wordlist_word_index(wordlist)
                if word_matches >= word_match_threshold:
                    results.append((word_matches, pt.to_latin()))
 
        # Sort all results
        results.sort()
        with open(f'dbg_{page_index}.txt', 'w') as fp:
            for r in results:
                fp.write(f'word matches: {r[0]}\n{r[1]}\n\n=================\n\n')

class Attempts(object):
    """
        Attempts made.
    """

    @staticmethod
    def show_all_pages():
        """
            Presents all pages.
        """

        # Decrypt all pages
        page_index = 1
        for page in PAGES:

            # Build the processed text
            processed_text = ProcessedText(page[0])

            # Get the rune IoC
            rune_ioc = processed_text.get_rune_ioc()

            # Decrypt
            page[1].transform(processed_text)

            # Present and wait for input
            print(f'Page: {page_index}\nRunic IoC (pre): {rune_ioc}\nRunic IoC (post): {processed_text.get_rune_ioc()}\nLatin IoC: {processed_text.get_latin_ioc()}\n\n')
            screen.print_solved_text(f'{processed_text.to_latin()}\n\n{page[0]}\n\n\n')
            screen.press_enter()
            page_index += 1

    def show_all_solved_words():
        """
            Presents all solved words.
        """

        # Get words and show them
        words = get_rune_wordlist()
        sep_len = 4 + max([ len(word) for word in words ])
        word_index = 0
        for word in words:
            word_index += 1
            line = f'[{word_index} / {len(words)}]: word'
            line += ' ' * (sep_len - len(line))
            line += runes_to_latin(word)
            line += ' ' * (sep_len * 2 - len(line))
            line += str(len(word))
            screen.print_solved_text(line)
            screen.press_enter()

    @staticmethod
    def show_unsolved_pages_potential_cribs_lengths():
        """
            Shows each unsolved page with potential crib lengths at the beginning of the page.
        """

        # Iterate all unsolved pages
        page_index = -1
        for page in get_unsolved_pages():

            # Get all words until a period
            page_index += 1
            header_words = ProcessedText(page.split('.')[0]).get_rune_words()
            if len(header_words) == 0:
                continue
            header_words_lengths = [ len(w) for w in header_words ]
            print(f'Page: {page_index}\n\n')
            screen.print_solved_text(f'{page}\n\n{header_words_lengths}')
            screen.press_enter()

    @staticmethod
    def double_tot_index_with_reversing(word_threshold=6, ioc_threshold=1.8):
        """
            Adds or substructs either tot(primes) or tot(tot(primes)), on both normal text as well as reversed text.
            If the number of prefixed words are above the given threshold or the IOC is above the given threshold, print result.
        """

        # Get an extended wordlist for a measurement
        wordlist = get_rune_wordlist(True)

        # Iterate all pages
        page_index = -1
        for page in tqdm(get_unsolved_pages(), desc='Pages being analyzed'):

            # Increase page index
            page_index += 1

            # Iterate all number of totient operations
            for tot_call_count in range(1, 3):
               
                # Try adding or substructing
                for add_option in (False, True):

                    # Try reversing and then run totient index manipulation
                    pt = ProcessedText(page)
                    ReverseTransformer().transform(pt)
                    TotientPrimeTransformer(tot_calls=tot_call_count, add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

                    # Try without reversing
                    pt = ProcessedText(page)
                    TotientPrimeTransformer(tot_calls=tot_call_count, add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

                    # Reverse after totient index manipulation
                    ReverseTransformer().transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

    @staticmethod
    def use_2013_missing_primes(word_threshold=6, ioc_threshold=1.8):
        """
            Attempts to use the Cicada 3301 message missing primes from 2013 as a keystream.
        """

        # Get an extended wordlist for a measurement
        wordlist = get_rune_wordlist(True)

        # Iterate all pages
        page_index = -1
        for page in tqdm(get_unsolved_pages()):

            # Increase page index
            page_index += 1

            # Whether to add or substruct
            for add in (False, True):

                # Try decryption
                pt = ProcessedText(page)
                KeystreamTransformer(add=add, keystream=iter(secrets.MISSING_PRIMES_2013)).transform(pt)
                if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                    print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

    @staticmethod
    def autokey_and_vigenere_bruteforce_with_reversing(word_threshold=6, ioc_threshold=1.8, min_key_len=6):
        """
            Attempts Autokey or Vigenere bruteforcing with or without reversing the text of each page.
            Uses keys derived from all decrypted pages, with and without replacing all occurrences of first character with "F".
            Also tries reversing all keys.
            Uses all supported modes of Autokey: plaintext, cipehrtext or alternating (starting from either plaintext or ciphertext, or using the Mobius function).
        """

        # Get an extended wordlist for a measurement
        wordlist = get_rune_wordlist(True)

        # Build potential keys
        keys = get_rune_wordlist()
        rev_keys = [ k[::-1] for k in keys ]
        keys += [ k.replace(k[0], RUNES[0]) for k in keys ]
        keys += rev_keys
        keys = [ k for k in keys if len(k) > min_key_len ]
        keys = set(keys)

        # Iterate all pages
        page_index = -1
        for page in get_unsolved_pages():

            # Increase page index
            page_index += 1

            # Iterate all keys
            for key in tqdm(keys, desc=f'Page {page_index}'):
              
                # Attempt Vigenere
                pt = ProcessedText(page)
                VigenereTransformer(key=key).transform(pt)
                if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                    print(f'PAGE {page_index} (Vigenere Key={key}, IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n')
                    screen.print_solved_text(f'{pt.to_latin()}\n\n{page}\n\n\n')

                # Iterate all modes
                for mode in (AutokeyMode.PLAINTEXT, AutokeyMode.CIPHERTEXT, AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT, AutokeyMode.ALT_MOBIUS_START_PLAINTEXT, AutokeyMode.ALT_MOBIUS_START_CIPHERTEXT):

                    # Either try or do not try GP-mode
                    for use_gp in (False, True):

                        # Apply Autokey
                        pt = ProcessedText(page)
                        AutokeyTransformer(key=key, mode=mode, use_gp=use_gp).transform(pt)
                        if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                            print(f'PAGE {page_index} (Autokey Key={key}, mode={mode}, IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n')
                            screen.print_solved_text(f'{pt.to_latin()}\n\n{page}\n\n\n')

                        # Reverse
                        ReverseTransformer().transform(pt)
                        if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                            print(f'PAGE {page_index} (Autokey Key={key}, mode={mode}, reversed, IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n')
                            screen.print_solved_text(f'{pt.to_latin()}\n\n{page}\n\n\n')

                        # Start from reversing and then apply Autokey
                        pt = ProcessedText(page)
                        ReverseTransformer().transform(pt)
                        AutokeyTransformer(key=key, mode=mode, use_gp=use_gp).transform(pt)
                        if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                            print(f'PAGE {page_index} (Reversed text Autokey Key={key}, mode={mode}, IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n')
                            screen.print_solved_text(f'{pt.to_latin()}\n\n{page}\n\n\n')
    @staticmethod
    def oeis_keystream(word_threshold=6, ioc_threshold=1.8):
        """
            Tries all OEIS sequences on each page, using them as keystreams.
        """

        # Get an extended wordlist for a measurement
        wordlist = get_rune_wordlist(True)

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
            
            # Iterate all pages
            page_index = -1
            for page in get_unsolved_pages():

                # Increase page index
                page_index += 1

                # Try adding or substructing
                for add_option in (False, True):

                    # Try sequence as-is
                    pt = ProcessedText(page)
                    KeystreamTransformer(keystream=iter(sequences[seq]), add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'PAGE {page_index} (Seq={seq}, IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

                    # Try a special function on the sequence which comes from the Cicada page 15 spiral
                    pt = ProcessedText(page)
                    func_seq = [ abs(3301 - elem) for elem in sequences[seq] ]
                    KeystreamTransformer(keystream=iter(func_seq), add=add_option).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'PAGE {page_index} (Seq={seq} with 1033 function, IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

    @staticmethod
    def page15_function_keystream():
        """
            Uses abs(3301-p) on all primes p as a keystream, as well as Fibonacci-indexed primes.
            This function was concluded from the Page 15 square matrix.
        """

        # Iterate all pages
        page_index = -1
        for page in get_unsolved_pages():

            # Increase page index
            page_index += 1

            # Try adding or substructing
            for add_option in (False, True):

                # Try on primes 
                pt = ProcessedText(page)
                Page15FuncPrimesTransformer(add=add_option).transform(pt)
                print(f'PAGE {page_index} Func15(primes) (IOC={pt.get_rune_ioc()}):\n\n')
                screen.print_solved_text(f'{pt.to_latin()}\n\n{page}\n\n\n')
                screen.press_enter()

                # Try on Fibonacci-indexed primes
                pt = ProcessedText(page)
                Page15FiboPrimesTransformer(add=add_option).transform(pt)
                print(f'PAGE {page_index} Func15(fibo-primes) (IOC={pt.get_rune_ioc()}):\n\n')
                screen.print_solved_text(f'{pt.to_latin()}\n\n{page}\n\n\n')
                screen.press_enter()

                # Try on Fibonacci-indexed primes without the page 15 function
                pt = ProcessedText(page)
                FiboPrimesTransformer(add=add_option).transform(pt)
                print(f'PAGE {page_index} (fibo-primes) (IOC={pt.get_rune_ioc()}):\n\n')
                screen.print_solved_text(f'{pt.to_latin()}\n\n{page}\n\n\n')
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
            screen.press_enter()
            continue
        except Exception as ex:
            last_error = f'ERROR: {ex}'

if __name__ == '__main__':
    research_menu()
