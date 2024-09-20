#!/usr/bin/env python3
from pages import PAGES
from core import RUNES
from core import LATIN
from core import ProcessedText
from core import latin_to_runes
from transformers import *
import os
import itertools
import sys
from tqdm import tqdm

def press_enter():
    """
        Waits for an ENTER keypress.
    """

    # Get input and clear the screen
    _ = input()
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

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
        print(f'Page: {page_index}\nRunic IoC (pre): {rune_ioc}\nRunic IoC (post): {processed_text.get_rune_ioc()}\nLatin IoC: {processed_text.get_latin_ioc()}\n\n{processed_text.to_latin()}\n\n{page[0]}\n\n\n')
        press_enter()
        page_index += 1

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

def show_all_solved_words():
    """
        Presents all solved words.
    """

    # Get words and show them
    words = get_rune_wordlist()
    sep_len = 4 + max([ len(word) for word in words ])
    for word in words:
        line = word
        line += ' ' * (sep_len - len(line))
        line += runes_to_latin(word)
        line += ' ' * (sep_len * 2 - len(line))
        line += str(len(word))
        print(line)

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

def show_unsolved_pages_potential_cribs():
    """
        Shows each unsolved page with potential cribs at the beginning of the page.
    """

    # Iterate all unsolved pages
    for page in get_unsolved_pages():

        # Get all words until a period
        header_words = ProcessedText(page.split('.')[0]).get_rune_words()
        if len(header_words) == 0:
            continue
        header_words_lengths = [ len(w) for w in header_words ]
        print(f'{page}\n\n{header_words_lengths}')
        #press_enter()

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
                        press_enter()

                    # Try Atbash
                    AtbashTransformer().transform(shift_pt)
                    if shift_pt.get_first_non_wordlist_word_index(wordlist) > word_match_threashold:
                        print(f'Page {page_index} with shift {shift} and Atbash has {shift_pt.get_first_non_wordlist_word_index(wordlist)} matches\n\n{shift_pt.to_latin()}')
                        press_enter()

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
    def double_tot_index_with_reversing(word_threshold=4, ioc_threshold=1.4):
        """
            Adds or substructs either tot(primes) or tot(tot(primes)), on both normal text as well as reversed text.
            If the number of prefixed words are above the given threshold or the IOC is above the given threshold, print result.
        """

        # Get an extended wordlist for a measurement
        wordlist = get_rune_wordlist(True)

        # Iterate all pages
        page_index = -1
        for page in get_unsolved_pages():

            # Increase page index
            page_index += 1

            # Iterate all number of totient operations
            for tot_call_count in range(1, 3):
                
                # Try reversing and then run totient index manipulation
                pt = ProcessedText(page)
                ReverseTransformer().transform(pt)
                TotientPrimeTransformer(tot_calls=tot_call_count).transform(pt)
                if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                    print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

                # Try without reversing
                pt = ProcessedText(page)
                TotientPrimeTransformer(tot_calls=tot_call_count).transform(pt)
                if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                    print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

                # Reverse after totient index manipulation
                ReverseTransformer().transform(pt)
                if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                    print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

    @staticmethod
    def autokey_bruteforce_with_reversing(word_threshold=4, ioc_threshold=1.4):
        """
            Attempts Autokey bruteforcing with or without reversing the text of each page.
            Uses keys derived from all decrypted pages, with and without replacing all occurrences of first character with "F".
            Uses all supported modes of Autokey: plaintext, cipehrtext or alternating (starting from either plaintext or ciphertext, or using the Mobius function).
        """

        # Get an extended wordlist for a measurement
        wordlist = get_rune_wordlist(True)

        # Build potential keys
        keys = get_rune_wordlist()
        keys += [ k.replace(k[0], RUNES[0]) for k in keys ]
        keys = set(keys)

        # Iterate all pages
        page_index = -1
        for page in get_unsolved_pages():

            # Increase page index
            page_index += 1

            # Iterate all keys
            for key in tqdm(keys, desc=f'Page {page_index}'):
               
                # Iterate all modes
                for mode in (AutokeyMode.PLAINTEXT, AutokeyMode.CIPHERTEXT, AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT, AutokeyMode.ALT_MOBIUS_START_PLAINTEXT, AutokeyMode.ALT_MOBIUS_START_CIPHERTEXT):

                    # Apply Autokey
                    pt = ProcessedText(page)
                    AutokeyTransformer(key=key, mode=mode).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

                    # Reverse
                    ReverseTransformer().transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

                    # Start from reversing and then apply Autokey
                    pt = ProcessedText(page)
                    ReverseTransformer().transform(pt)
                    AutokeyTransformer(key=key, mode=mode).transform(pt)
                    if pt.get_first_non_wordlist_word_index(wordlist) >= word_threshold or pt.get_rune_ioc() >= ioc_threshold:
                        print(f'PAGE {page_index} (IOC={pt.get_rune_ioc()}, WordMatchers={pt.get_first_non_wordlist_word_index(wordlist)}):\n{pt.to_latin()}\n\n')

if __name__ == '__main__':
    Attempts.autokey_bruteforce_with_reversing()
