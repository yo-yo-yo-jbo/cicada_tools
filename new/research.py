#!/usr/bin/env python3
from pages import PAGES
from core import RUNES
from core import LATIN
from core import ProcessedText
from transformers import *
import os
import itertools
import sys

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

def get_rune_wordlist():
    """
        Get a Runic wordlist from all solved pages dynamically.
    """

    # Try to decrypt all pages
    result = set()
    for page in PAGES:

        # Process all text
        processed_text = ProcessedText(page[0])
        for transformer in page[1]:
            transformer.transform(processed_text)

        # Skip unsolved pages
        if processed_text.is_unsolved():
            continue

        # Get all words
        for word in processed_text.get_rune_words():
            if len(word) == 0:
                continue
            result.add(word)

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

def bruteforce_autokey():

    # Get the wordlist
    wordlist = get_rune_wordlist()
    potential_keys = [ 'ᚳᚩᚾᛋᚢᛗᛈᛏᛡᚾ', 'ᛈᚱᛖᛋᛖᚱᚢᚪᛏᛡᚾ', 'ᚪᛞᚻᛖᚱᛖᚾᚳᛖ' ]

    # Extend key list to include rune "F" too for each word
    potential_keys += [ k.replace(k[0], RUNES[0]) for k in potential_keys ]

    # Get unresolved pages
    unsolved_pages = get_unsolved_pages()

    # Threshold
    word_match_threshold = 1

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
            transformers = []
            for mode in [ AutokeyMode.PLAINTEXT, AutokeyMode.CIPHERTEXT, AutokeyMode.ALT_START_PLAINTEXT, AutokeyMode.ALT_START_CIPHERTEXT ]:
   
                # Build transformers
                transformers = []
                transformers.append( [ AutokeyMobiusTransformer(keys=keys, mode=mode) ])
                transformers.append(TotientPrimeTransformer(add=True))
                tranaformers.append(TotientPrimeTransformer(add=False))
                transformers.append(AtbashTransformer())
                shift_by_one_transformer = ShiftTransformer(shift = 1)



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

if __name__ == '__main__':
    #show_unsolved_pages_potential_cribs()
    #show_all_solved_words()
    #auto_crib_get_keys()
    bruteforce_autokey()

